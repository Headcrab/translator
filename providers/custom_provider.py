"""Кастомный провайдер для работы с произвольными LLM API."""

from typing import Dict, Any, List, AsyncGenerator
from .base_provider import BaseProvider
import aiohttp
import json
import logging
import os

logger = logging.getLogger(__name__)


class CustomProvider(BaseProvider):
    """Провайдер для работы с произвольными LLM API."""

    def __init__(self, model_info: Dict[str, Any]):
        """
        Инициализирует провайдер с информацией о модели.

        Args:
            model_info: Словарь с информацией о модели
        """
        # Сначала получаем токен из переменной окружения, если она указана
        access_token = model_info.get("access_token")
        logger.debug(f"\n=== Access token env name: {access_token}")

        if access_token:
            env_value = os.getenv(access_token)
            logger.debug(f"=== Access token env value exists: {env_value is not None}")
            logger.debug(
                f"=== Access token env value length: {len(env_value) if env_value else 0}"
            )

            if env_value:
                # Если значение получено из переменной окружения, используем его
                model_info["access_token"] = env_value
                logger.debug(f"=== Access token set from env: {env_value[:5]}...")
            else:
                logger.debug(
                    f"=== WARNING: Environment variable {access_token} is not set or empty"
                )

        # Теперь вызываем родительский конструктор с обновленным model_info
        super().__init__(model_info)

        # Убираем жесткое добавление /chat/completions
        self.api_version = None

    def _format_message(self, role: str, content: str) -> Dict[str, Any]:
        """
        Форматирует сообщение в соответствии с форматом API OpenAI.

        Args:
            role: Роль сообщения (system/user/assistant)
            content: Текст сообщения

        Returns:
            Dict[str, Any]: Отформатированное сообщение
        """
        return {"role": role, "content": content}

    async def _detect_api_version(self, headers: Dict[str, str]) -> None:
        """
        Определяет версию API путем тестового запроса.

        Args:
            headers: Заголовки для запроса
        """
        async with aiohttp.ClientSession() as session:
            # Пробуем базовый формат
            data = {
                "model": self.model_info["model_name"],
                "messages": [self._format_message("user", "test")],
                "temperature": 0.3,
                "stream": False,
            }

            async with session.post(
                self.model_info["api_endpoint"], headers=headers, json=data
            ) as response:
                if response.status == 200:
                    self.api_version = "base"
                    return

            # Если базовый формат не работает, пробуем формат GPT-4 Vision
            data["messages"][0]["content"] = [{"type": "text", "text": "test"}]
            async with session.post(
                self.model_info["api_endpoint"], headers=headers, json=data
            ) as response:
                if response.status == 200:
                    self.api_version = "vision"
                    return

            # Если ни один формат не работает, используем базовый
            self.api_version = "base"

    async def _get_headers(self) -> Dict[str, str]:
        """
        Формирует заголовки для запроса к API.

        Returns:
            Dict[str, str]: Заголовки запроса
        """
        headers = {"Content-Type": "application/json"}

        token = self.model_info.get("access_token")
        logger.debug(
            f"\n=== CustomProvider token value: {token[:10]}..."
            if token
            else "[MISSING]"
        )

        if token:
            # Простая логика аутентификации - используем стандартный Bearer токен
            if token.startswith(("Bearer ", "Basic ", "Token ", "Api-Key ")):
                headers["Authorization"] = token
                logger.debug(f"=== Using token with existing prefix: {token[:15]}...")
            else:
                headers["Authorization"] = f"Bearer {token}"
                logger.debug(f"=== Added Bearer prefix: Bearer {token[:10]}...")

        return headers

    async def _prepare_messages(
        self, messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Подготавливает сообщения в соответствии с версией API.

        Args:
            messages: Список сообщений

        Returns:
            List[Dict[str, Any]]: Подготовленные сообщения
        """
        if self.api_version == "vision":
            return [
                {
                    "role": msg["role"],
                    "content": [{"type": "text", "text": msg["content"]}],
                }
                for msg in messages
            ]
        return messages

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Получает список доступных моделей от кастомного API.

        Returns:
            List[Dict[str, Any]]: Список моделей в формате:
            [{"id": "model_id", "name": "Model Name"}]
        """
        # Получаем базовый URL API, убирая /chat/completions
        base_url = self.model_info["api_endpoint"].replace("/chat/completions", "")
        models_url = f"{base_url}/models"

        try:
            async with aiohttp.ClientSession() as session:
                headers = await self._get_headers()
                async with session.get(models_url, headers=headers) as response:
                    if response.status != 200:
                        await self._handle_http_error(
                            response, "получения списка моделей"
                        )

                    data = await response.json()

                    # Пробуем разные форматы ответа
                    if isinstance(data, dict):
                        # Формат OpenAI
                        if "data" in data:
                            return [
                                {
                                    "id": model["id"],
                                    "name": model.get("name", model["id"]),
                                }
                                for model in data["data"]
                            ]
                        # Другие возможные форматы
                        models = data.get("models", [])
                        if models:
                            return [
                                {
                                    "id": model.get("id", model.get("model_id", "")),
                                    "name": model.get(
                                        "name",
                                        model.get("model_name", model.get("id", "")),
                                    ),
                                }
                                for model in models
                            ]
                    elif isinstance(data, list):
                        # Список моделей напрямую
                        return [
                            {
                                "id": model.get("id", model.get("model_id", "")),
                                "name": model.get(
                                    "name", model.get("model_name", model.get("id", ""))
                                ),
                            }
                            for model in data
                        ]

                    logger.error(f"Неизвестный формат ответа API: {data}")
                    return []

        except Exception as e:
            logger.error(f"Ошибка при получении списка моделей: {str(e)}")
            return []

    async def translate(self, messages, target_lang, streaming_callback=None) -> str:
        """
        Переводит текст с использованием кастомного API в формате OpenAI.
        Принимает список сообщений, сформированный LLMApi.

        Args:
            messages: Список сообщений, например, [
                {"role": "system", "content": "Target language: Русский.\n\n<system prompt>"},
                {"role": "user", "content": "API endpoint и API key"}
            ]
            target_lang: Целевой язык (используется для обратной совместимости, но не влияет на формирование сообщения)
            streaming_callback: Опциональный callback для обработки потокового вывода

        Returns:
            str: Переведенный текст
        """
        prepared_msgs = await self._prepare_messages(messages)
        use_streaming = self.model_info.get("streaming", False)

        if use_streaming:
            logger.debug("=== Используем streaming режим для перевода ===")
            # Преобразуем сообщения в формат для generate_stream
            prompt = prepared_msgs[-1][
                "content"
            ]  # Берем последнее сообщение как prompt
            system_prompt = (
                prepared_msgs[0]["content"] if len(prepared_msgs) > 1 else ""
            )

            # Очищаем предыдущий текст через callback
            if streaming_callback:
                await streaming_callback("")

            accumulated_text = ""

            async for delta in self.generate_stream(prompt, system_prompt):
                accumulated_text += delta
                if streaming_callback:
                    await streaming_callback(
                        delta
                    )  # Отправляем только новую часть текста

            return accumulated_text

        async with aiohttp.ClientSession() as session:
            data = {
                "model": self.model_info["model_name"],
                "messages": prepared_msgs,
                "temperature": 0.3,
                "stream": False,
            }
            headers = await self._get_headers()

            await self._log_http_request(
                "POST", self.model_info["api_endpoint"], headers, data
            )

            async with session.post(
                self.model_info["api_endpoint"], headers=headers, json=data
            ) as response:
                response_text = await response.text()
                await self._log_http_response(response, response_text)

                if response.status != 200:
                    await self._handle_http_error(response, "перевода")

                result = await response.json()
                content = result["choices"][0]["message"]["content"]
                if isinstance(content, list):
                    return content[0].get("text", "")
                return content

    async def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        """
        Генерирует текст с использованием кастомного API в формате OpenAI.

        Args:
            prompt: Текст запроса
            system_prompt: Системный промпт

        Returns:
            str: Сгенерированный текст
        """
        messages = []
        if system_prompt:
            messages.append(self._format_message("system", system_prompt))
        messages.append(self._format_message("user", prompt))

        async with aiohttp.ClientSession() as session:
            data = {
                "model": self.model_info["model_name"],
                "messages": await self._prepare_messages(messages),
                "temperature": 0.3,
                "stream": False,
            }

            headers = await self._get_headers()
            logger.debug(f"Request data: {data}")
            logger.debug(f"Request headers: {headers}")
            async with session.post(
                self.model_info["api_endpoint"], headers=headers, json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        f"Ошибка перевода. Статус {response.status}. Текст ошибки: {error_text}"
                    )
                    raise Exception(f"API error: {error_text}")

                result = await response.json()
                logger.debug(f"API response: {result}")
                content = result["choices"][0]["message"]["content"]
                if isinstance(content, list):
                    return content[0].get("text", "")
                return content

    async def generate_stream(
        self, prompt: str, system_prompt: str = ""
    ) -> AsyncGenerator[str, None]:
        """
        Генерирует текст в потоковом режиме с использованием кастомного API в формате OpenAI.

        Args:
            prompt: Текст запроса
            system_prompt: Системный промпт

        Yields:
            str: Части сгенерированного текста
        """
        messages = []
        if system_prompt:
            messages.append(self._format_message("system", system_prompt))
        messages.append(self._format_message("user", prompt))

        prepared_messages = await self._prepare_messages(messages)
        logger.debug(f"\n=== Подготовленные сообщения для stream: {prepared_messages}")

        async with aiohttp.ClientSession() as session:
            data = {
                "model": self.model_info["model_name"],
                "messages": prepared_messages,
                "temperature": 0.3,
                "stream": True,
            }

            headers = await self._get_headers()

            await self._log_http_request(
                "POST", self.model_info["api_endpoint"], headers, data
            )

            async with session.post(
                self.model_info["api_endpoint"], headers=headers, json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    await self._log_http_response(response, error_text)
                    await self._handle_http_error(response, "потокового перевода")

                logger.debug(f"=== Stream response status: {response.status}")
                first_chunk = True
                async for line in response.content:
                    if line:
                        line = line.decode("utf-8").strip()
                        logger.debug(f"\n=== Получена строка потока: {line}")
                        if line.startswith("data: "):
                            if line == "data: [DONE]":
                                logger.debug("=== Получен маркер завершения потока")
                                break
                            try:
                                chunk = json.loads(line[6:])
                                logger.debug(f"=== Получен chunk: {chunk}")

                                # Проверяем наличие delta в chunk
                                if "choices" not in chunk or not chunk["choices"]:
                                    logger.debug("=== Chunk не содержит choices")
                                    continue

                                choice = chunk["choices"][0]
                                if "delta" not in choice:
                                    logger.debug("=== Choice не содержит delta")
                                    continue

                                # Пропускаем только первый чанк, где роль assistant
                                if (
                                    first_chunk
                                    and choice["delta"].get("role") == "assistant"
                                ):
                                    logger.debug(
                                        "=== Пропускаем первый чанк с ролью assistant"
                                    )
                                    first_chunk = False
                                    continue

                                first_chunk = False

                                # Проверяем finish_reason только если он не пустой
                                if choice.get("finish_reason"):
                                    logger.debug(
                                        f"=== Finish reason: {choice['finish_reason']}, завершаю поток"
                                    )
                                    break

                                delta = choice["delta"].get("content", "")
                                if delta:
                                    if isinstance(delta, list):
                                        delta = delta[0].get("text", "")
                                        logger.debug(
                                            f"=== Преобразован delta из списка: {delta}"
                                        )
                                    logger.debug(f"=== Delta получен: {delta}")
                                    yield delta
                                else:
                                    logger.debug("=== Получен пустой delta")

                            except json.JSONDecodeError as e:
                                logger.debug(
                                    f"=== Ошибка парсинга JSON: {str(e)}, строка: {line}"
                                )
                                continue
                            except Exception as e:
                                logger.debug(
                                    f"=== Неожиданная ошибка при обработке chunk: {str(e)}"
                                )
                                continue
