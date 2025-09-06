import tempfile
import os
import essentia.standard as es
from exceptions import EssentiaExtractorError, TempFileWritingError
import json

class EssentiaExtractor:
    def __init__(self, profile_path: str = "songProfile.yaml"):
        # Configure which statistics you want
        if not os.path.exists(profile_path):
            raise FileNotFoundError(f"Essentia profile not found: {profile_path}")

        self.extractor = es.MusicExtractor(profile=profile_path)

        # Define only the features we want to keep
        self.allowed_features = {
            "rhythm.bpm",
            "tonal.chords_key",
            "tonal.chords_scale",
            "rhythm.danceability",
            "lowlevel.average_loudness",
        }

    def __pool_to_dict(self, pool) -> dict:
        """
        Recursively convert an Essentia Pool into a native Python dict.
        Handles lists, arrays, and nested structures.
        """
        result = {}
        for key in pool.descriptorNames():
            if key in self.allowed_features: # Filter only neccessary features
                value = pool[key]
                # Convert numpy arrays to list
                if hasattr(value, "tolist"):
                    result[key] = value.tolist()
                else:
                    result[key] = value
        return result

    def extract_from_bytes(self, audio_bytes: bytes, suffix=".wav") -> dict:
        """
        Extract song features from raw audio bytes (e.g., HTTP upload).
        Writes to a temporary file, calls MusicExtractor, then cleans up.
        """
        tmp_file = None
        try:
            try:
                # Create temp file in /tmp
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                tmp_file.write(audio_bytes)
                tmp_file.flush()
                tmp_file.close()
            except Exception as e:
                raise TempFileWritingError("Failed to write audio to temp file") from e

            # Run MusicExtractor
            try:
                features, _ = self.extractor(tmp_file.name)
            except Exception as e:
                raise EssentiaExtractorError("Failed to extract song features by Essentia", song_path={tmp_file.name}) from e

            return self.__pool_to_dict(features)

        finally:
            # Cleanup temp file
            if tmp_file and os.path.exists(tmp_file.name):
                os.remove(tmp_file.name)

    def extract_from_file(self, filepath: str) -> dict:
        """
        Extract song features directly from an existing file path.
        """
        features, _ = self.extractor(filepath)
        return self.__pool_to_dict(features)
