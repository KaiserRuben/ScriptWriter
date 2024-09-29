import logging
from src.script_automator import ScriptAutomator
from src.utils.file_handlers import load_txt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Starting script automation process")
    automator = ScriptAutomator()
    automator.run(generate_outline=False, generate_characters=False, generate_themes=False, generate_scenes=True)
    logging.info("Script automation process completed")


if __name__ == "__main__":
    main()