class DailyTrackerError(Exception):
    """Базовое исключение приложения"""
    pass

class DataValidationError(DailyTrackerError):
    """Ошибка валидации данных"""
    pass

class FileOperationError(DailyTrackerError):
    """Ошибка операций с файлами"""
    pass

class TemplateError(DailyTrackerError):
    """Ошибка работы с шаблонами"""
    pass

class ProjectNotFoundError(DailyTrackerError):
    """Проект не найден"""
    pass

class DayNotFoundError(DailyTrackerError):
    """День не найден"""
    pass