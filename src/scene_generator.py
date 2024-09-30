import json
from copy import deepcopy
from math import inf
from typing import Dict, Any, List, Optional, Tuple
import logging

from tqdm import tqdm

from prompts.scene import GENERATE_SCENE, EVALUATE_SCENE, REFINE_SCENE, EXTRACT_STORY_ELEMENTS, EVALUATE_FULL_SCRIPT
from src.llm.LLMService import LLMService
from src.utils.JSONValidator import JSONValidator
from src.utils.file_handlers import load_txt, save_json, save_txt

logger = logging.getLogger(__name__)


def generate_scene_with_validation(llm_service: LLMService, prompt: str, max_attempts: int = 3) -> Optional[
    Dict[str, Any]]:
    for attempt in range(max_attempts):
        scene_json = llm_service.generate(prompt, format="json")
        validated_scene = JSONValidator.validate_scene_json(scene_json)

        if validated_scene:
            return validated_scene
        else:
            print(f"Attempt {attempt + 1} failed. Retrying...")

    print(f"Failed to generate valid JSON after {max_attempts} attempts.")
    return None


def _parse_json_to_markdown(scene_json: Dict[str, Any], current_act: int = None) -> Tuple[str, int]:
    markdown = ""

    # Extract act number from scene number (assuming format "1.2.3" where 1 is the act number)
    try:
        scene_act = int(scene_json['scene_number'].split('.')[0])
    except Exception as e:
        try:
            scene_act = int(scene_json['scene_number'].split(' ')[1][0])
        except Exception as e:
            scene_act = -1

    # If this is a new act, add the act header
    if scene_act != current_act:
        markdown += f"# ACT {scene_act}\n\n---\n\n"
        current_act = scene_act

    markdown += f"## Scene {scene_json['scene_number']}: {scene_json['location']} - {scene_json['time']}\n\n"

    for item in scene_json['content']:
        if item['type'] == 'action':
            markdown += f"{item['text']}\n\n"
        elif item['type'] == 'dialog':
            markdown += f"{item['character'].upper()}\n{item['text']}\n\n"
        elif item['type'] == 'transition':
            markdown += f"{item['text'].upper()}\n\n"

    return markdown, current_act

def _truncate_story(story: Dict[str, Any], sub_scene: Dict[str, Any]) -> Dict[str, Any]:
    """
    Truncates the story to only include all subscenes for the current subscene,
    all other subscenes in the story are removed.
    """
    truncated_story = deepcopy(story)
    for act in truncated_story['acts']:
        for scene in act['scenes']:
            sub_scene_numbers = [sub_scene['sub_scene_number'] for sub_scene in scene['sub_scenes']]
            if sub_scene['sub_scene_number'] not in sub_scene_numbers:
                # delete key sub_scenes from scene
                scene.pop('sub_scenes', None)


    return truncated_story

def _save_scene_output(scene_content: Dict[str, Any], scene_markdown: str, scene_number: str):
    save_json(f'output/scenes/scene_{scene_number}.json', scene_content)
    save_txt(f'output/scenes/scene_{scene_number}.md', scene_markdown)


