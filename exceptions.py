class OpenAiAccessError(Exception):
    pass

class NoTranscriptedVoiceToTextError(Exception):
    pass

class FileNotFoundInVoiceFilesDir(Exception):
    pass

class HTTPResponseParsingError(Exception):
    pass

class AiAccessException(Exception):
    pass