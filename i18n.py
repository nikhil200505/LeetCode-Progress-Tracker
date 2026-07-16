"""Утилита для интернационализации."""

import json
import os
from typing import Dict, Any


class I18n:
    """Класс для работы с переводами."""

    def __init__(self, locales_dir: str = "locales"):
        self.locales_dir = locales_dir
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.current_language = "ru"
        self.supported_languages = ["ru", "en"]
        self.load_translations()

    def load_translations(self):
        """Загружает переводы из JSON файлов."""
        for lang in self.supported_languages:
            file_path = os.path.join(self.locales_dir, f"{lang}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)

    def set_language(self, language: str):
        """Устанавливает текущий язык."""
        if language in self.supported_languages:
            self.current_language = language

    def get_language(self) -> str:
        """Возвращает текущий язык."""
        return self.current_language

    def translate(self, key: str, language: str = None) -> str:
        """
        Переводит ключ на указанный язык.

        Args:
            key: Ключ перевода в формате "section.subsection.key"
            language: Язык перевода (если не указан, используется текущий)

        Returns:
            Переведенная строка или исходный ключ, если перевод не найден
        """
        lang = language or self.current_language

        if lang not in self.translations:
            return key

        # Получаем перевод по вложенному ключу
        translation = self.translations[lang]
        keys = key.split('.')

        try:
            for k in keys:
                translation = translation[k]
            return translation
        except (KeyError, TypeError):
            # Если перевод не найден, возвращаем исходный ключ
            return key

    def get_all_translations(self, language: str = None) -> Dict[str, Any]:
        """Возвращает все переводы для указанного языка."""
        lang = language or self.current_language
        return self.translations.get(lang, {})

    def get_supported_languages(self) -> list:
        """Возвращает список поддерживаемых языков."""
        return self.supported_languages


# Создаем глобальный экземпляр
i18n = I18n()
