# Конфигурационный файл для скрипта отслеживания прогресса LeetCode

# --- ПОЛЬЗОВАТЕЛИ ---
# Укажите юзернеймы на LeetCode. Можете добавлять или убирать людей,
# скрипт адаптируется автоматически.
USERNAMES = ["iris0o", "NG7"]

# --- ФАЙЛЫ ---
# Имя файла для хранения данных
CSV_FILE = "leetcode_progress.csv"
# Имя файла для графика
PLOT_FILE = "leetcode_progress.png"

# --- НАСТРОЙКИ ЗАПРОСОВ ---
# Таймаут для HTTP запросов (секунды)
REQUEST_TIMEOUT = 10

# --- НАСТРОЙКИ ГРАФИКА ---
# Размер фигуры
FIGURE_SIZE = (14, 8)
# Стиль графика
PLOT_STYLE = 'seaborn-v0_8-darkgrid'
# Размер маркеров
MARKER_SIZE = 4
# Размер шрифта заголовка
TITLE_FONT_SIZE = 18
# Размер шрифта осей
AXIS_FONT_SIZE = 12
# Размер шрифта легенды
LEGEND_FONT_SIZE = 10

# --- НАСТРОЙКИ CSV ---
CSV_ENCODING = 'utf-8'

# --- URL И ЗАПРОСЫ ---
LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"
USER_PROFILE_QUERY = """
    query getUserProfile($username: String!) {
      matchedUser(username: $username) {
        submitStats: submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
    }
    """