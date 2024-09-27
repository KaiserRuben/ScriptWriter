import logging
from src.script_automator import ScriptAutomator
from src.utils.file_handlers import load_txt

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    logging.info("Starting script automation process")

    # Check if an initial script exists
    try:
        initial_script = load_txt('data/initial_script.txt')
        if len(initial_script):
            logging.info("Initial script loaded successfully.")
        else:
            initial_script = None
            logging.info("Initial script is empty. Starting from scratch.")
    except FileNotFoundError:
        initial_script = None
        logging.info("No initial script found. Starting from scratch.")

    automator = ScriptAutomator(initial_script)
    automator.run()
    logging.info("Script automation process completed")


if __name__ == "__main__":
    main()