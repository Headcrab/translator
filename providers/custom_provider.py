"""Кастомный провайдер для работы с произвольными LLM API."""
from typing import Dict, Any, List, AsyncGenerator
from .base_provider import BaseProvider
import aiohttp
import json
import logging

logger = logging.getLogger(__name__)

class CustomProvider(BaseProvider):
    """Провайдер для работы с произвольными LLM API."""
    
    def __init__(self, model_info: Dict[str, Any]):
        """
        Инициализирует провайдер с информацией о модели.
        
        Args:
            model_info: Словарь с информацией о модели
        """
        super().__init__(model_info)
        # Добавляем /chat/completions к URL если его нет
        api_endpoint = self.model_info.get("api_endpoint", "").rstrip("/")
        if not api_endpoint.endswith("/chat/completions"):
            api_endpoint += "/chat/completions"
        self.model_info["api_endpoint"] = api_endpoint
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
        return {
            "role": role,
            "content": content
        }
        
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
                "stream": False
            }
            
            async with session.post(
                self.model_info["api_endpoint"],
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    self.api_version = "base"
                    return
                    
            # Если базовый формат не работает, пробуем формат GPT-4 Vision
            data["messages"][0]["content"] = [{"type": "text", "text": "test"}]
            async with session.post(
                self.model_info["api_endpoint"],
                headers=headers,
                json=data
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
        headers = {
            "Content-Type": "application/json"
        }
        
        token = self.model_info.get('access_token')
        if token:
            # Пробуем разные варианты заголовков авторизации
            auth_headers = []
            
            # Если токен уже содержит тип, используем как есть
            if any(token.startswith(prefix) for prefix in ['Bearer ', 'Basic ', 'Token ']):
                auth_headers.append(token)
            else:
                # Добавляем разные варианты префиксов
                auth_headers.extend([
                    f"Bearer {token}",
                    token,  # Без префикса
                    f"Token {token}",
                    f"Basic {token}"
                ])
            
            # Пробуем разные имена заголовков
            auth_header_names = [
                "Authorization",
                "X-API-Key",
                "api-key",
                "x-api-token"
            ]
            
            # Создаем все возможные комбинации
            for header_name in auth_header_names:
                for auth_value in auth_headers:
                    headers[header_name] = auth_value
                    
                    # Пробуем сделать тестовый запрос с текущими заголовками
                    try:
                        await self._detect_api_version(headers)
                        logger.info(f"Успешная авторизация с заголовком {header_name}: {auth_value}")
                        return headers
                    except Exception as e:
                        logger.debug(f"Неудачная попытка с заголовком {header_name}: {auth_value} - {str(e)}")
                        continue
            
            # Если ни один вариант не сработал, возвращаем базовый вариант
            headers["Authorization"] = f"Bearer {token}"
                
        return headers
        
    async def _prepare_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
                    "content": [{"type": "text", "text": msg["content"]}]
                }
                for msg in messages
            ]
        return messages
        
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Возвращает пустой список моделей, так как для кастомного провайдера
        модели задаются вручную.
        
        Returns:
            List[Dict[str, Any]]: Пустой список моделей
        """
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
            print("=== Используем streaming режим для перевода ===")
            # Преобразуем сообщения в формат для generate_stream
            prompt = prepared_msgs[-1]["content"]  # Берем последнее сообщение как prompt
            system_prompt = prepared_msgs[0]["content"] if len(prepared_msgs) > 1 else ""
            
            # Очищаем предыдущий текст через callback
            if streaming_callback:
                await streaming_callback("")
            
            accumulated_text = ""
            
            async for delta in self.generate_stream(prompt, system_prompt):
                accumulated_text += delta
                if streaming_callback:
                    await streaming_callback(delta)  # Отправляем только новую часть текста
            
            return accumulated_text
            
        async with aiohttp.ClientSession() as session:
            data = {
                "model": self.model_info["model_name"],
                "messages": prepared_msgs,
                "temperature": 0.3,
                "stream": False
            }
            headers = await self._get_headers()
            print(f"=== Translate Request data: {data}")
            print(f"=== Translate Request headers: {headers}")
            async with session.post(
                self.model_info["api_endpoint"],
                headers=headers,
                json=data
            ) as response:
                print(f"=== Translate Response Status: {response.status}")
                if response.status != 200:
                    error_text = await response.text()
                    print(f"=== Ошибка перевода. Статус {response.status}. Текст ошибки: {error_text}")
                    raise Exception(f"API error: {error_text}")
                    
                result = await response.json()
                print(f"=== Translate API response: {result}")
                content = result["choices"][0]["message"]["content"]
                print(f"=== Translate content: {content}")
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
                "stream": False
            }
            
            headers = await self._get_headers()
            logger.debug(f"Request data: {data}")
            logger.debug(f"Request headers: {headers}")
            async with session.post(
                self.model_info["api_endpoint"],
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Ошибка перевода. Статус {response.status}. Текст ошибки: {error_text}")
                    raise Exception(f"API error: {error_text}")
                    
                result = await response.json()
                logger.debug(f"API response: {result}")
                content = result["choices"][0]["message"]["content"]
                if isinstance(content, list):
                    return content[0].get("text", "")
                return content
        
    async def generate_stream(self, prompt: str, system_prompt: str = "") -> AsyncGenerator[str, None]:
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
        print(f"\n=== Подготовленные сообщения для stream: {prepared_messages}")
        
        async with aiohttp.ClientSession() as session:
            data = {
                "model": self.model_info["model_name"],
                "messages": prepared_messages,
                "temperature": 0.3,
                "stream": True
            }
            
            headers = await self._get_headers()
            print(f"=== Stream request data: {data}")
            print(f"=== Stream request headers: {headers}")
            
            async with session.post(
                self.model_info["api_endpoint"],
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"=== Stream error response: {error_text}")
                    raise Exception(f"API error: {error_text}")
                
                print(f"=== Stream response status: {response.status}")
                first_chunk = True
                async for line in response.content:
                    if line:
                        line = line.decode("utf-8").strip()
                        print(f"\n=== Получена строка потока: {line}")
                        if line.startswith("data: "):
                            if line == "data: [DONE]":
                                print("=== Получен маркер завершения потока")
                                break
                            try:
                                chunk = json.loads(line[6:])
                                print(f"=== Получен chunk: {chunk}")
                                
                                # Проверяем наличие delta в chunk
                                if "choices" not in chunk or not chunk["choices"]:
                                    print("=== Chunk не содержит choices")
                                    continue
                                    
                                choice = chunk["choices"][0]
                                if "delta" not in choice:
                                    print("=== Choice не содержит delta")
                                    continue
                                
                                # Пропускаем только первый чанк, где роль assistant
                                if first_chunk and choice["delta"].get("role") == "assistant":
                                    print("=== Пропускаем первый чанк с ролью assistant")
                                    first_chunk = False
                                    continue
                                
                                first_chunk = False
                                
                                # Проверяем finish_reason только если он не пустой
                                if choice.get("finish_reason"):
                                    print(f"=== Finish reason: {choice['finish_reason']}, завершаю поток")
                                    break
                                    
                                delta = choice["delta"].get("content", "")
                                if delta:
                                    if isinstance(delta, list):
                                        delta = delta[0].get("text", "")
                                        print(f"=== Преобразован delta из списка: {delta}")
                                    print(f"=== Delta получен: {delta}")
                                    yield delta
                                else:
                                    print("=== Получен пустой delta")
                                    
                            except json.JSONDecodeError as e:
                                print(f"=== Ошибка парсинга JSON: {str(e)}, строка: {line}")
                                continue
                            except Exception as e:
                                print(f"=== Неожиданная ошибка при обработке chunk: {str(e)}")
                                continue 