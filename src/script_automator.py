import logging
from typing import Dict, Any

from replicate.exceptions import ModelError
from tqdm import tqdm
import json

from prompts.main import DEVELOP_CHARACTERS, IDENTIFY_THEMES, WRITE_SCENE, EVALUATE_SCENE, REVIEW_SCRIPT
from prompts.outline import GENERATE_ACTS, VALIDATE_ACTS, GENERATE_KEY_SCENES, VALIDATE_KEY_SCENES, GENERATE_SUB_SCENES, \
    VALIDATE_SUB_SCENES, REVIEW_OUTLINE, VALIDATE_FINAL_OUTLINE
from src.llm.LLMService import LLMService
from src.utils.file_handlers import load_json, save_json, load_txt, save_txt


def sort_json_content(json_data: Dict[str, Any]) -> Dict[str, Any]:
    # Sort acts
    json_data['acts'] = sorted(json_data['acts'], key=lambda x: x['act_number'])

    # Sort scenes and sub-scenes within each act
    for act in json_data['acts']:
        act['scenes'] = sorted(act['scenes'], key=lambda x: float(x['scene_number']))

        for scene in act['scenes']:
            if 'sub_scenes' in scene:
                scene['sub_scenes'] = sorted(scene['sub_scenes'], key=lambda x: x['sub_scene_number'])

    return json_data


def merge_outlines(original_outline, new_outline):
    # Merge top-level attributes
    merged = {
        "title": new_outline.get("title", original_outline.get("title")),
        "concept": new_outline.get("concept", original_outline.get("concept")),
        "acts": []
    }

    # Create a dictionary of acts for easier merging
    original_acts = {act["act_number"]: act for act in original_outline.get("acts", [])}
    new_acts = {act["act_number"]: act for act in new_outline.get("acts", [])}

    # Merge acts
    for act_number in set(original_acts.keys()) | set(new_acts.keys()):
        if act_number in new_acts:
            merged_act = new_acts[act_number]
            if act_number in original_acts:
                # Merge scenes
                original_scenes = {scene["scene_number"]: scene for scene in
                                   original_acts[act_number].get("scenes", [])}
                new_scenes = {scene["scene_number"]: scene for scene in merged_act.get("scenes", [])}

                merged_scenes = []
                for scene_number in set(original_scenes.keys()) | set(new_scenes.keys()):
                    if scene_number in new_scenes:
                        merged_scene = new_scenes[scene_number]
                        if scene_number in original_scenes:
                            # Merge sub-scenes
                            original_sub_scenes = {sub["sub_scene_number"]: sub for sub in
                                                   original_scenes[scene_number].get("sub_scenes", [])}
                            new_sub_scenes = {sub["sub_scene_number"]: sub for sub in
                                              merged_scene.get("sub_scenes", [])}

                            merged_sub_scenes = list(new_sub_scenes.values())  # Prioritize new sub-scenes
                            for sub_number, sub_scene in original_sub_scenes.items():
                                if sub_number not in new_sub_scenes:
                                    merged_sub_scenes.append(sub_scene)

                            merged_scene["sub_scenes"] = merged_sub_scenes
                    else:
                        merged_scene = original_scenes[scene_number]
                    merged_scenes.append(merged_scene)

                merged_act["scenes"] = merged_scenes
        else:
            merged_act = original_acts[act_number]

        merged["acts"].append(merged_act)

    # Sort acts by act_number
    merged["acts"].sort(key=lambda x: x["act_number"])

    return merged


