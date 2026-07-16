"""Утилиты для LeetCode Progress Tracker."""


def get_latest_value(dataframe, username):
    """Получить последнее значение для пользователя из DataFrame.

    Args:
        dataframe: pandas DataFrame с данными
        username: имя пользователя для поиска в колонках

    Returns:
        int: Последнее значение для пользователя или 0 если данных нет
    """
    if (dataframe.empty or
        username not in dataframe.columns or
            dataframe[username].dropna().empty):
        return 0
    return dataframe[username].dropna().iloc[-1]
