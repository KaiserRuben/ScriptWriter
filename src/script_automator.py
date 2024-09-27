import logging

from replicate.exceptions import ModelError
from tqdm import tqdm
import json

from prompts.outline import GENERATE_ACTS, VALIDATE_ACTS, GENERATE_KEY_SCENES, VALIDATE_KEY_SCENES, GENERATE_SUB_SCENES, \
    VALIDATE_SUB_SCENES, REVIEW_OUTLINE, VALIDATE_FINAL_OUTLINE
from src.llm.LLMService import LLMService
from src.utils.file_handlers import load_json, save_json, load_txt, save_txt


class ScriptAutomator:
    def __init__(self, initial_script=None):
        self.config = load_json('config/settings.json')
        self.llm_service = LLMService(provider_name=self.config.get('llm_provider', 'ollama'), default_model=self.config.get('llm_model', 'gemma2:27b'))
        self.max_iterations = self.config.get('max_scene_iterations', 5)
        self.good_scene_threshold = self.config.get('good_scene_threshold', 0.8)
        self.initial_script = initial_script

    def run(self):
        concept = load_txt('data/concept.txt')
        outline = self.generate_outline(concept)
        characters = self.develop_characters(concept, outline)
        themes = self.identify_themes(concept, outline)
        script = self.write_scenes(outline, characters, themes)
        analysis = self.review_script(script, outline, characters, themes)

        save_txt('output/full_script.txt', script)
        save_json('output/script_analysis.json', analysis)
        logging.info("Script generation complete. Check the 'output' folder for results.")

    def generate_outline(self, concept):
        logging.info("Generating outline")
        acts = self._generate_and_validate(GENERATE_ACTS, VALIDATE_ACTS, concept=concept)

        scenes = []
        for act in tqdm(acts['acts'], desc="Generating scenes", unit="act"):
            act_scenes = self._generate_and_validate(GENERATE_KEY_SCENES, VALIDATE_KEY_SCENES,
                                                     concept=concept, act=act, full_acts=acts)
            scenes.extend(act_scenes['scenes'])

        detailed_scenes = []
        for i, scene in enumerate(tqdm(scenes, desc="Generating sub-scenes", unit="scene")):
            previous_scene = scenes[i - 1] if i > 0 else None
            sub_scenes = self._generate_and_validate(GENERATE_SUB_SCENES, VALIDATE_SUB_SCENES,
                                                     concept=concept, scene=scene, previous_scene=previous_scene,
                                                     full_scenes=scenes)
            detailed_scenes.extend(sub_scenes['sub_scenes'])

        outline = {'acts': acts['acts'], 'scenes': detailed_scenes}
        final_outline = self._generate_and_validate(REVIEW_OUTLINE, VALIDATE_FINAL_OUTLINE,
                                                    concept=concept, outline=outline)

        # move acts and scenes from outline to final_outline if they don't exist
        def merge_outlines(final_outline, outline):
            # Merge acts
            if 'acts' not in final_outline:
                final_outline['acts'] = outline['acts']
            else:
                act_dict = {act['act_number']: act for act in final_outline['acts']}
                for new_act in outline['acts']:
                    act_dict[new_act['act_number']] = new_act
                final_outline['acts'] = list(act_dict.values())

            # Merge scenes
            if 'scenes' not in final_outline:
                final_outline['scenes'] = outline['scenes']
            else:
                scene_dict = {scene['scene_number']: scene for scene in final_outline['scenes']}
                for new_scene in outline['scenes']:
                    scene_dict[new_scene['scene_number']] = new_scene
                final_outline['scenes'] = list(scene_dict.values())

            return final_outline

        # Usage
        final_outline = merge_outlines(final_outline, outline)

        save_json('data/outline.json', final_outline)
        return final_outline

    def _generate_and_validate(self, generate_prompt, validate_prompt, **kwargs):
        max_attempts = self.config.get('max_outline_generation_attempts', 3)
        feedback = None
        for attempt in range(max_attempts):
            # Generate content
            generation_prompt = generate_prompt.format(**kwargs)
            if attempt > 0:
                # Include previous feedback in the generation prompt
                generation_prompt += f"\n\nPrevious attempt feedback: {feedback}\nPlease address these issues in your next generation attempt."
            try:
                content = self.llm_service.generate(generation_prompt, format="json")
            except ModelError as e:
                logging.warning(f"Model Error. Using fallback provider and model. Error: {str(e)}")
                tmp_llm_service = LLMService(provider_name=self.config.get('llm_fallback_provider', 'openai'), default_model=self.config.get('llm_fallback_model', 'gpt-4o'))
                content = tmp_llm_service.generate(generation_prompt, format="json")


            # Validate content
            validate_kwargs = kwargs.copy()
            validate_kwargs['content'] = json.dumps(content)
            validation = self.llm_service.generate(validate_prompt.format(**validate_kwargs), format="json")

            if type(validation) is dict and "is_valid" in validation and validation['is_valid']:
                return content
            else:
                if type(validation) is not dict:
                    logging.warning(f"Validation failed. Attempt {attempt + 1}/{max_attempts}. No feedback provided.")
                    continue
                feedback = validation.get('feedback', "No feedback provided.")
                logging.warning(f"Validation failed. Attempt {attempt + 1}/{max_attempts}. Feedback: {feedback}")


        raise ValueError(f"Failed to generate valid content after {max_attempts} attempts.")

    def develop_characters(self, concept, outline):
        logging.info("Developing characters")
        prompt = self.prompts['develop_characters'].format(
            concept=concept,
            outline=json.dumps(outline),
            initial_script=self.initial_script if self.initial_script else "No initial script provided."
        )
        characters = self.llm_service.generate(prompt, format="json")
        save_json('data/characters.json', characters)
        return characters

    def identify_themes(self, concept, outline):
        logging.info("Identifying themes")
        prompt = self.prompts['identify_themes'].format(
            concept=concept,
            outline=json.dumps(outline),
            initial_script=self.initial_script if self.initial_script else "No initial script provided."
        )
        themes = self.llm_service.generate(prompt, format="json")
        save_json('data/themes.json', themes)
        return themes

    def write_scenes(self, outline, characters, themes):
        logging.info("Writing scenes")
        full_script = self.initial_script + "\n\n" if self.initial_script else ""
        start_scene = 1 if not self.initial_script else len(outline['scenes']) + 1
        for scene in tqdm(outline['scenes'][start_scene - 1:], desc="Writing scenes"):
            scene_content = self.write_single_scene(scene, characters, themes, full_script)
            scene_filename = f"data/script_sections/section_{scene['scene_number']:03d}.txt"
            save_txt(scene_filename, scene_content)
            full_script += scene_content + "\n\n"
        return full_script

    def write_single_scene(self, scene, characters, themes, script_so_far):
        best_scene = ""
        best_score = 0
        for i in range(self.max_iterations):
            prompt = self.prompts['write_scene'].format(
                scene=json.dumps(scene),
                characters=json.dumps(characters),
                themes=json.dumps(themes),
                script_so_far=script_so_far,
                initial_script=self.initial_script if self.initial_script else "No initial script provided."
            )
            scene_content = self.llm_service.generate(prompt)
            score, feedback = self.evaluate_scene(scene_content, scene, characters, themes, script_so_far)

            if score > best_score:
                best_scene = scene_content
                best_score = score

            if score >= self.good_scene_threshold:  # Assuming 0.8 is our threshold for a good scene
                logging.info(f"Acceptable scene generated after {i + 1} iterations")
                return scene_content

            logging.info(f"Scene iteration {i + 1} score: {score}. Feedback: {feedback}")

        logging.warning(
            f"Could not generate satisfactory scene after {self.max_iterations} iterations. Using best scene (score: {best_score})")
        return best_scene

    def evaluate_scene(self, scene_content, scene, characters, themes, script_so_far):
        prompt = self.prompts['evaluate_scene'].format(
            scene_content=scene_content,
            scene=json.dumps(scene),
            characters=json.dumps(characters),
            themes=json.dumps(themes),
            script_so_far=script_so_far,
            initial_script=self.initial_script if self.initial_script else "No initial script provided."
        )
        evaluation = self.llm_service.generate(prompt, format="json")
        return evaluation['score'], evaluation['feedback']

    def review_script(self, script, outline, characters, themes):
        logging.info("Reviewing script")
        prompt = self.prompts['review_script'].format(
            script=script,
            outline=json.dumps(outline),
            characters=json.dumps(characters),
            themes=json.dumps(themes),
            initial_script=self.initial_script if self.initial_script else "No initial script provided."
        )
        analysis = self.llm_service.generate(prompt, format="json")
        return analysis