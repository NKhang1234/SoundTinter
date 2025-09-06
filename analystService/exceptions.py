class EssentiaExtractorError(Exception):
    """Raised when Essentia fails to extract audio features."""
    def __init__(self, message: str, song_path: str = None):
        super().__init__(message)
        self.song_path = song_path

class TempFileWritingError(Exception):
    """Raised when failed to write audio to temp file"""
    def __init__(self, message: str):
        super().__init__(message)

class FileReadError(Exception):
    """Raised when failed to read audio"""
    def __init__(self, message: str):
        super().__init__(message)