class ChatSessionNotFoundError(Exception):
    pass


class ChatPromptLimitError(Exception):
    pass


class ChatAssistantUnavailableError(Exception):
    pass


class ChatSessionBusyError(Exception):
    pass