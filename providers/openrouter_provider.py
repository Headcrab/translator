"""Реализация провайдера для OpenRouter."""
from typing import Optional, Callable, Coroutine
from providers.base_provider import BaseProvider
import aiohttp
import json
import asyncio

class OpenRouterProvider(BaseProvider):
    """Провайдер для работы с OpenRouter API."""
    
    async def translate(
        self,
        messages: list,
        target_lang: str,
        streaming_callback: Optional[Callable[[str], Coroutine]] = None
    ) -> str:
        # Если есть callback для стриминга, используем streaming_translate
        if streaming_callback:
            return await self._streaming_translate(messages, streaming_callback)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "LLM Translator"
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
                response.raise_for_status()
                result = await response.json()
                return result["choices"][0]["message"]["content"].strip()

    async def _streaming_translate(self, messages, callback):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "LLM Translator",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": messages,
            "stream": True
        }
        
        full_response = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_endpoint,
                    headers=headers,
                    json=data
                ) as response:
                    response.raise_for_status()
                    
                    buffer = ""
                    async for chunk in response.content:
                        buffer += chunk.decode('utf-8')
                        while 'data: ' in buffer:
                            # Находим начало и конец текущего события SSE
                            start = buffer.find('data: ')
                            end = buffer.find('\n', start)
                            if end == -1:  # Если конец строки не найден, ждем больше данных
                                break
                                
                            line = buffer[start:end].strip()
                            buffer = buffer[end + 1:]  # Убираем обработанную часть из буфера
                            
                            if line == 'data: [DONE]':
                                break
                                
                            if line.startswith('data: '):
                                try:
                                    chunk_data = json.loads(line[6:])
                                    if 'choices' in chunk_data:
                                        delta = chunk_data['choices'][0].get('delta', {}).get('content', '')
                                        if delta:
                                            full_response.append(delta)
                                            if callback is not None:
                                                if asyncio.iscoroutinefunction(callback):
                                                    await callback(delta)
                                                else:
                                                    callback(delta)
                                except json.JSONDecodeError:
                                    continue

            return ''.join(full_response)
        
        except Exception as e:
            print(f"OpenRouter streaming error: {e}")
            return "Ошибка перевода" 