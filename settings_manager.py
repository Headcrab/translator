import json
import os


class SettingsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.settings_file = os.path.join(
                os.path.dirname(__file__), "settings.json"
            )
            self.settings = self._load_settings()
            self.initialized = True

    def _load_settings(self):
        """Загружает настройки из файла. Если файл не существует, создает его с дефолтными настройками."""
        default_settings = {
            "window": {"x": 100, "y": 100, "width": 800, "height": 600},
            "hotkey": {"modifiers": ["win"], "key": "C"},
            "behavior": {"start_minimized": False, "minimize_to_tray_on_close": True},
            "languages": {"available": ["en", "ru", "kk"], "current": "ru"},
            "models": {
                "available": [],
                "current": None,
                "system_prompt": "Ты профессиональный переводчик..."
            },
            "theme": {"mode": "system"},  # Возможные значения: "light", "dark", "system"
            "appearance": {  # Переносим настройки шрифта в отдельную секцию
                "font_family": "Arial",
                "font_size": 12
            }
        }

        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return default_settings
        except Exception as e:
            print(f"Ошибка при загрузке настроек: {e}")
            return default_settings

    def save_settings(self):
        """Сохраняет текущие настройки в файл."""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {e}")

    def get_window_geometry(self):
        """Возвращает геометрию окна."""
        window = self.settings.get("window", {})
        return (
            window.get("x", 100),
            window.get("y", 100),
            window.get("width", 800),
            window.get("height", 600),
        )

    def set_window_geometry(self, x, y, width, height):
        """Устанавливает геометрию окна."""
        self.settings["window"] = {"x": x, "y": y, "width": width, "height": height}
        self.save_settings()

    def get_hotkey(self):
        """Возвращает настройки горячих клавиш."""
        hotkey = self.settings.get("hotkey", {})
        return (hotkey.get("modifiers", ["win"]), hotkey.get("key", "C"))

    def set_hotkey(self, modifiers, key):
        """Устанавливает настройки горячих клавиш."""
        self.settings["hotkey"] = {"modifiers": modifiers, "key": key}
        self.save_settings()

    def get_behavior(self):
        """Возвращает настройки поведения."""
        behavior = self.settings.get("behavior", {})
        return (
            behavior.get("start_minimized", False),
            behavior.get("minimize_to_tray_on_close", True),
        )

    def set_behavior(self, start_minimized, minimize_to_tray_on_close):
        """Устанавливает настройки поведения."""
        self.settings["behavior"] = {
            "start_minimized": start_minimized,
            "minimize_to_tray_on_close": minimize_to_tray_on_close,
        }
        self.save_settings()

    def get_languages(self):
        """Возвращает список доступных языков и текущий язык."""
        languages = self.settings.get("languages", {})
        return (
            languages.get("available", ["en", "ru", "kk"]),
            languages.get("current", "ru"),
        )

    def set_current_language(self, language):
        """Устанавливает текущий язык."""
        if "languages" not in self.settings:
            self.settings["languages"] = {
                "available": ["en", "ru", "kk"],
                "current": language,
            }
        else:
            self.settings["languages"]["current"] = language
        self.save_settings()

    def set_available_languages(self, languages):
        """Устанавливает список доступных языков."""
        if "languages" not in self.settings:
            self.settings["languages"] = {
                "available": languages,
                "current": languages[0] if languages else "ru",
            }
        else:
            self.settings["languages"]["available"] = languages
            # Если текущий язык больше не в списке доступных, меняем на первый доступный
            if self.settings["languages"]["current"] not in languages:
                self.settings["languages"]["current"] = (
                    languages[0] if languages else "ru"
                )
        self.save_settings()

    def get_models(self):
        """Возвращает список доступных моделей и текущую модель."""
        models = self.settings.get("models", {}).get("available", [])
        current_model_name = self.settings.get("models", {}).get("current")
        
        # Находим текущую модель по имени
        current_model = next(
            (model for model in models if model["name"] == current_model_name),
            None
        )
        
        return models, current_model  # Возвращаем список моделей и объект текущей

    def add_model(self, name, provider, api_endpoint, model_name, access_token, streaming=False):
        """Добавляет новую модель в список доступных."""
        if "models" not in self.settings:
            self.settings["models"] = {"available": [], "current": None}

        model = {
            "name": name,
            "provider": provider,
            "api_endpoint": api_endpoint,
            "model_name": model_name,
            "access_token": access_token,
            "streaming": streaming  # Убедимся, что streaming сохраняется
        }

        # Проверяем, существует ли модель с таким именем
        existing_model_index = next(
            (i for i, m in enumerate(self.settings["models"]["available"]) if m["name"] == name),
            None
        )

        if existing_model_index is not None:
            # Обновляем существующую модель
            self.settings["models"]["available"][existing_model_index] = model
        else:
            # Добавляем новую модель
            self.settings["models"]["available"].append(model)

        # Если текущая модель не выбрана, устанавливаем новую модель как текущую
        if not self.settings["models"]["current"]:
            self.settings["models"]["current"] = name

        self.save_settings()

    def remove_model(self, name):
        """Удаляет модель из списка доступных."""
        if "models" in self.settings:
            self.settings["models"]["available"] = [
                model
                for model in self.settings["models"]["available"]
                if model["name"] != name
            ]
            # Если удалили текущую модель, сбрасываем выбор
            if self.settings["models"]["current"] == name:
                self.settings["models"]["current"] = (
                    self.settings["models"]["available"][0]["name"]
                    if self.settings["models"]["available"]
                    else None
                )
            self.save_settings()

    def set_current_model(self, name):
        """Устанавливает текущую модель."""
        if "models" in self.settings:
            # Проверяем, существует ли модель с таким именем
            if any(
                model["name"] == name for model in self.settings["models"]["available"]
            ):
                self.settings["models"]["current"] = name
                self.save_settings()

    def set_model_access_token(self, model_name, access_token):
        """Устанавливает токен доступа для указанной модели."""
        if "models" in self.settings:
            for model in self.settings["models"]["available"]:
                if model["name"] == model_name:
                    model["access_token"] = access_token
                    self.save_settings()
                    break

    def get_model_info(self, model_name=None):
        """Возвращает информацию о модели.

        Args:
            model_name: Имя модели. Если не указано, возвращает информацию о текущей модели.

        Returns:
            dict: Информация о модели (name, provider, api_endpoint, model_name, access_token)
            или None, если модель не найдена
        """
        if "models" not in self.settings:
            return None

        if model_name is None:
            model_name = self.settings["models"].get("current")
            if model_name is None:
                return None

        for model in self.settings["models"]["available"]:
            if model["name"] == model_name:
                return model.copy()  # Возвращаем копию, чтобы избежать случайных изменений

        return None

    def get_theme(self):
        """Возвращает текущую тему.

        Returns:
            str: Режим темы ('light', 'dark' или 'system')
        """
        return self.settings.get("theme", {}).get("mode", "system")

    def set_theme(self, mode):
        """Устанавливает тему.

        Args:
            mode: Режим темы ('light', 'dark' или 'system')
        """
        if mode not in ["light", "dark", "system"]:
            raise ValueError("Недопустимый режим темы")
        
        if "theme" not in self.settings:
            self.settings["theme"] = {}
        
        self.settings["theme"]["mode"] = mode
        self.save_settings()

    def add_language(self, language):
        """Добавляет новый язык в список доступных."""
        if "languages" not in self.settings:
            self.settings["languages"] = {
                "available": [language],
                "current": language
            }
        else:
            if language not in self.settings["languages"]["available"]:
                self.settings["languages"]["available"].append(language)
        self.save_settings()

    def edit_language(self, old_language, new_language):
        """Редактирует существующий язык."""
        if "languages" in self.settings:
            if old_language in self.settings["languages"]["available"]:
                index = self.settings["languages"]["available"].index(old_language)
                self.settings["languages"]["available"][index] = new_language
                
                # Если редактируем текущий язык, обновляем его
                if self.settings["languages"]["current"] == old_language:
                    self.settings["languages"]["current"] = new_language
                    
                self.save_settings()

    def delete_language(self, language):
        """Удаляет язык из списка доступных."""
        if "languages" in self.settings:
            if language in self.settings["languages"]["available"]:
                self.settings["languages"]["available"].remove(language)
                
                # Если удаляем текущий язык, меняем на первый доступный
                if self.settings["languages"]["current"] == language:
                    self.settings["languages"]["current"] = (
                        self.settings["languages"]["available"][0]
                        if self.settings["languages"]["available"]
                        else "ru"
                    )
                    
                self.save_settings()

    def get_system_prompt(self) -> str:
        prompt = self.settings.get("system_prompt", "")
        # Защита от пустого промпта
        return prompt or "Ты профессиональный переводчик. Переведи текст на {language}."
    
    def set_system_prompt(self, prompt):
        self.settings['system_prompt'] = prompt
        self.save_settings()

    def get_settings_window_geometry(self):
        """Возвращает сохраненную геометрию окна настроек."""
        return self.settings.get("settings_window_geometry", (100, 100, 400, 300))

    def set_settings_window_geometry(self, x, y, width, height):
        """Сохраняет геометрию окна настроек."""
        self.settings["settings_window_geometry"] = (x, y, width, height)
        self.save_settings()

    def get_font_settings(self):
        return {
            "font_family": self.settings.get("appearance", {}).get("font_family", "Cascadia Code"),
            "font_size": self.settings.get("appearance", {}).get("font_size", 12)
        }

    def save_font_settings(self, font_family, font_size):
        if "appearance" not in self.settings:
            self.settings["appearance"] = {}
        self.settings["appearance"]["font_family"] = font_family
        self.settings["appearance"]["font_size"] = font_size
        self.save_settings()
