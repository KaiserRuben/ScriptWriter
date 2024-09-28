# prompts.py

GENERATE_ACTS = """
Concept:
```
{concept}
```


Task:
Based solely on the concept, generate a high-level structure for the story. The number of acts should match what is specified in the concept. Include a brief description of each act and its main focus. Ensure that all key elements from the concept are accurately represented.

Important guidelines:
1. Use only the information provided in the concept. Do not introduce any elements that are not explicitly mentioned.
2. Pay special attention to use correct names, events, and concepts as described in the concept.
3. The acts should follow the progression outlined in the concept.
4. Do not make assumptions or add details that are not present in the given concept.


Respond in JSON format with the following structure:
{{
  "title": "Story Title",
  "concept": "Brief concept description",
  "acts": [
    {{
      "act_number": 1,
      "title": "Act 1 Title",
      "description": "Act 1 description"
    }},
    ...
  ]
}}
Start with {{... and end with ...}}. Only return valid json as response.

Ensure that your response includes the exact number of acts as specified or implied in the concept.
"""

VALIDATE_ACTS = """
Concept:
```
{concept}
```

Acts to validate:
```
{content}
```


Task:
Review the following act structure for the story. Ensure it provides a solid foundation for the narrative, covers all major story beats, and accurately aligns with the provided concept. Pay special attention to the following points:

1. The structure should have the exact number of acts as specified or implied in the concept.
2. The acts should accurately represent all key elements of the story as described in the concept.
3. There should be no elements or details that are not present in the original concept.
4. The acts should follow the progression outlined in the concept.
5. Names, events, and concepts should match those in the provided concept exactly.

Respond in JSON format with the following structure:
{{
  "is_valid": true/false,
  "feedback": "Detailed feedback explaining why the acts are valid or invalid. If invalid, provide specific points of discrepancy with the original concept."
}}
Start with {{... and end with ...}}. Only return valid json as response.

If any of the above points are not met, or if there are any inconsistencies with the original concept, mark the acts as invalid and provide detailed feedback.
"""

GENERATE_KEY_SCENES = """
Concept:
{concept}

Current Act:
{act}

All Acts:
{full_acts}


Task:
Based on the concept and act information, generate key scenes for this current act. Each scene should be a major plot point or important moment in the story. 

Respond in JSON format with the structure: 
{{
  "scenes": [
    {{
      "scene_number": "1.1", 
      "title": "Scene Title", 
      "description": "Scene description"
    }}
  ]
}}
Start with {{... and end with ...}}. Only return valid json as response.
"""

VALIDATE_KEY_SCENES = """
Concept:
{concept}

All Acts:
{full_acts}

Current Act:
{act}

Key Scenes:
{content}


Task:
Review the following key scenes for the act. Ensure they represent significant plot points, advance the story, and align with the act's purpose and the overall concept. Consider the context of all acts. Make sure that names and events match those in the concept exactly. If the scenes are valid, don't provide feedback as the scenes are already correct. 

Respond in JSON format with the structure: 
{{
  "is_valid": true/false, 
  "feedback": "Detailed feedback if not valid; if valid, leave empty"
}}
Start with {{... and end with ...}}. Only return valid json as response.
"""

GENERATE_SUB_SCENES = """
Concept:
{concept}

All Scenes:
{full_scenes}

Previous Scene:
{previous_scene}

Current Scene:
{scene}


Task:
Based on the following concept and scene information, generate detailed sub-scenes for this key scene. Each sub-scene should provide more specific plot details and character moments. 

Respond in JSON format with the structure: 
{{
  "sub_scenes": [
    {{
      "sub_scene_number": "1.1.1", 
      "title": "Sub-scene Title", 
      "description": "Sub-scene description"
    }}
  ]
}}
Start with {{... and end with ...}}. Only return valid json as response.
"""

VALIDATE_SUB_SCENES = """
Concept:
{concept}

All Scenes:
{full_scenes}

Previous Scene:
{previous_scene}

Current Scene:
{scene}

Sub-scenes:
{content}

Task:
Review the following sub-scenes. Ensure they provide detailed plot development, character moments, and thematic exploration that align with the key scene, previous scene (if applicable), and overall concept. Consider the context of all scenes. If the scenes are valid, don't provide feedback as the scenes are already correct. 

Respond in JSON format with the structure: 
{{
  "is_valid": true/false, 
  "feedback": "Detailed feedback if not valid; if valid, leave empty"
}}
Start with {{... and end with ...}}. Only return valid json as response.
"""

REVIEW_OUTLINE = """
Concept:
{concept}

Outline:
{outline}



Task:
Review and refine the provided outline based on the original concept. Your goal is to enhance the narrative structure while maintaining the core story idea. Please focus on the following aspects:

1. Consistency: Ensure all elements align with the original concept and maintain internal logic.
2. Pacing: Evaluate and adjust the story's rhythm, ensuring a balanced flow of events and character development.
3. Character Development: Strengthen character arcs and interactions to support the overall narrative.
4. Plot Structure: Refine the sequence of events to create a compelling and coherent story progression. Make sure, all plot elements are present, pay attention to sup-plots as-well.
5. Theme Reinforcement: Emphasize key themes throughout the outline to add depth to the narrative.

Guidelines for Modifications:
- For minor adjustments, modify existing scenes directly.
- When adding new content, use decimal scene numbers to avoid overwriting existing scenes (e.g., a new scene between 1.1 and 1.2 should be numbered 1.1.1).
- Only include parts of the outline that you have modified or added in your response.

Response Format:
- Begin your response with {{ and end with }}.
- Use valid JSON format for your entire response.
- Include only the modified or new portions of the outline.

Start with {{... and end with ...}}. Only return valid json as response.
"""

VALIDATE_FINAL_OUTLINE = """
Concept:
{concept}

Outline:
{content}


Task:
Review the entire outline. Ensure it forms a coherent narrative, maintains proper pacing, develops characters and themes effectively, and stays true to the original concept. Check for any inconsistencies or areas that need improvement. 

Respond in JSON format with the structure: 
{{
  "is_valid": true/false, 
  "feedback": "Detailed feedback if not valid"
}}
Start with {{... and end with ...}}. Only return valid json as response.
"""