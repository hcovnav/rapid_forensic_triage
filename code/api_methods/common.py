from pathlib import Path
import json

def get_gemini_api_key(cwd):
    """Reads the Gemini API key from a local config.json file.

    This function securely retrieves the API key from a configuration file
    expected to be in the root of the project directory. This approach avoids
    hardcoding sensitive credentials directly into the source code.

    Args:
        cwd (str): The current working directory of the main application, used to
            construct the path to the 'config.json' file.

    Returns:
        str: The Gemini API key if the file and key are found. Returns a
             placeholder string or an error message if the file is not found
             or the key is missing.
    """
    try:
        with open(Path(cwd) / "config.json", "r") as config_file:
            config = json.load(config_file)
        return config.get("gemini_api_key", "YOUR_API_KEY_HERE")
    except FileNotFoundError:
        print("[-] config.json not found. Please ensure it exists and contains your API key.")
        return "Unable to retrieve the Gemini API key."

