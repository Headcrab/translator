"""Реализация провайдера для OpenRouter."""
from typing import Optional, Callable, Coroutine
from providers.base_provider import BaseProvider
import aiohttp
import json
import logging

class OpenRouterProvider(BaseProvider):
    """Провайдер для работы с OpenRouter API."""
    
    def __init__(self, config: dict):
        self.access_token = config["access_token"]
        self.model_name = config["model_name"]
        self.api_endpoint = config.get("api_endpoint", "https://openrouter.ai/api/v1/chat/completions")
        self.stream_options = config.get("stream_options", {})
    
    async def translate(
        self,
        messages: list,
        target_lang: str,
        streaming_callback: Optional[Callable[[str], Coroutine]] = None
    ) -> str:
        return await self._streaming_translate(messages, streaming_callback)

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
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_endpoint,
                headers=headers,
                json=data
            ) as response:
                response.raise_for_status()
                
                if response.status != 200:
                    error_text = await response.text()
                    logging.error(f"OpenRouter API error: {error_text}")
                    raise Exception(f"OpenRouter API error: {error_text}")
                
                async for line in response.content:
                    if line:
                        line = line.decode('utf-8').strip()
                        logging.debug(f"Received line: {line}")
                        
                        if not line or line == "data: [DONE]":
                            continue
                            
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                if not data["choices"]:
                                    continue
                                delta = data["choices"][0]["delta"].get("content", "")
                                if delta:
                                    full_response.append(delta)
                                    if callback:
                                        await callback(delta)
                            except Exception as e:
                                logging.error(f"Error processing chunk: {e}")
                                continue
        
        return "".join(full_response) 