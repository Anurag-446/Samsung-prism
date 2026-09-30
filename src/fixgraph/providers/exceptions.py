class ProviderError(Exception):
    pass

class ProviderTimeoutError(ProviderError):
    pass

class ProviderResponseError(ProviderError):
    pass

class EmbedderInitializationError(ProviderError):
    pass
