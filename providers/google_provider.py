"""Провайдер для работы с Google AI API."""

import google.generativeai as genai
import asyncio
from typing import List, Dict, Any, Optional, Callable
from .base_provider import BaseProvider

class GoogleProvider(BaseProvider):
    """Класс для работы с Google AI API."""
    
    def __init__(self, model_info: Dict[str, Any]):
        """
        Инициализация провайдера.
        
        Args:
            model_info: Словарь с информацией о модели
        """
        super().__init__(model_info)
        genai.configure(api_key=model_info['access_token'])
        self.model = genai.GenerativeModel(model_info['model_name'])
        
    async def translate(
        self,
        messages: List[Dict[str, str]],
        target_lang: str,
        streaming_callback: Optional[Callable] = None
    ) -> str:
        """
        Выполняет перевод текста.
        
        Args:
            messages: Список сообщений для контекста
            target_lang: Целевой язык перевода
            streaming_callback: Callback для потоковой обработки
            
        Returns:
            str: Переведенный текст
        """
        prompt = self._convert_messages_to_prompt(messages)
        
        try:
            if not streaming_callback:
                # Неасинхронный режим
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.model.generate_content(prompt)
                )
                return response.text
            
            # Потоковый режим
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model.generate_content(prompt, stream=True)
            )
            
            full_response = ""
            async def process_chunks():
                nonlocal full_response
                for chunk in response:
                    if chunk.text:
                        await streaming_callback(chunk.text)
                        full_response += chunk.text
                        await asyncio.sleep(0)  # Даем шанс другим корутинам
            
            await process_chunks()
            return full_response
                
        except Exception as e:
            print(f"Ошибка Google AI API: {e}")
            raise
            
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Конвертирует список сообщений в текстовый промпт."""
        prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                prompt += f"Instructions: {msg['content']}\n\n"
            elif msg["role"] == "user":
                prompt += f"Text to translate: {msg['content']}\n\n"
            elif msg["role"] == "assistant":
                prompt += f"Translation: {msg['content']}\n\n"
        return prompt.strip() 