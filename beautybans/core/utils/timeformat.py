def format_minutes(total_minutes):
    """
    Конвертирует минуты в читаемый формат.
    Примеры:
        136   -> "2 ч. 16 мин."
        11656 -> "1 нед. 1 д. 2 ч. 16 мин."
    """
    if not total_minutes or total_minutes <= 0:
        return '0 мин.'

    units = [
        ('г.', 525600),   # год = 365 дней
        ('мес.', 43200),  # месяц = 30 дней
        ('нед.', 10080),  # неделя = 7 дней
        ('д.', 1440),     # день
        ('ч.', 60),       # час
        ('мин.', 1),      # минута
    ]

    parts = []
    remaining = int(total_minutes)
    for name, unit_minutes in units:
        if remaining >= unit_minutes:
            value = remaining // unit_minutes
            remaining = remaining % unit_minutes
            parts.append(f'{value} {name}')

    return ' '.join(parts)
