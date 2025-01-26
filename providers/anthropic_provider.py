"""Реализация провайдера для Anthropic."""
from typing import Optional, Callable, Coroutine
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
        streaming_callback: Optional[Callable[[str], Coroutine]] = None
    ) -> str:
        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key": self.access_token
        }
        
        formatted_messages = []
        for msg in messages:
            role = "assistant" if msg["role"] == "assistant" else "user"
            if msg["role"] == "system":
                system = msg["content"]
                continue
            formatted_messages.append({"role": role, "content": msg["content"]})
        
        logging.debug(f"Formatted messages: {formatted_messages}")
        
        data = {
            "model": self.model_name,
            "messages": formatted_messages,
            "max_tokens": 1000,
            "system": system if "system" in locals() else None,
            "stream": True if streaming_callback else False
        }
        
        logging.debug(f"Request data: {data}")
        full_response = ""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_endpoint}/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=None)
                ) as response:
                    response.raise_for_status()
                    logging.debug(f"Response status: {response.status}")
                    
                    if streaming_callback:
                        async for line in response.content:
                            if line:
                                line = line.decode('utf-8').strip()
                                logging.debug(f"Received line: {line}")
                                
                                if not line or line == "data: [DONE]":
                                    continue
                                    
                                if line.startswith("data: "):
                                    try:
                                        chunk = json.loads(line[6:])
                                        if chunk["type"] == "content_block_delta":
                                            delta = chunk["delta"].get("text", "")
                                            if delta:
                                                full_response += delta
                                                await streaming_callback(delta)
                                    except json.JSONDecodeError as e:
                                        logging.error(f"JSON decode error: {e}, line: {line}")
                                        continue
                                    except Exception as e:
                                        logging.error(f"Error processing chunk: {e}")
                                        continue
                        
                        return full_response
                    else:
                        result = await response.json()
                        return result["content"][0]["text"]
                        
        except Exception as e:
            logging.error(f"Error in translate: {e}")
            raise 