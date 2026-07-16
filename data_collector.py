import requests
from datetime import datetime
import os
import csv
from config import (
    USERNAMES, CSV_FILE, REQUEST_TIMEOUT,
    CSV_ENCODING, LEETCODE_GRAPHQL_URL, USER_PROFILE_QUERY
)


def get_leetcode_stats(username):
    """Получает статистику решенных задач для пользователя по уровням сложности."""
    variables = {"username": username}
    payload = {"query": USER_PROFILE_QUERY, "variables": variables}

    try:
        response = requests.post(
            LEETCODE_GRAPHQL_URL,
            json=payload,
            timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if data.get("data", {}).get("matchedUser") is None:
            print(f"Ошибка: Пользователь '{username}' не найден.")
            return None

        stats = data["data"]["matchedUser"]["submitStats"]["acSubmissionNum"]

        # Извлекаем данные по уровням сложности
        result = {
            'total': 0,
            'easy': 0,
            'medium': 0,
            'hard': 0
        }

        for item in stats:
            difficulty = item['difficulty'].lower()
            count = item['count']

            if difficulty == 'all':
                result['total'] = count
            elif difficulty == 'easy':
                result['easy'] = count
            elif difficulty == 'medium':
                result['medium'] = count
            elif difficulty == 'hard':
                result['hard'] = count

        return result
    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети при запросе для {username}: {e}")
        return None
    except Exception as e:
        print(f"Произошла ошибка при обработке данных для {username}: {e}")
        return None


def update_progress_data():
    """Добавляет новые замеры в CSV файл в "длинном" формате."""
    # Проверяем, существует ли файл, и если нет - создаем с заголовками
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding=CSV_ENCODING) as f:
            writer = csv.writer(f)
            # Новые заголовки с детализацией по сложности
            headers = [
                'timestamp',
                'username',
                'total_solved',
                'easy_solved',
                'medium_solved',
                'hard_solved']
            writer.writerow(headers)

    # Открываем файл для добавления данных
    with open(CSV_FILE, 'a', newline='', encoding=CSV_ENCODING) as f:
        writer = csv.writer(f)
        now_iso = datetime.now().isoformat()

        print("-" * 30)
        print(
            f"Запуск обновления данных: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        for username in USERNAMES:
            stats = get_leetcode_stats(username)
            if stats is not None:
                writer.writerow([
                    now_iso, username,
                    stats['total'], stats['easy'], stats['medium'], stats['hard']
                ])
                print(
                    f"  - {username}: {stats['total']} задач (E:{stats['easy']}, M:{stats['medium']}, H:{stats['hard']}). Запись добавлена.")
            else:
                print(f"  - {username}: не удалось получить данные.")
        print("-" * 30)


def main():
    """Основная функция для запуска из других модулей."""
    update_progress_data()


if __name__ == "__main__":
    main()
