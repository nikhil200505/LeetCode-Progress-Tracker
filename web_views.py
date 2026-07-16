"""Веб-страницы для LeetCode Progress Tracker."""

from fastapi import Request, APIRouter, Cookie
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from modules.data_processor import load_and_process_data
from modules.utils import get_latest_value
from modules.i18n import i18n
from config import USERNAMES

templates = Jinja2Templates(directory="templates")


# Создаем роутер для веб-страниц
web_router = APIRouter()


@web_router.get("/", response_class=HTMLResponse)
async def index(request: Request, lang: str = Cookie(default="ru")):
    """Главная страница с графиками."""
    # Устанавливаем язык из cookie
    i18n.set_language(lang if lang in i18n.get_supported_languages() else "ru")

    try:
        data_dict = load_and_process_data()

        # Получаем статистику
        stats = []
        for username in USERNAMES:
            if username in data_dict['total'].columns:
                latest_total = get_latest_value(data_dict['total'], username)
                latest_progress = get_latest_value(
                    data_dict['progress_total'], username)

                # Детальная статистика по сложности, если доступна
                latest_easy = get_latest_value(data_dict['easy'], username)
                latest_medium = get_latest_value(data_dict['medium'], username)
                latest_hard = get_latest_value(data_dict['hard'], username)

                stats.append({
                    'username': username,
                    'total': int(latest_total),
                    'progress': int(latest_progress),
                    'easy': int(latest_easy),
                    'medium': int(latest_medium),
                    'hard': int(latest_hard)
                })
            else:
                stats.append({
                    'username': username,
                    'total': 0,
                    'progress': 0,
                    'easy': 0,
                    'medium': 0,
                    'hard': 0
                })

        # Добавляем прогресс по сложности в статистику
        for stat in stats:
            easy_progress = int(
                get_latest_value(
                    data_dict['progress_easy'],
                    stat['username']))
            medium_progress = int(
                get_latest_value(
                    data_dict['progress_medium'],
                    stat['username']))
            hard_progress = int(
                get_latest_value(
                    data_dict['progress_hard'],
                    stat['username']))

            stat['easy_progress'] = easy_progress
            stat['medium_progress'] = medium_progress
            stat['hard_progress'] = hard_progress

        # Последнее обновление
        if not data_dict['total'].empty:
            last_update = data_dict['total'].index[-1].strftime(
                '%Y-%m-%d %H:%M:%S')
        else:
            last_update = i18n.translate("errors.no_data")

        return templates.TemplateResponse("index.html", {
            "request": request,
            "stats": stats,
            "last_update": last_update,
            "has_difficulty_data": (not data_dict['easy'].empty or
                                    not data_dict['medium'].empty or
                                    not data_dict['hard'].empty),
            "translations": i18n.get_all_translations(),
            "current_language": i18n.get_language(),
            "supported_languages": i18n.get_supported_languages()
        })

    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": f"{i18n.translate('errors.loading_error')} {str(e)}",
            "suggestion": i18n.translate("errors.suggestion"),
            "translations": i18n.get_all_translations(),
            "current_language": i18n.get_language()
        })
