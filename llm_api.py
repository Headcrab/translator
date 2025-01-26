"""Модуль для работы с API различных LLM моделей."""

import os
import json
import aiohttp
import asyncio
from typing import Optional, Dict, Any
import requests
from settings_manager import SettingsManager

class LLMApi:
    """Класс для работы с API различных LLM моделей."""
    
    def __init__(self, model_info: Dict[str, Any], settings_manager: SettingsManager):
        """
        Инициализация клиента API.
        
        Args:
            model_info: Словарь с информацией о модели:
                - name: Имя модели
                - provider: Провайдер (OpenAI, Anthropic, OpenRouter)
                - api_endpoint: URL эндпоинта API
                - model_name: Название модели у провайдера
                - access_token: Токен доступа к API
        """
        self.model_info = model_info
        self.settings_manager = settings_manager
        self.provider = model_info["provider"]
        self.api_endpoint = model_info["api_endpoint"]
        self.model_name = model_info["model_name"]
        self.access_token = model_info.get("access_token")
        
    async def translate(self, text: str, target_lang: str, streaming_callback=None) -> str:
        """Выполняет перевод с поддержкой потокового режима."""
        system_prompt = self.settings_manager.get_system_prompt()
        
        messages = [
            {"role": "system", "content": system_prompt.format(language=target_lang)},
            {"role": "user", "content": text}
        ]

        if self.provider == "OpenAI" and self.model_info.get('streaming', False):
            return await self._streaming_translate(messages, streaming_callback)
        else:
            return await self._regular_translate(messages)

    async def _streaming_translate(self, messages, callback):
        """Потоковый перевод для OpenAI."""
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError(
                "Для использования потокового режима требуется библиотека openai. "
                "Установите ее: pip install openai"
            )
        
        client = AsyncOpenAI(api_key=self.access_token)
        
        full_translation = []
        response = await client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True
        )
        
        async for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                full_translation.append(delta)
                if callback:
                    callback(delta)
        
        return ''.join(full_translation)

    async def _regular_translate(self, messages: list) -> str:
        """Перевод через OpenAI API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        
        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_endpoint}/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API вернул ошибку {response.status}: {error_text}")
                    
                result = await response.json()
                return result["choices"][0]["message"]["content"].strip()
                
    async def _translate_anthropic(self, messages: list) -> str:
        """Перевод через Anthropic API."""
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.access_token
        }
        
        data = {
            "model": self.model_name,
            "prompt": f"\n\nHuman: {messages[-1]['content']}\n\nAssistant:",
            "max_tokens_to_sample": 1000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_endpoint}/v1/complete",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API вернул ошибку {response.status}: {error_text}")
                    
                result = await response.json()
                return result["completion"].strip()
                
    async def _translate_openrouter(self, messages: list) -> str:
        """Перевод через OpenRouter API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        
        data = {
            "model": self.model_name,
            "messages": messages
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_endpoint,
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenRouter API вернул ошибку {response.status}: {error_text}")
                    
                result = await response.json()
                return result["choices"][0]["message"]["content"].strip()

    async def translate_text_async(self, text, target_lang, model_config, callback=None):
        provider = model_config.get('provider')
        
        if provider == "openai":
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=model_config.get('access_token'))
            
            response = await client.chat.completions.create(
                model=model_config['model_name'],
                messages=[{"role": "user", "content": text}],
                stream=model_config.get('streaming', False)
            )
            
            if model_config.get('streaming'):
                full_translation = []
                async for chunk in response:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_translation.append(delta)
                        if callback:
                            await asyncio.sleep(0.01)
                            callback(delta)
                return ''.join(full_translation)
            else:
                return response.choices[0].message.content
        
        # Аналогичные изменения для других провайдеров...

def translate(text):
    # Пример реализации перевода с использованием внешнего API
    try:
        response = requests.post("https://api.translate.com/translate", data={"text": text})
        response.raise_for_status()
        return response.json().get("translated_text", "")
    except requests.RequestException as e:
        # Логирование ошибки
        print(f"Ошибка при переводе: {e}")
        return "Ошибка перевода"

