"""
Модуль для сохранения и загрузки настроек GUI приложения
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """
    Менеджер конфигурации для GUI приложения
    Сохраняет настройки в JSON файл в домашней директории пользователя
    """

    def __init__(self, app_name: str = "giis-signer"):
        """
        Инициализация конфигурации

        Args:
            app_name: Имя приложения для создания директории конфига
        """
        self.app_name = app_name
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        self._config: Dict[str, Any] = {}
        self.load()

    def _get_config_dir(self) -> Path:
        """Получить директорию для хранения конфигурации"""
        # Для Windows используем %APPDATA%
        if os.name == 'nt':
            base_dir = Path(os.getenv('APPDATA', Path.home()))
        else:
            # Для Linux/macOS используем ~/.config
            base_dir = Path.home() / ".config"

        config_dir = base_dir / self.app_name

        # Создаем директорию если не существует
        config_dir.mkdir(parents=True, exist_ok=True)

        return config_dir

    def load(self) -> None:
        """Загрузить конфигурацию из файла"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except Exception as e:
                print(f"Ошибка при загрузке конфигурации: {e}")
                self._config = {}
        else:
            self._config = {}

    def save(self) -> None:
        """Сохранить конфигурацию в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении конфигурации: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Получить значение по ключу

        Args:
            key: Ключ настройки
            default: Значение по умолчанию

        Returns:
            Значение настройки или default
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Установить значение по ключу

        Args:
            key: Ключ настройки
            value: Значение настройки
        """
        self._config[key] = value
        self.save()

    def get_last_certificate_thumbprint(self) -> Optional[str]:
        """Получить отпечаток последнего использованного сертификата"""
        return self.get("last_certificate_thumbprint")

    def set_last_certificate_thumbprint(self, thumbprint: str) -> None:
        """Сохранить отпечаток последнего использованного сертификата"""
        self.set("last_certificate_thumbprint", thumbprint)

    def get_window_geometry(self) -> Optional[str]:
        """Получить сохраненную геометрию окна"""
        return self.get("window_geometry")

    def set_window_geometry(self, geometry: str) -> None:
        """Сохранить геометрию окна"""
        self.set("window_geometry", geometry)

    def get_theme(self) -> str:
        """Получить тему оформления (dark/light/system)"""
        return self.get("theme", "system")

    def set_theme(self, theme: str) -> None:
        """Сохранить тему оформления"""
        self.set("theme", theme)

    def get_last_input_dir(self) -> Optional[str]:
        """Получить последнюю использованную директорию для входных файлов"""
        return self.get("last_input_dir")

    def set_last_input_dir(self, directory: str) -> None:
        """Сохранить последнюю использованную директорию для входных файлов"""
        self.set("last_input_dir", directory)

    def get_last_output_dir(self) -> Optional[str]:
        """Получить последнюю использованную директорию для выходных файлов"""
        return self.get("last_output_dir")

    def set_last_output_dir(self, directory: str) -> None:
        """Сохранить последнюю использованную директорию для выходных файлов"""
        self.set("last_output_dir", directory)

    def clear(self) -> None:
        """Очистить всю конфигурацию"""
        self._config = {}
        self.save()