class ScriptAutomator:
    def __init__(self, initial_script=None):
        self.config = load_json('config/settings.json')
        self.llm_service = LLMService(provider_name=self.config.get('llm_provider', 'ollama'),
                                      default_model=self.config.get('llm_model', 'gemma2:27b'))
        self.max_iterations = self.config.get('max_scene_iterations', 5)
        self.good_scene_threshold = self.config.get('good_scene_threshold', 0.8)
        self.initial_script = initial_script
        self.use_local_context = self.config.get('use_local_context', True)

    def run(self):
        concept = load_txt('data/concept.txt')
        # outline = self.generate_outline(concept)
        outline = sort_json_content(load_json('data/outline.json'))
        characters = self.develop_characters(concept, outline)
        themes = self.identify_themes(concept, outline)
        script = self.write_scenes(outline, characters, themes)
        analysis = self.review_script(script, outline, characters, themes)

        save_txt('output/full_script.txt', script)
        save_json('output/script_analysis.json', analysis)
        logging.info("Script generation complete. Check the 'output' folder for results.")

    def generate_outline(self, concept):
        logging.info("Generating outline")
        outline = self._generate_and_validate(GENERATE_ACTS, VALIDATE_ACTS, concept=concept)

        for act in tqdm(outline['acts'], desc="Generating scenes", unit="act"):
            act_scenes = self._generate_and_validate(GENERATE_KEY_SCENES, VALIDATE_KEY_SCENES,
                                                     concept=concept, act=act, full_acts=outline['acts'])
            act['scenes'] = act_scenes['scenes']

            for scene in tqdm(act['scenes'], desc=f"Generating sub-scenes for Act {act['act_number']}", unit="scene"):
                sub_scenes = self._generate_and_validate(GENERATE_SUB_SCENES, VALIDATE_SUB_SCENES,
                                                         concept=concept, scene=scene, previous_scene=None,
                                                         full_scenes=act['scenes'])
                scene['sub_scenes'] = sub_scenes['sub_scenes']

        final_outline = self._generate_and_validate(REVIEW_OUTLINE, VALIDATE_FINAL_OUTLINE,
                                                    concept=concept, outline=outline)

        # Merge the final_outline with the original outline
        merged_outline = sort_json_content(merge_outlines(outline, final_outline))

        save_json('data/outline.json', merged_outline)
        return merged_outline

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
                tmp_llm_service = LLMService(provider_name=self.config.get('llm_fallback_provider', 'openai'),
                                             default_model=self.config.get('llm_fallback_model', 'gpt-4o'))
                content = tmp_llm_service.generate(generation_prompt, format="json")

            # Validate content
            validate_kwargs = kwargs.copy()
            validate_kwargs['content'] = json.dumps(content)
            try:
                validation = self.llm_service.generate(validate_prompt.format(**validate_kwargs), format="json")
            except ModelError as e:
                logging.warning(f"Model Error. Using fallback provider and model. Error: {str(e)}")
                tmp_llm_service = LLMService(provider_name=self.config.get('llm_fallback_provider', 'openai'),
                                             default_model=self.config.get('llm_fallback_model', 'gpt-4o'))
                validation = tmp_llm_service.generate(validate_prompt.format(**validate_kwargs), format="json")

            if isinstance(validation, dict) and validation.get('is_valid', False):
                return content
            else:
                feedback = validation.get('feedback', "No feedback provided.") if isinstance(validation,
                                                                                             dict) else "Invalid validation response"
                logging.warning(f"Validation failed. Attempt {attempt + 1}/{max_attempts}. Feedback: {feedback}")

        raise ValueError(f"Failed to generate valid content after {max_attempts} attempts.")

    def develop_characters(self, concept, outline):
        logging.info("Developing characters")
        prompt = DEVELOP_CHARACTERS.format(
            concept=concept,
            outline=json.dumps(outline),
            initial_script=self.initial_script if self.initial_script else "No initial script provided."
        )
        characters = self.llm_service.generate(prompt, format="json")
        save_json('data/characters.json', characters)
        return characters

    def identify_themes(self, concept, outline):
        logging.info("Identifying themes")
        prompt = IDENTIFY_THEMES.format(
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

        for act in tqdm(outline['acts'], desc="Writing acts"):
            for scene in tqdm(act['scenes'], desc=f"Writing scenes for Act {act['act_number']}", leave=False):
                scene_content = self.write_single_scene(scene, act, outline, characters, themes, full_script)
                scene_filename = f"data/script_sections/act_{act['act_number']}_scene_{scene['scene_number']}.txt"
                save_txt(scene_filename, scene_content)
                full_script += scene_content + "\n\n"

        return full_script

    def write_single_scene(self, scene, act, outline, characters, themes, full_script):
        best_scene = ""
        best_score = 0

        # Determine the context to use
        if self.use_local_context:
            context = self.get_local_context(scene, act, outline)
        else:
            context = full_script

        for i in range(self.max_iterations):
            prompt = WRITE_SCENE.format(
                scene=json.dumps(scene),
                act=json.dumps(act),
                outline=json.dumps(outline),
                characters=json.dumps(characters),
                themes=json.dumps(themes),
                context=context,
                initial_script=self.initial_script if self.initial_script else "No initial script provided."
            )
            scene_content = self.llm_service.generate(prompt)
            score, feedback = self.evaluate_scene(scene_content, scene, act, outline, characters, themes, context)

            if score > best_score:
                best_scene = scene_content
                best_score = score

            if score >= self.good_scene_threshold:
                logging.info(f"Acceptable scene generated after {i + 1} iterations")
                return scene_content

            logging.info(f"Scene iteration {i + 1} score: {score}. Feedback: {feedback}")

        logging.warning(
            f"Could not generate satisfactory scene after {self.max_iterations} iterations. Using best scene (score: {best_score})")
        return best_scene

    def get_local_context(self, scene, act, outline):
        context = ""

        # Get the previous scene in the same act
        scene_index = act['scenes'].index(scene)
        if scene_index > 0:
            prev_scene = act['scenes'][scene_index - 1]
            context += f"Previous scene: {json.dumps(prev_scene)}\n\n"

        # Get the next scene in the same act
        if scene_index < len(act['scenes']) - 1:
            next_scene = act['scenes'][scene_index + 1]
            context += f"Next scene: {json.dumps(next_scene)}\n\n"

        context += f"Current act number: {act['act_number']}\n\n"

        return context

    def evaluate_scene(self, scene_content, scene, act, outline, characters, themes, context):
        prompt = EVALUATE_SCENE.format(
            scene_content=scene_content,
            scene=json.dumps(scene),
            act=json.dumps(act),
            outline=json.dumps(outline),
            characters=json.dumps(characters),
            themes=json.dumps(themes),
            context=context,
        )
        evaluation = self.llm_service.generate(prompt, format="json")
        return evaluation['score'], evaluation['feedback']

    def review_script(self, script, outline, characters, themes):
        logging.info("Reviewing script")
        prompt = REVIEW_SCRIPT.format(
            script=script,
            outline=json.dumps(outline),
            characters=json.dumps(characters),
            themes=json.dumps(themes),
            initial_script=self.initial_script if self.initial_script else "No initial script provided."
        )
        analysis = self.llm_service.generate(prompt, format="json")
        return analysis
