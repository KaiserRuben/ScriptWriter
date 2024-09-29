DEVELOP_CHARACTERS = """As a character development specialist and dialogue coach for Star Trek, create detailed and extensive profiles for the relevant characters of 'Star Trek: Cognitive Horizon'. Base your character development on the given concept, outline, and initial script (if provided), ensuring that each character has a unique voice, background, and arc that contributes to the psychological horror elements of the story.

Concept:
{concept}

Outline:
{outline}

Initial Script:
{initial_script}

For each main character, provide the following information in JSON format:
1. Name and rank/role
2. Species and relevant background
3. Personality traits and quirks
4. Strengths and weaknesses
5. Personal goals and fears
6. Relationships with other characters
7. Unique perspective on the unfolding events
8. Character arc throughout the story
9. How their mind might be specifically affected by the anomaly

If an initial script is provided, ensure that your character profiles align with and build upon the portrayals established in that script.

Ensure that the characters represent a diverse range of perspectives and reactions to the psychological challenges they'll face. Consider how each character's background and personality will influence their experience of the reality-altering anomaly.

Provide the character profiles in the following JSON format:
{{
  "character_name": {{
    "rank": "...",
    "species": "...",
    "background": "...",
    "personality": ["..."],
    "strengths": ["..."],
    "weaknesses": ["..."],
    "goals": ["..."],
    "fears": ["..."],
    "relationships": {{"character_name": "description"}},
    "perspective": "...",
    "arc": "...",
    "anomaly_effect": "..."
  }}
}}"""

IDENTIFY_THEMES = """As an ethical philosopher and psychological horror expert, identify and develop the key themes for 'Star Trek: Cognitive Horizon'. Your analysis should be based on the given concept, outline, and initial script (if provided), focusing on the psychological, philosophical, and ethical implications of the story.

Concept:
```
{concept}
```

Outline:
{outline}

Identify and elaborate on the following in JSON format:
1. Main theme: The central philosophical or psychological question the story explores.
2. Sub-themes: Supporting themes that contribute to the main theme and overall narrative.
3. Ethical dilemmas: Moral quandaries faced by the characters due to their experiences.
4. Psychological concepts: Key psychological principles or phenomena explored in the story.
5. Star Trek connections: How these themes relate to or challenge traditional Star Trek ideals.
6. Horror elements: How the themes contribute to the psychological horror aspect of the story.

If an initial script is provided, ensure that your thematic analysis aligns with and builds upon the themes established in that script.

Ensure that the themes you identify are deeply woven into the narrative, character arcs, and the overall concept of cognitive distortion and reality alteration.

Provide your analysis in the following JSON format:
{{
  "main_theme": {{
    "description": "...",
    "exploration": "..."
  }},
  "sub_themes": [
    {{
      "name": "...",
      "description": "...",
      "relevance": "..."
    }}
  ],
  "ethical_dilemmas": [
    {{
      "situation": "...",
      "dilemma": "...",
      "implications": "..."
    }}
  ],
  "psychological_concepts": [
    {{
      "concept": "...",
      "application": "...",
      "impact": "..."
    }}
  ],
  "star_trek_connections": [
    {{
      "theme": "...",
      "traditional_view": "...",
      "challenge_or_extension": "..."
    }}
  ],
  "horror_elements": [
    {{
      "element": "...",
      "psychological_impact": "...",
      "manifestation": "..."
    }}
  ]
}}"""

WRITE_SCENE = """As a seasoned Star Trek writer with expertise in psychological horror, write the following scene for 'Star Trek: Cognitive Horizon'. Blend elements of classic Star Trek with escalating psychological tension and subtle horror. Pay close attention to character voices, thematic relevance, and the gradual distortion of reality.

Scene Details:
{scene}

Act:
{act}

Outline:
{outline}

Characters:
{characters}

Themes:
{themes}

Local Script Context:
{context}

Initial Script (for style reference):
{initial_script}

Guidelines for writing the scene:
1. Begin with a vivid description of the setting, incorporating subtle elements of wrongness or unease.
2. Introduce characters through action and dialogue that reflects their unique voices and current psychological states.
3. Advance the plot while weaving in thematic elements and building tension.
4. Include detailed sensory descriptions, especially focusing on visual and auditory elements that may be subtly distorted.
5. End the scene with a hook or a moment of realization that drives the story forward and deepens the psychological horror.
6. Ensure continuity with the script so far and the initial script (if provided), building upon previous events and character developments.
7. Maintain the style, tone, and pacing established in the initial script (if provided).

Remember to:
- Maintain the balance between Star Trek's spirit of exploration and the encroaching psychological horror.
- Use technical jargon appropriate to Star Trek, but describe the inexplicable in ways that create a sense of dread.
- Show the characters attempting to rationalize their experiences, with increasing difficulty as reality becomes more distorted.
- Incorporate elements of the 'living dimension' concept, suggesting that the environment itself might be sentient or reactive.

Write the scene in standard screenplay format, including scene headings, action descriptions, and dialogue. Focus on creating a mounting sense of psychological tension and unease throughout the scene, while staying true to the style established in the initial script (if provided)."""

