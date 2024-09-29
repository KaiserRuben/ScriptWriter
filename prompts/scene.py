GENERATE_SCENE = """
Data:
Characters: 
{characters}

Themes: 
{themes}

Outline: 
{outline}

Current Scene: 
{current_scene}

Script Context (Last {context_length} characters): 
{full_script_context}

Task:
As an expert screenwriter with deep knowledge of the {genre} genre, your task is to write a compelling screenplay for the current scene. This scene should seamlessly integrate into the larger narrative (Outline) while advancing the plot, developing characters, and exploring key themes.

Guidelines:
1. Maintain consistency with the established characters, their voices, and arcs.
2. Advance the plot in meaningful ways that align with the outline.
3. Incorporate and explore the identified themes relevant to this scene.
4. Use vivid descriptions for actions and engaging dialogue.
5. Ensure the scene fits within the given context and flows naturally from the previous scenes.
6. Pay special attention to the unique elements of {genre}, incorporating them organically into the scene.
7. Utilize the provided context to maintain consistency and continuity throughout the script.
8. "Show, don't tell" - use actions and dialogue to convey information and emotions effectively.

Output Format:
Provide the scene in the following JSON format:

{{
  "scene_number": "string",
  "location": "string",
  "time": "string",
  "content": [
    {{
      "type": "action" | "dialog" | "transition",
      "character": "string" (only if type is "dialog"),
      "text": "string"
    }}
  ]
}}

Ensure all required fields are included and formatted correctly.
"""

EVALUATE_SCENE = """
Data:
Outline:
{outline}

Scene Details: 
{scene_details}

Characters: 
{characters}

Themes: 
{themes}

Current Scene (in Markdown format): 
{scene_content}

Task:
As a seasoned script editor and {genre} expert, critically evaluate the current scene (in its context -> Outline) based on the following criteria:

1. Character consistency and development (0-20 points)
2. Plot advancement (0-20 points)
3. Thematic exploration (0-20 points)
4. Dialogue quality (0-15 points)
5. Descriptive writing and atmosphere (0-15 points)
6. Consistency with overall story and {genre} elements (0-10 points)

For each criterion, provide a score and a brief justification. Be specific in your feedback, referencing particular elements of the scene that work well or need improvement.

Output Format:
Respond in the following JSON format:
{{
  "criteria": {{
    "character_consistency": {{"justification": "","score": 0}},
    "plot_advancement": {{"justification": "","score": 0}},
    "thematic_exploration": {{"justification": "","score": 0}},
    "dialogue_quality": {{"justification": "","score": 0}},
    "descriptive_writing": {{"justification": "","score": 0}},
    "story_consistency": {{"justification": "","score": 0}}
  }},
  "total_score": 0,
  "feedback": "Specific feedback here, organized by areas for improvement"
}}
"""

REFINE_SCENE = """
Data:
Characters: 
{characters}

Themes: 
{themes}

Original Scene (in JSON format): 
{scene_content}

Feedback: 
{feedback}

Scene Details: 
{scene_details}

Full Script Context (Last {context_length} characters): 
{full_script_context}

Task:
As a skilled script doctor specializing in {genre}, your task is to refine the given scene based on the provided feedback. Your goal is to address the issues raised while maintaining the scene's core elements, purpose, and style consistency with the initial script.

Guidelines for refinement:
1. Address each point of feedback systematically, focusing on the areas that received lower scores in the evaluation.
2. Maintain the scene's original purpose and key plot points.
3. Enhance character interactions and dialogue to better reflect their established voices and development arcs.
4. Strengthen the integration of themes relevant to this scene.
5. Improve descriptive writing and atmosphere where indicated, ensuring it aligns with the {genre}.
6. Ensure consistency with the overall story and character arcs.
7. Maintain the writing style established in the initial script.
8. Use the provided context to ensure continuity with previous scenes.

Output Format:
Provide the refined scene in the following JSON format:

{{
  "scene_number": "string",
  "location": "string",
  "time": "string",
  "content": [
    {{
      "type": "action" | "dialog" | "transition",
      "character": "string" (only if type is "dialog"),
      "text": "string"
    }}
  ]
}}

Ensure all required fields are included and formatted correctly.
"""

EXTRACT_STORY_ELEMENTS = """
Outline:
{outline}

Task:
Analyze the following scene and extract key story elements:

{scene_content}

Task:
1. Identify important details such as character names, locations, objects, or events introduced in this scene.
2. Note any information that might be relevant for future scenes.
3. Specify the scope of each piece of information (e.g., "global" for information relevant to the entire story, "act" for information relevant to the current act, or "scene" for information only relevant to this specific scene).

Output Format:
Provide the extracted story elements in JSON format:
{{
    "story_elements": [
        {{
            "type": "character_name" | "location" | "object" | "event" | "other",
            "content": "Extracted information",
            "scope": "global" | "act" | "scene",
            "scene_number": "{scene_number}"
        }}
    ]
}}
        """

EVALUATE_FULL_SCRIPT = """
Given Data:
Full Script: {full_script}
Outline: {outline}
Characters: {characters}
Themes: {themes}

Task:
As a veteran showrunner and {genre} aficionado, conduct a comprehensive evaluation of the full script. Assess how well it comes together as a cohesive narrative, paying special attention to the overall flow, character arcs, and thematic exploration. Evaluate based on these criteria:

1. Overall narrative coherence (0-25 points)
2. Character development across scenes (0-25 points)
3. Thematic consistency and exploration (0-20 points)
4. Pacing and structure (0-15 points)
5. Dialogue consistency across scenes (0-15 points)

For each criterion, provide a score and a detailed justification. Be specific in your feedback, referencing particular scenes or story elements that stand out, both positively and negatively.

Additionally, identify any specific scenes that could be improved to enhance the overall script quality. For each scene identified, provide a clear reason for why it needs improvement and how it could better serve the overall narrative.

Output Format:
Respond in the following JSON format:
{{
  "criteria": {{
    "narrative_coherence": {{"justification": "","score": 0}},
    "character_development": {{"justification": "","score": 0}},
    "thematic_consistency": {{"justification": "","score": 0}},
    "pacing_and_structure": {{"justification": "","score": 0}},
    "dialogue_consistency": {{"justification": "","score": 0}}
  }},
  "scenes_to_improve": [
    {{
      "scene_id": "scene identifier",
      "reason": "Reason for improvement",
      "suggestions": "Specific suggestions for enhancement"
    }}
  ],
  "total_score": 0,
  "feedback": "Overall feedback here, summarizing the script's strengths and weaknesses",
}}
"""