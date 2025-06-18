"""Реализация провайдера для Anthropic."""

from typing import Optional, Callable, Coroutine, List, Dict, Any
from providers.base_provider import BaseProvider
import aiohttp
import json
import logging


class AnthropicProvider(BaseProvider):
    """Провайдер для работы с Anthropic API."""

    async def translate(
        self,
        messages: list,
        target_lang: str,
        streaming_callback: Optional[Callable[[str], Coroutine]] = None,
    ) -> str:
        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key": self.access_token,
        }

        formatted_messages = []
        system = None
        for msg in messages:
            role = "assistant" if msg["role"] == "assistant" else "user"
            if msg["role"] == "system":
                system = msg["content"]
                continue
            formatted_messages.append({"role": role, "content": msg["content"]})

        logging.debug(f"Formatted messages: {formatted_messages}")

        # Определяем режим streaming
        use_streaming = streaming_callback is not None

        data = {
            "model": self.model_name,
            "max_tokens": 4000,
            "messages": formatted_messages,
            "stream": use_streaming,
        }

        if system:
            data["system"] = system

        url = "https://api.anthropic.com/v1/messages"
        await self._log_http_request("POST", url, headers, data)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    response_text = await response.text()
                    await self._log_http_response(response, response_text)
                    await self._handle_http_error(response, "перевода")

                if use_streaming:
                    return await self._handle_streaming_response(
                        response, streaming_callback
                    )
                else:
                    return await self._handle_regular_response(response)

    async def _handle_regular_response(self, response) -> str:
        """Обрабатывает обычный (не streaming) ответ от Anthropic."""
        response_text = await response.text()
        await self._log_http_response(response, response_text)

        result = await response.json()
        if result.get("content") and len(result["content"]) > 0:
            return result["content"][0]["text"]
        return ""

    async def _handle_streaming_response(self, response, streaming_callback) -> str:
        """Обрабатывает streaming ответ от Anthropic."""
        full_response = ""

        async for line in response.content:
            line = line.decode("utf-8").strip()
            if not line:
                continue

            # Anthropic использует формат Server-Sent Events
            if line.startswith("data: "):
                data_str = line[6:]  # Убираем "data: "

                if data_str == "[DONE]":
                    break

                try:
                    data = json.loads(data_str)

                    # Обрабатываем различные типы событий
                    if data.get("type") == "content_block_delta":
                        delta = data.get("delta", {})
                        if delta.get("type") == "text_delta":
                            text_chunk = delta.get("text", "")
                            if text_chunk:
                                full_response += text_chunk
                                if streaming_callback:
                                    await streaming_callback(text_chunk)

                except json.JSONDecodeError:
                    # Игнорируем некорректные JSON строки
                    continue

        return full_response

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Получает список доступных моделей от Anthropic."""
        # Сначала проверяем валидность API ключа
        headers = {
            "x-api-key": self.access_token,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                # Делаем минимальный тестовый запрос для проверки ключа
                test_data = {
                    "model": "claude-3-haiku-20240307",
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1,
                }

                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=test_data,
                ) as response:
                    if response.status == 401:
                        logging.error("Anthropic API key is invalid")
                        return []
                    # Остальные ошибки игнорируем - главное что ключ валидный

        except Exception as e:
            logging.error(f"Error validating Anthropic API key: {e}")
            return []

        # Возвращаем список моделей только если ключ валидный
        models = [
            {
                "name": "Anthropic - Claude 3 Opus",
                "model_name": "claude-3-opus-20240229",
                "description": "Most capable model for highly complex tasks",
            },
            {
                "name": "Anthropic - Claude 3 Sonnet",
                "model_name": "claude-3-sonnet-20240229",
                "description": "Ideal balance of intelligence and speed",
            },
            {
                "name": "Anthropic - Claude 3 Haiku",
                "model_name": "claude-3-haiku-20240307",
                "description": "Fastest and most compact model for simpler tasks",
            },
            {
                "name": "Anthropic - Claude 2.1",
                "model_name": "claude-2.1",
                "description": "Previous generation model with strong capabilities",
            },
            {
                "name": "Anthropic - Claude 2.0",
                "model_name": "claude-2.0",
                "description": "Previous generation model",
            },
            {
                "name": "Anthropic - Claude Instant",
                "model_name": "claude-instant-1.2",
                "description": "Fast and cost-effective model",
            },
        ]
        return models
