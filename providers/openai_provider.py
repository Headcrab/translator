"""Реализация провайдера для OpenAI."""

from typing import Any, Dict, Optional, Callable, Coroutine, List
from providers.base_provider import BaseProvider
import aiohttp
from openai import AsyncOpenAI
import logging


class OpenAIProvider(BaseProvider):
    """Провайдер для работы с OpenAI API."""

    async def translate(
        self,
        messages: list,
        target_lang: str,
        streaming_callback: Optional[Callable[[str], Coroutine]] = None,
    ) -> str:
        if self.model_info.get("streaming", False):
            return await self._streaming_translate(messages, streaming_callback)
        return await self._regular_translate(messages)

    async def _streaming_translate(self, messages, callback):
        client = None
        try:
            client = AsyncOpenAI(api_key=self.access_token)
            full_translation = []

            response = await client.chat.completions.create(
                model=self.model_name, messages=messages, stream=True
            )

            async for chunk in response:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta.content
                if delta:
                    full_translation.append(delta)
                    if callback:
                        try:
                            await callback(delta)
                        except Exception as e:
                            logging.error("Callback error: %s", e)

            return "".join(full_translation) or ""

        except Exception as e:
            logging.error("Streaming error: %s", e)
            return "Ошибка перевода"

        finally:
            if client:
                await client.close()

    async def _regular_translate(self, messages: list) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

        data = {"model": self.model_name, "messages": messages, "temperature": 0.7}

        url = f"{self.api_endpoint}/chat/completions"
        await self._log_http_request("POST", url, headers, data)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                response_text = await response.text()
                await self._log_http_response(response, response_text)

                if response.status != 200:
                    await self._handle_http_error(response, "перевода")

                result = await response.json()
                return result["choices"][0]["message"]["content"].strip()

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Получает список доступных моделей от OpenAI."""
        client = None
        try:
            client = AsyncOpenAI(api_key=self.access_token)
            models = await client.models.list()

            # Фильтруем только модели для чата и GPT
            chat_models = []
            for model in models.data:
                if model.id.startswith(("gpt-", "text-davinci-")):
                    # Создаем описание на основе ID модели
                    description = ""
                    if "gpt-4" in model.id:
                        description = (
                            "Самая мощная модель GPT-4 с расширенными возможностями"
                        )
                    elif "gpt-3.5" in model.id:
                        description = "Быстрая и эффективная модель GPT-3.5"
                    elif "text-davinci" in model.id:
                        description = "Классическая модель Davinci"
                    else:
                        description = f"OpenAI {model.id} model"

                    chat_models.append(
                        {
                            "name": f"OpenAI - {model.id}",
                            "model_name": model.id,
                            "description": description,
                        }
                    )

            return sorted(chat_models, key=lambda x: x["model_name"])

        except Exception as e:
            logging.error("Error getting OpenAI models: %s", e)
            return []

        finally:
            if client:
                await client.close()
