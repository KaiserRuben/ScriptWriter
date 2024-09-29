from typing import Dict, Any, List
import logging

from tqdm import tqdm

from prompts.scene import GENERATE_SCENE, EVALUATE_SCENE, REFINE_SCENE, EXTRACT_STORY_ELEMENTS
from src.llm.LLMService import LLMService
from src.utils.file_handlers import load_txt, save_json, save_txt
from src.utils.sort_and_compare import compare_scene_numbers

logger = logging.getLogger(__name__)


class SceneGenerator:
    def __init__(self, llm_service: LLMService, config: Dict[str, Any], characters: Dict[str, Any],
                 themes: Dict[str, Any]):
        self.llm_service = llm_service
        self.config = config
        self.characters = characters
        self.themes = themes
        self.style_guide = load_txt("data/style_guide.md")
        self.good_scene_threshold = config.get('good_scene_threshold', 80)  # Default to 80 out of 100
        self.max_iterations = config.get('max_scene_iterations', 5)
        self.story_elements = []  # New: Store extracted story elements

    def generate_scenes(self, story: Dict[str, Any]) -> List[Dict[str, Any]]:
        generated_scenes = []
        generated_scenes_str = ""
        previous_scene = None
        current_act_elements = []

        total_sub_scenes = sum([len(scene.get('sub_scenes', [])) for act in story['acts'] for scene in act['scenes']])
        with tqdm(total=total_sub_scenes, desc="Generating scenes", unit="sub-scene") as pbar:
            for act in story['acts']:
                act_elements = []
                for scene in act['scenes']:
                    for sub_scene in scene.get('sub_scenes', []):
                        sub_scene_content = self._generate_single_scene(sub_scene, story, previous_scene,
                                                                        self.story_elements + current_act_elements)
                        generated_scenes.append(sub_scene_content)
                        generated_scenes_str += "\n" + sub_scene_content['content']

                        # Extract story elements from the generated scene
                        new_elements = self._extract_story_elements(sub_scene_content['content'],
                                                                    sub_scene['sub_scene_number'],
                                                                    story)

                        # Update story elements
                        for item in new_elements['story_elements']:
                            if item['scope'] == 'global':
                                self.story_elements.append(item)
                            elif item['scope'] == 'act':
                                act_elements.append(item)
                            # 'scene' scope items are not stored for future use

                        current_act_elements = [item for item in current_act_elements if int(item['scene_number'][0]) == act['act_number']]

                        save_json(f'output/sub_scenes/sub_scene_{sub_scene["sub_scene_number"]}.json',
                                  sub_scene_content)
                        save_txt(f'output/sub_scenes/up_to_scene/{sub_scene["sub_scene_number"]}.md',
                                 generated_scenes_str)

                        previous_scene = sub_scene_content['content']

                        pbar.update(1)

                # At the end of each act, update the current act elements
                current_act_elements = act_elements

        return generated_scenes

    def _generate_single_scene(self, sub_scene: Dict[str, Any], story: Dict[str, Any],
                               previous_scene: str, current_elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        best_scene = None
        best_score = 0
        evaluation = {
            'feedback': "",
            'total_score': 0
        }
        feedback = ""
        scene_content = ""

        for attempt in range(self.max_iterations):
            if attempt == 0:
                # Initial generation
                scene_content = self._generate_scene(sub_scene, story, previous_scene, current_elements)
            else:
                # Refine based on previous feedback
                scene_content = self._refine_scene(scene_content, feedback, sub_scene, story,
                                                   previous_scene)

            evaluation = self._evaluate_scene(scene_content, sub_scene, story)

            # check all keys and types of evaluation
            if (not type(evaluation) == dict) or (not 'total_score' in evaluation.keys()) or (
            not type(evaluation['total_score']) == int):
                logger.error(f"Failed to evaluate scene. Evaluation: {evaluation}")
                total_score = -1
            else:
                total_score = evaluation['total_score']

            if (not type(evaluation) == dict) or (not 'feedback' in evaluation.keys()) or (
            not type(evaluation['feedback']) == str):
                logger.error(f"Failed to evaluate scene. Evaluation: {evaluation}")
                feedback = ""
            else:
                feedback = evaluation['feedback']

            if total_score > best_score:
                best_scene = scene_content
                best_score = total_score

            if total_score >= self.good_scene_threshold:
                logger.info(
                    f"Generated a satisfactory sub-scene after {attempt + 1} attempts with score {total_score}.")
                return {'scene_number': sub_scene['sub_scene_number'], 'content': scene_content,
                        'evaluation': evaluation}

            logger.info(f"Attempt {attempt + 1} failed with score {total_score}. Feedback: {feedback}")

        logging.warning(
            f"Failed to generate a satisfactory sub-scene after {self.max_iterations} attempts. Using the best generated scene.")
        return {'scene_number': sub_scene['sub_scene_number'], 'content': best_scene, 'score': best_score}

    def _generate_scene(self, sub_scene: Dict[str, Any], story: Dict[str, Any],
                        previous_scene: str, current_elements: List[Dict[str, Any]]) -> str:
        prompt = GENERATE_SCENE.format(
            characters=self.characters,
            themes=self.themes,
            outline=story,
            current_scene=sub_scene,
            previous_scene=previous_scene,  # Use the actual previous scene content
            genre=self.config.get('genre', 'unknown'),
            title=story.get('title', 'Untitled'),
            story_elements=current_elements
        )
        if previous_scene is None:
            prompt += '\nStylistic Guide:\n' + self.style_guide

        return self.llm_service.generate(prompt)

    def _evaluate_scene(self, scene_content: str, sub_scene: Dict[str, Any],
                        story: Dict[str, Any]) -> Dict[str, Any]:
        prompt = EVALUATE_SCENE.format(
            outline=story,
            scene_content=scene_content,
            scene_details=sub_scene,
            characters=self.characters,
            themes=self.themes,
            genre=self.config.get('genre', 'movie'),
        )
        return self.llm_service.generate(prompt, format="json")

    def _extract_story_elements(self, scene_content: str, scene_number: str, outline) -> Dict[str, Any]:
        prompt = EXTRACT_STORY_ELEMENTS.format(
            scene_content=scene_content,
            scene_number=scene_number,
            outline=outline
        )

        extracted_elements = self.llm_service.generate(prompt, format="json")
        return extracted_elements

    def _refine_scene(self, scene_content: str, feedback: str, sub_scene: Dict[str, Any],
                      story: Dict[str, Any], previous_scene: str) -> str:
        prompt = REFINE_SCENE.format(
            scene_content=scene_content,
            feedback=feedback,
            scene_details=sub_scene,
            characters=self.characters,
            themes=self.themes,
            genre=self.config.get('genre', 'movie'),
            style_guide=self.style_guide,
            previous_scene=previous_scene
        )
        return self.llm_service.generate(prompt)
