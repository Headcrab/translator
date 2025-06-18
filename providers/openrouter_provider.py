"""Реализация провайдера для OpenRouter."""

from typing import Optional, Callable, Coroutine, List, Dict, Any
from providers.base_provider import BaseProvider
import aiohttp
import json
import logging


class OpenRouterProvider(BaseProvider):
    """Провайдер для работы с OpenRouter API."""

    def __init__(self, config: dict):
        if "access_token" not in config:
            config["access_token"] = ""
        super().__init__(
            config
        )  # наследуем и инициализируем access_token, model_name и api_endpoint
        self.stream_options = config.get("stream_options", {})

    async def translate(
        self,
        messages: list,
        target_lang: str,
        streaming_callback: Optional[Callable[[str], Coroutine]] = None,
    ) -> str:
        if streaming_callback:
            return await self._streaming_translate(messages, streaming_callback)

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "LLM Translator",
            "Content-Type": "application/json",
        }

        data = {"model": self.model_name, "messages": messages, "temperature": 0.7}

        await self._log_http_request("POST", self.api_endpoint, headers, data)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_endpoint, headers=headers, json=data
            ) as response:
                response_text = await response.text()
                await self._log_http_response(response, response_text)

                if response.status != 200:
                    await self._handle_http_error(response, "перевода")

                result = await response.json()
                return result["choices"][0]["message"]["content"].strip()

    async def _streaming_translate(self, messages, callback):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "LLM Translator",
            "Content-Type": "application/json",
        }

        data = {"model": self.model_name, "messages": messages, "stream": True}

        full_response = []

        await self._log_http_request("POST", self.api_endpoint, headers, data)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_endpoint, headers=headers, json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    await self._log_http_response(response, error_text)
                    await self._handle_http_error(response, "потокового перевода")

                async for line in response.content:
                    if line:
                        line = line.decode("utf-8").strip()
                        if line.startswith("data: ") and line != "data: [DONE]":
                            try:
                                chunk_data = json.loads(line[6:])
                                if "choices" in chunk_data and chunk_data["choices"]:
                                    delta = chunk_data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        full_response.append(content)
                                        if callback:
                                            await callback(content)
                            except json.JSONDecodeError:
                                continue

        return "".join(full_response) or ""

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Получает список доступных моделей от OpenRouter."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "LLM Translator",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://openrouter.ai/api/v1/models", headers=headers
                ) as response:
                    if response.status != 200:
                        await self._handle_http_error(
                            response, "получения списка моделей"
                        )

                    data = await response.json()
                    models = []

                    for model in data.get("data", []):
                        models.append(
                            {
                                "name": f"OpenRouter - {model['name']}",
                                "model_name": model["id"],
                                "description": model.get(
                                    "description", f"OpenRouter {model['name']} model"
                                ),
                            }
                        )

                    return sorted(models, key=lambda x: x["model_name"])

        except Exception as e:
            logging.error(f"Error getting OpenRouter models: {e}")
            return []
