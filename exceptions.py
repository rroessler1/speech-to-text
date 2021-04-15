class STTError(Exception):
    def __init__(self, message, show_settings=False):
        super().__init__(message)
        self.show_settings = show_settings
