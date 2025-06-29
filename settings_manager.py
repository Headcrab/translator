import json
import os
import sys


class SettingsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            # Получить путь к файлу настроек через путь запуска программы
            self.settings_file = os.path.join(
                os.path.dirname(sys.argv[0]), "settings.json"
            )
            self.settings = self._load_settings()
            self.initialized = True

    def _load_settings(self):
        """Загружает настройки из файла. Если файл не существует, создает его с дефолтными настройками."""
        default_settings = {
            "window": {"x": 100, "y": 100, "width": 800, "height": 600},
            "settings_window": {
                "x": 150,
                "y": 150,
                "width": 800,
                "height": 600,
            },
            "providers": {
                "OpenAI": {
                    "access_token_env": "OPENAI_API_KEY",
                    "api_endpoint": "https://api.openai.com/v1/chat/completions",
                },
                "Anthropic": {
                    "access_token_env": "ANTHROPIC_API_KEY",
                    "api_endpoint": "https://api.anthropic.com/v1/messages",
                },
                "Google": {"access_token_env": "GOOGLE_API_KEY", "api_endpoint": ""},
                "OpenRouter": {
                    "access_token_env": "OPENROUTER_API_KEY",
                    "api_endpoint": "https://openrouter.ai/api/v1/chat/completions",
                },
                "Cerebras": {
                    "access_token_env": "CEREBRAS_API_KEY",
                    "api_endpoint": "https://api.cerebras.ai/v1",
                },
                "Nebius": {
                    "access_token_env": "NEBIUS_API_KEY",
                    "api_endpoint": "https://api.studio.nebius.ai/v1/",
                },
            },
            "languages": {
                "available": ["Русский", "English", "Deutsch", "Français", "Español"],
                "current": "English",
            },
            "models": {"available": [], "current": None},
            "prompts": {
                "available": [
                    {
                        "name": "Базовый",
                        "text": "Переведи следующий текст на указанный язык, сохраняя стиль и тон оригинала.",
                    },
                    {
                        "name": "Формальный",
                        "text": "Переведи следующий текст на указанный язык, используя формальный стиль и деловой тон.",
                    },
                    {
                        "name": "Разговорный",
                        "text": "Переведи следующий текст на указанный язык, используя разговорный стиль и неформальный тон.",
                    },
                ],
                "current": None,
            },
            "hotkey": {"modifiers": ["ctrl", "shift"], "key": "T"},
            "behavior": {"start_minimized": False, "minimize_to_tray_on_close": True},
            "theme": {"mode": "system"},
            "font": {"family": "Arial", "size": 12},
        }

        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)
                    # Обновляем дефолтные настройки загруженными
                    self._update_dict_recursively(default_settings, loaded_settings)
                    return default_settings
            return default_settings
        except Exception as e:
            print(f"Ошибка при загрузке настроек: {e}")
            return default_settings

    def _update_dict_recursively(self, target, source):
        """Рекурсивно обновляет словарь, сохраняя структуру и дефолтные значения."""
        for key, value in source.items():
            if key in target:
                if isinstance(value, dict) and isinstance(target[key], dict):
                    self._update_dict_recursively(target[key], value)
                else:
                    target[key] = value

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
        models_config = self.settings.get("models", {}).get("available", [])
        current_model_config = self.settings.get("models", {}).get("current")

        hydrated_models = []
        for model_conf in models_config:
            provider_name = model_conf["provider"]
            provider_settings = self.get_provider_settings(provider_name)

            # Получаем токен доступа из переменных окружения
            access_token_env = provider_settings.get("access_token_env", "")
            access_token = ""
            if access_token_env:
                access_token = os.getenv(access_token_env, "")

            hydrated_model = {
                **model_conf,
                "name": f"{model_conf['model_name']} - {provider_name}",
                "api_endpoint": provider_settings.get("api_endpoint", ""),
                "access_token_env": access_token_env,
                "access_token": access_token,
            }
            hydrated_models.append(hydrated_model)

        current_model = None
        if current_model_config:
            current_model = next(
                (
                    m
                    for m in hydrated_models
                    if m["provider"] == current_model_config["provider"]
                    and m["model_name"] == current_model_config["model_name"]
                ),
                None,
            )

        return hydrated_models, current_model

    def add_model(self, provider, model_name, streaming=False):
        """Добавляет новую модель в список доступных."""
        if "models" not in self.settings:
            self.settings["models"] = {"available": [], "current": None}

        model = {"provider": provider, "model_name": model_name, "streaming": streaming}

        # Проверяем, существует ли модель с таким именем
        existing_model = next(
            (
                m
                for m in self.settings["models"]["available"]
                if m["provider"] == provider and m["model_name"] == model_name
            ),
            None,
        )

        if not existing_model:
            self.settings["models"]["available"].append(model)

        # Если текущая модель не выбрана, устанавливаем новую модель как текущую
        if not self.settings["models"]["current"]:
            self.settings["models"]["current"] = {
                "provider": provider,
                "model_name": model_name,
            }

        self.save_settings()

    def remove_model(self, provider, model_name):
        """Удаляет модель из списка доступных."""
        if "models" in self.settings:
            self.settings["models"]["available"] = [
                m
                for m in self.settings["models"]["available"]
                if not (m["provider"] == provider and m["model_name"] == model_name)
            ]

            current = self.settings["models"].get("current")
            if (
                current
                and current["provider"] == provider
                and current["model_name"] == model_name
            ):
                available = self.settings["models"]["available"]
                self.settings["models"]["current"] = available[0] if available else None

            self.save_settings()

    def set_current_model(self, provider, model_name):
        """Устанавливает текущую модель."""
        if "models" in self.settings:
            # Проверяем, существует ли модель с таким именем
            if any(
                m["provider"] == provider and m["model_name"] == model_name
                for m in self.settings["models"]["available"]
            ):
                self.settings["models"]["current"] = {
                    "provider": provider,
                    "model_name": model_name,
                }
                self.save_settings()

    def set_model_access_token(self, model_name, access_token):
        """Устанавливает токен доступа для указанной модели."""
        if "models" in self.settings:
            for model in self.settings["models"]["available"]:
                if model["name"] == model_name:
                    model["access_token"] = access_token
                    self.save_settings()
                    break

    def get_model_info(self, provider=None, model_name=None):
        """Возвращает информацию о модели, включая ключ API из настроек провайдера."""
        if provider is None or model_name is None:
            current_config = self.settings.get("models", {}).get("current")
            if not current_config:
                available = self.settings.get("models", {}).get("available", [])
                if not available:
                    return None
                current_config = available[0]

            provider = current_config["provider"]
            model_name = current_config["model_name"]

        models, _ = self.get_models()
        model_info = next(
            (
                m
                for m in models
                if m["provider"] == provider and m["model_name"] == model_name
            ),
            None,
        )

        if model_info:
            access_token_env = model_info.get("access_token_env", "")
            if access_token_env:
                access_token = os.getenv(access_token_env, "")
                model_info["access_token"] = access_token
            else:
                model_info["access_token"] = ""

        return model_info

    def get_theme(self):
        """Возвращает настройки темы."""
        theme = self.settings.get("theme", {})
        return theme.get("mode", "system")

    def set_theme(self, mode):
        """Устанавливает настройки темы."""
        self.settings["theme"] = {"mode": mode}
        self.save_settings()

    def get_provider_settings(self, provider_name):
        """Возвращает настройки для конкретного провайдера."""
        return self.settings.get("providers", {}).get(provider_name, {})

    def set_provider_settings(self, provider_name, access_token_env, api_endpoint):
        """Устанавливает переменную окружения и endpoint для провайдера."""
        if "providers" not in self.settings:
            self.settings["providers"] = {}
        if provider_name not in self.settings["providers"]:
            self.settings["providers"][provider_name] = {}
        self.settings["providers"][provider_name]["access_token_env"] = access_token_env
        self.settings["providers"][provider_name]["api_endpoint"] = api_endpoint
        self.save_settings()

    def add_language(self, language):
        """Добавляет новый язык в список доступных."""
        if "languages" not in self.settings:
            self.settings["languages"] = {"available": [language], "current": language}
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
        self.settings["system_prompt"] = prompt
        self.save_settings()

    def get_settings_window_geometry(self):
        """Возвращает сохраненную геометрию окна настроек."""
        win = self.settings.get("settings_window", {})
        return (
            win.get("x", 100),
            win.get("y", 100),
            win.get("width", 400),
            win.get("height", 300),
        )

    def set_settings_window_geometry(self, x, y, width, height):
        """Сохраняет геометрию окна настроек."""
        self.settings["settings_window"] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        }
        self.save_settings()

    def get_font_settings(self):
        """Получает настройки шрифта."""
        appearance = self.settings.get("font", {})
        return {
            "font_family": appearance.get("family", "Arial"),
            "font_size": int(appearance.get("size", 12)),
        }

    def save_font_settings(self, font_family, font_size):
        """Сохраняет настройки шрифта."""
        if not isinstance(font_size, int):
            try:
                font_size = int(font_size)
            except (ValueError, TypeError):
                font_size = 12

        if "font" not in self.settings:
            self.settings["font"] = {}

        self.settings["font"].update({"family": font_family, "size": font_size})

        self.save_settings()

    def get_prompts(self):
        """Возвращает список доступных промптов и текущий промпт."""
        return (
            self.settings["prompts"]["available"],
            self.settings["prompts"]["current"],
        )

    def get_prompt_info(self, name=None):
        """Возвращает информацию о промпте по имени."""
        if not name and self.settings["prompts"]["current"]:
            return self.settings["prompts"]["current"]

        for prompt in self.settings["prompts"]["available"]:
            if prompt["name"] == name:
                return prompt
        return None

    def add_prompt(self, name, text):
        """Добавляет новый системный промпт."""
        prompt = {"name": name, "text": text}
        self.settings["prompts"]["available"].append(prompt)
        if not self.settings["prompts"]["current"]:
            self.settings["prompts"]["current"] = prompt
        self.save_settings()

    def edit_prompt(self, old_name, new_name, text):
        """Редактирует существующий системный промпт."""
        for prompt in self.settings["prompts"]["available"]:
            if prompt["name"] == old_name:
                prompt["name"] = new_name
                prompt["text"] = text
                if (
                    self.settings["prompts"]["current"]
                    and self.settings["prompts"]["current"]["name"] == old_name
                ):
                    self.settings["prompts"]["current"] = prompt
                break
        self.save_settings()

    def delete_prompt(self, name):
        """Удаляет системный промпт."""
        self.settings["prompts"]["available"] = [
            p for p in self.settings["prompts"]["available"] if p["name"] != name
        ]

        if (
            self.settings["prompts"]["current"]
            and self.settings["prompts"]["current"]["name"] == name
        ):
            if self.settings["prompts"]["available"]:
                self.settings["prompts"]["current"] = self.settings["prompts"][
                    "available"
                ][0]
            else:
                self.settings["prompts"]["current"] = None

        self.save_settings()

    def set_current_prompt(self, name):
        """Устанавливает текущий системный промпт."""
        for prompt in self.settings["prompts"]["available"]:
            if prompt["name"] == name:
                self.settings["prompts"]["current"] = prompt
                self.save_settings()
                break