class SceneGenerator:
    def __init__(self, llm_service: LLMService, llm_service_validation: LLMService, config: Dict[str, Any], characters: Dict[str, Any],
                 themes: Dict[str, Any]):
        self.llm_service = llm_service
        self.llm_service_validation = llm_service_validation
        self.config = config
        self.characters = characters
        self.themes = themes
        self.style_guide = load_txt("data/style_guide.md")
        self.good_scene_threshold = config.get('good_scene_threshold', 80)
        self.max_iterations = config.get('max_scene_iterations', 5)
        self.full_script_threshold = config.get('full_script_threshold', 85)

    def generate_scenes(self, story: Dict[str, Any], start_with_scene="2.2.8") -> List[Dict[str, Any]]:
        generated_scenes = []
        full_script_markdown = ""
        current_act = None

        total_sub_scenes = sum([len(scene.get('sub_scenes', [])) for act in story['acts'] for scene in act['scenes']])
        with tqdm(total=total_sub_scenes, desc="Generating scenes", unit="sub-scene") as pbar:
            for act in story['acts']:
                for scene in act['scenes']:
                    for sub_scene in scene.get('sub_scenes', []):
                        scene_content = self._generate_single_scene(sub_scene, story, full_script_markdown)
                        generated_scenes.append(scene_content)

                        scene_markdown, current_act = _parse_json_to_markdown(scene_content['content'],
                                                                                   current_act)
                        full_script_markdown += "\n" + scene_markdown

                        _save_scene_output(scene_content, scene_markdown, sub_scene['sub_scene_number'])

                        pbar.update(1)

        # Save initial full script
        save_txt('output/full_script_initial.md', full_script_markdown)
        save_json('output/scenes_initial.json', generated_scenes)

        # Evaluate and refine full script
        evaluation = self._evaluate_full_script(full_script_markdown, story)
        refined_scenes = self._refine_full_script(generated_scenes, evaluation, story)

        # Save refined full script
        refined_full_script_markdown = "\n".join(
            [_parse_json_to_markdown(scene['content']) for scene in refined_scenes])
        save_txt('output/full_script_refined.md', refined_full_script_markdown)
        save_json('output/scenes_refined.json', refined_scenes)

        return refined_scenes

    def _generate_single_scene(self, sub_scene: Dict[str, Any], story: Dict[str, Any],
                               full_script_markdown: str) -> Dict[str, Any]:
        best_scene = None
        best_score = 0

        story_truncated = _truncate_story(story, sub_scene)

        scene_content = self._generate_scene(sub_scene, story_truncated, full_script_markdown)
        for attempt in range(self.max_iterations):
            if scene_content is None:
                continue  # Skip evaluation if generation failed

            evaluation = self._evaluate_scene(scene_content, sub_scene, story_truncated)
            try:
                total_score = evaluation.get('total_score', 0)
            except AttributeError:
                total_score = 0

            if total_score > best_score:
                best_scene = scene_content
                best_score = total_score

            if total_score >= self.good_scene_threshold:
                logger.info(f"Scene {sub_scene['sub_scene_number']} generated successfully with score {total_score}")
                return {'scene_number': sub_scene['sub_scene_number'], 'content': scene_content,
                        'evaluation': evaluation}

            feedback = ""
            try:
                logger.info(f"Scene {sub_scene['sub_scene_number']} generated with score {total_score}. Refining... (try {attempt+1} of {self.max_iterations})"
                        f"\n\tFeedback: {evaluation['feedback']}")
                feedback = evaluation['feedback']
            except TypeError as e:
                logger.info(f"Scene {sub_scene['sub_scene_number']} generated with score {total_score}. Refining... (try {attempt+1} of {self.max_iterations})"
                            f"\n\tFeedback: {evaluation}")
                feedback = evaluation


            if attempt < self.max_iterations - 1:  # Don't refine on the last iteration
                scene_content = self._refine_scene(scene_content, feedback, sub_scene, story_truncated,
                                                   full_script_markdown)

        logger.info(f"Scene {sub_scene['sub_scene_number']} could not be refined further. Using the best attempt (score: {best_score})")
        return {'scene_number': sub_scene['sub_scene_number'], 'content': best_scene, 'score': best_score}

    def _generate_scene(self, sub_scene: Dict[str, Any], story: Dict[str, Any],
                        full_script_markdown: str) -> Optional[Dict[str, Any]]:
        context_length = self.config.get('context_length', inf)
        context = full_script_markdown[-context_length:] if len(
            full_script_markdown) > context_length else full_script_markdown
        context_length = len(context)

        prompt = GENERATE_SCENE.format(
            # characters=self.characters,
            # themes=self.themes,
            outline=story,
            current_scene=sub_scene,
            full_script_context=context,
            context_length=context_length,
            genre=self.config.get('genre', 'unknown'),
            title=story.get('title', 'Untitled')
        )

        return generate_scene_with_validation(self.llm_service, prompt)

    def _evaluate_scene(self, scene_content: Dict[str, Any], sub_scene: Dict[str, Any],
                        story: Dict[str, Any]) -> Dict[str, Any]:
        scene_markdown = _parse_json_to_markdown(scene_content)
        prompt = EVALUATE_SCENE.format(
            outline=story,
            scene_content=scene_markdown,
            scene_details=sub_scene,
            characters=self.characters,
            themes=self.themes,
            genre=self.config.get('genre', 'movie'),
        )
        return self.llm_service_validation.generate(prompt, format="json")

    def _refine_scene(self, scene_content: Dict[str, Any], feedback: str, sub_scene: Dict[str, Any],
                      story: Dict[str, Any], full_script_markdown: str) -> Optional[Dict[str, Any]]:
        context_length = self.config.get('context_length', inf)
        context = full_script_markdown[-context_length:] if len(
            full_script_markdown) > context_length else full_script_markdown

        prompt = REFINE_SCENE.format(
            scene_content=json.dumps(scene_content),
            feedback=feedback,
            scene_details=sub_scene,
            characters=self.characters,
            themes=self.themes,
            genre=self.config.get('genre', 'movie'),
            full_script_context=context,
            context_length=context_length,
        )
        return generate_scene_with_validation(self.llm_service, prompt)

    def _evaluate_full_script(self, full_script_markdown: str, story: Dict[str, Any]) -> Dict[str, Any]:
        prompt = EVALUATE_FULL_SCRIPT.format(
            full_script=full_script_markdown,
            outline=json.dumps(story),
            characters=json.dumps(self.characters),
            themes=json.dumps(self.themes),
            genre=self.config.get('genre', 'unknown')
        )
        evaluation = self.llm_service.generate(prompt, format="json")
        save_json('output/full_script_evaluation.json', evaluation)
        return evaluation

    def _refine_full_script(self, scenes: List[Dict[str, Any]], evaluation: Dict[str, Any], story: Dict[str, Any]) -> \
    List[Dict[str, Any]]:
        refined_scenes = scenes.copy()
        total_score = evaluation.get('total_score', 0)

        if total_score >= self.full_script_threshold:
            return refined_scenes

        scenes_to_improve = evaluation.get('scenes_to_improve', [])
        for scene_info in scenes_to_improve:
            scene_id = scene_info['scene_id']
            scene_index = next((i for i, scene in enumerate(refined_scenes) if scene['scene_number'] == scene_id), None)

            if scene_index is not None:
                refined_scene = self._refine_scene(refined_scenes[scene_index]['content'], scene_info['suggestions'],
                                                   story, "\n".join(
                        [_parse_json_to_markdown(s['content']) for s in refined_scenes]))
                refined_scenes[scene_index]['content'] = refined_scene

        return refined_scenes
