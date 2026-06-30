def verify_server_if_needed(server):
    """
    Автоматически верифицирует сервер при первом API запросе

    Использует update_fields для минимальной нагрузки - обновляет только is_verified.
    Проверка if выполняется в памяти без дополнительного запроса к БД.

    Args:
        server: экземпляр модели Server (уже загружен из БД)

    Returns:
        bool: True если сервер был верифицирован, False если уже был верифицирован
    """
    if not server.is_verified:
        server.is_verified = True
        server.save(update_fields=['is_verified'])
        return True
    return False
