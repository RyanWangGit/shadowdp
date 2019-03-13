class NoAnnotationError(ValueError):
    def __init__(self, lineno, message):
        self.lineno = lineno
        self.message = message