EVALUATE_SCENE = """As a critical script reviewer with expertise in both Star Trek and psychological horror, evaluate the following scene for 'Star Trek: Cognitive Horizon'. Assess how well it balances Star Trek elements with psychological horror, maintains character consistency, advances the plot, and explores the established themes.

Scene content:
{scene_content}

Scene:
{scene}

Act:
{act}

Outline:
{outline}

Characters:
{characters}

Themes:
{themes}

Scene Context:
{context}

Provide a score from 0 to 1 (where 1 is perfect) and detailed feedback on the following aspects:
1. Consistency with Star Trek universe and tone
2. Quality of psychological horror elements
3. Character voice and development
4. Thematic exploration
5. Plot advancement
6. Dialogue quality
7. Descriptive writing and atmosphere
8. Continuity with previous scenes and the initial script (if provided)
9. Adherence to the style established in the initial script (if provided)

Based on these aspects, provide an overall score and constructive feedback for improvement.

Respond in the following JSON format:
{{
  "score": 0.0,
  "feedback": "Detailed feedback here",
  "aspects": {{
    "star_trek_consistency": {{"score": 0.0, "comments": ""}},
    "psychological_horror": {{"score": 0.0, "comments": ""}},
    "character_development": {{"score": 0.0, "comments": ""}},
    "thematic_exploration": {{"score": 0.0, "comments": ""}},
    "plot_advancement": {{"score": 0.0, "comments": ""}},
    "dialogue_quality": {{"score": 0.0, "comments": ""}},
    "descriptive_writing": {{"score": 0.0, "comments": ""}},
    "continuity": {{"score": 0.0, "comments": ""}},
    "style_adherence": {{"score": 0.0, "comments": ""}}
  }}
}}"""

REVIEW_SCRIPT = """As a comprehensive script reviewer with expertise in both Star Trek and psychological horror, provide a detailed analysis of the complete 'Star Trek: Cognitive Horizon' script. Evaluate how well the script balances classic Star Trek elements with psychological horror, and assess its effectiveness in exploring the themes and character arcs established in the concept.

Script:
{script}

Outline:
{outline}

Characters:
{characters}

Themes:
{themes}

Initial Script (for reference):
{initial_script}

Provide a detailed review addressing the following aspects:
1. Overall narrative structure and pacing
2. Character development and consistency throughout the script
3. Dialogue quality and distinction of character voices
4. Integration and exploration of established themes
5. Effectiveness of the psychological horror elements
6. Balance of Star Trek sci-fi elements with horror aspects
7. Plausibility of the scientific and psychological concepts presented
8. Visual and auditory descriptions, especially of the 'living dimension'
9. Ethical dilemmas and their exploration
10. Satisfaction of the resolution and its implications for the characters and Star Trek universe
11. Consistency with the style and tone established in the initial script (if provided)

For each aspect, provide:
- A brief assessment
- Specific examples from the script
- Suggestions for improvement, if necessary

Additionally, include:
- Strengths of the script
- Areas for improvement
- Overall impression and potential impact on the Star Trek franchise

Provide your review in the following JSON format:
{{
  "overall_quality": "...",
  "strengths": ["..."],
  "areas_for_improvement": ["..."],
  "aspects": {{
    "narrative_structure": {{
      "assessment": "...",
      "examples": ["..."],
      "suggestions": ["..."]
    }},
    "character_development": {{
      "assessment": "...",
      "examples": ["..."],
      "suggestions": ["..."]
    }},
    "dialogue": {{
      "assessment": "...",
      "examples": ["..."],
      "suggestions": ["..."]
    }},
    "theme_integration": {{
      "assessment": "...",
      "examples": ["..."],
      "suggestions": ["..."]
    }},
    "horror_elements": {{
      "assessment": "...",
      "examples": ["..."],
      "suggestions": ["..."]
    }},
    "star_trek_balance": {{
      "assessment": "...",
      "examples": ["..."],
      "suggestions": ["..."]
    }},
    "scientific_plausibility": {{
      "assessment": "...",
      "examples": ["..."],
      "suggestions": ["..."]
    }},
    "visual_auditory_descriptions": {{
      "assessment": "...",
      "examples": ["..."],
      "suggestions": ["..."]
    }},
    "ethical_exploration": {{
      "assessment": "...",
      "examples": ["..."],
      "suggestions": ["..."]
    }},
    "resolution": {{
      "assessment": "...",
      "examples": ["..."],
      "suggestions": ["..."]
    }},
    "style_consistency": {{
      "assessment": "...",
      "examples": ["..."],
      "suggestions": ["..."]
    }}
  }},
  "overall_impression": "...",
  "franchise_impact": "..."
}}"""

