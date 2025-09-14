import tempfile
import os
import essentia.standard as es
from exceptions import EssentiaExtractorError, TempFileWritingError
import json
from decimal import Decimal

class EssentiaExtractor:
    def __init__(self):
        self.extractor = es.MusicExtractor(lowlevelStats=['mean', 'stdev'])

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
        def convert_value(value):
            if isinstance(value, float):
                return Decimal(str(value))
            elif isinstance(value, (list, tuple)):
                return [convert_value(x) for x in value]
            elif hasattr(value, "tolist"):
                return convert_value(value.tolist())
            else:
                return value

        result = {}
        for key in pool.descriptorNames():
            if key in self.allowed_features: # Filter only neccessary features
                value = pool[key]
                result[key] = convert_value(value)
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
