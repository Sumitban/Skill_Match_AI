

class ResumeExtractionError(Exception):
    pass

class ResumeFileNotFound(ResumeExtractionError):
    pass

class ResumeFileEmpty(ResumeExtractionError):
    pass

class ResumeCorrupted(ResumeExtractionError):
    pass

class InvalidTextInputError(ResumeExtractionError):
    pass

class LinkExtractionError(ResumeExtractionError):
    pass

class ResumeEncryptError(ResumeExtractionError):
    pass

class ResumeTextEmpty(ResumeExtractionError):
    pass