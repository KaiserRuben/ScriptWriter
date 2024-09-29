import json
from typing import Optional, Dict, Any


class JSONValidator:
    @staticmethod
    def validate_scene_json(scene_json: str) -> Optional[Dict[str, Any]]:
        try:
            # Check for required keys
            required_keys = ["scene_number", "location", "time", "content"]
            for key in required_keys:
                if key not in scene_json:
                    raise KeyError(f"Missing required key: {key}")

            # Validate content structure
            if not isinstance(scene_json["content"], list):
                raise TypeError("'content' must be a list")

            for item in scene_json["content"]:
                if not isinstance(item, dict):
                    raise TypeError("Each item in 'content' must be a dictionary")

                if "type" not in item:
                    raise KeyError("Each content item must have a 'type'")

                if item["type"] not in ["dialog", "action", "transition"]:
                    raise ValueError(f"Invalid content type: {item['type']}")

                if "text" not in item:
                    raise KeyError("Each content item must have 'text'")

                if item["type"] == "dialog" and "character" not in item:
                    raise KeyError("Dialog items must have a 'character'")

            return scene_json
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
        except (KeyError, TypeError, ValueError) as e:
            print(f"Validation error: {e}")

        return None