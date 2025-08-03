import json
from acrcloud.recognizer import ACRCloudRecognizer
import config

class ACRCloudClient:
    def __init__(self):
        # Initialize recognizer with project credentials
        self.config_obj = {
            "host": config.ACRCLOUD_HOST,
            "access_key": config.ACRCLOUD_KEY,
            "access_secret": config.ACRCLOUD_SECRET,
            "timeout": 10  # seconds
        }

        self.recognizer = ACRCloudRecognizer(self.config_obj)


    def identify_song(self, audio_data: bytes, start_seconds: int = 0, rec_length: int = 10) -> dict:
        try:
            # SDK will extract fingerprint, call ACRCloud, and return raw JSON string
            result_json = self.recognizer.recognize_by_filebuffer(audio_data, start_seconds, rec_length)

            # Parse the JSON string to Python dict
            result = json.loads(result_json)

            # Check if the result is valid
            if result.get("status", {}).get("msg") != "Success":
                raise RuntimeError(f"ACRCloud returned failure: {result.get('status', {})}")

            return result

        except json.JSONDecodeError:
            raise ValueError("ACRCloud returned invalid JSON response.")
        except Exception as e:
            raise RuntimeError(f"Failed to recognize audio: {str(e)}")
