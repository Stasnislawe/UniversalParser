class ScraperError(Exception):
    """Базовое исключение для ошибок сбора."""
    pass

class NoContainerFound(ScraperError):
    """Контейнер с товарами не найден на странице."""
    pass

class NoFieldsExtracted(ScraperError):
    """Не удалось извлечь ни одного поля из блоков."""
    pass