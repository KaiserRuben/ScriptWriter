# 🎬 Script Automation Project

## 📚 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Installation](#-installation)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [How It Works](#-how-it-works)
- [Example Output](#-example-output)
- [Limitations and Future Improvements](#-limitations-and-future-improvements)
- [Contributing](#-contributing)

## 🌟 Overview

The Script Automation Project is an innovative tool designed to assist in the creation of movie scripts and screenplays using advanced language models. This project leverages the power of AI to generate outlines, develop characters, identify themes, and create individual scenes, culminating in a complete script.

**Note: This tool is still in active development. While it produces interesting and sometimes surprising results, the output should be considered a creative starting point rather than a polished, ready-to-use script. Human intervention and editing are essential parts of the creative process.**

## 🚀 Features

- 📝 Automated generation of script outlines
- 👥 Character development based on the story concept
- 🎭 Theme identification and integration
- 🎥 Scene-by-scene generation with context awareness
- 🔄 Iterative refinement of generated content
- ⚙️ Flexible configuration options
- 🧠 Support for multiple language model providers

## 🛠️ Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/script-automation-project.git
   cd script-automation-project
   ```

2. Install Poetry (if not already installed):
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Install project dependencies:
   ```
   poetry install
   ```

## 🏁 Getting Started

Before running the script automation tool, you need to set up a few things:

1. **Concept File**: 
   - Create a `concept.txt` file in the `data` folder.
   - This file should contain a detailed description of your movie/script concept.
   - Include elements like plot summary, character descriptions, themes, and any specific requirements.

2. **Settings Configuration**:
   - Navigate to the `config` folder.
   - Edit the `settings.json` file to customize the behavior of the script generation process.
   - Key settings include LLM provider, model selection, and various thresholds for content generation.

3. **Prompt Customization** (Optional):
   - If you want to fine-tune the AI's output, you can edit the prompts in the `prompts` folder.
   - Files to consider:
     - `main.py`: Contains prompts for character development and theme identification.
     - `outline.py`: Includes prompts for generating and validating script structure.
     - `scene.py`: Holds prompts for scene generation and evaluation.

## 🖥️ Usage

1. Activate the Poetry environment:
   ```
   poetry shell
   ```

2. Run the main script:
   ```
   python main.py
   ```

3. Customize the generation process by modifying the `main.py` file:
   ```python
   automator.run(
       generate_outline=True,
       generate_characters=True,
       generate_themes=True,
       generate_scenes=True,
       start_with_scene=None  # Specify a scene number to continue from a specific point
   )
   ```

4. Check the `output` folder for generated content.

## ⚙️ Configuration

Edit the `config/settings.json` file to customize the script generation process:

```json
{
  "llm_provider": "ollama",
  "llm_model": "gemma2:27b",
  "llm_provider_validation": "ollama",
  "llm_model_validation": "gemma2:27b",
  "llm_fallback_provider": "openai",
  "llm_fallback_model": "gpt-4",
  "max_outline_generation_attempts": 3,
  "max_scene_iterations": 5,
  "good_scene_threshold": 80,
  "full_script_threshold": 85,
  "use_local_context": true,
  "context_length": 10000,
  "genre": "science fiction"
}
```

Adjust these settings to fine-tune the generation process and output quality.

## 🔍 How It Works

1. **Initialization**: The system loads configuration settings and initializes LLM services.

2. **Outline Generation**: 
   - Generates the overall structure (acts) of the script.
   - Creates key scenes for each act.
   - Develops sub-scenes for each main scene.

3. **Character Development**: 
   - Analyzes the concept and outline to create detailed character profiles.

4. **Theme Identification**: 
   - Extracts and defines the main themes of the story.

5. **Scene Generation**:
   - Iterates through each sub-scene in the outline.
   - Generates scene content using prompts and LLMs.
   - Evaluates and refines scenes based on quality criteria.

6. **Script Compilation and Refinement**:
   - Compiles individual scenes into a full script.
   - Evaluates the complete script for coherence and quality.
   - Refines specific scenes to improve the overall narrative.

## 📘 Example Output

Examples can be found in the [examples](examples) folder. These include generated outlines, character profiles, themes, and scenes for an example movie concepts.
## 🚧 Limitations and Future Improvements

- The current version may produce inconsistencies in character behavior or plot details across scenes.
- Long-term context management across the entire script is an area for improvement.
- Integration with more sophisticated natural language understanding models could enhance theme consistency and character development.
- User interface for easier interaction and real-time script editing is planned for future versions.
- The project is currently developed sporadically, as time allows.

## 🤝 Contributing

Contributions to the Script Automation Project are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes with clear, descriptive commit messages.
4. Push your branch and submit a pull request.

For major changes, please open an issue first to discuss the proposed changes.

---