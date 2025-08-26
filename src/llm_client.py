"""
LM Studio API Client

A client for communicating with LM Studio's local API server.
LM Studio provides an OpenAI-compatible API endpoint.
"""

import json
import requests
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union
from enum import Enum


class Role(Enum):
    """Message roles for chat completion."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """Represents a chat message."""
    role: Role
    content: str


@dataclass
class CompletionUsage:
    """Token usage information for a completion."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class CompletionChoice:
    """A single completion choice."""
    index: int
    message: Message
    finish_reason: Optional[str] = None


@dataclass
class CompletionResponse:
    """Response from the chat completion API."""
    id: str
    object: str
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: CompletionUsage


@dataclass
class ModelInfo:
    """Information about an available model."""
    id: str
    object: str
    created: int
    owned_by: str


@dataclass
class ModelsResponse:
    """Response containing available models."""
    object: str
    data: List[ModelInfo]


class LMStudioClient:
    """
    Client for interacting with LM Studio's local API server.
    
    LM Studio provides an OpenAI-compatible API that runs locally.
    Default endpoint is typically http://localhost:1234/v1
    """
    
    def __init__(
        self, 
        base_url: str = "http://localhost:1234/v1",
        timeout: int = 30,
        api_key: Optional[str] = None
    ):
        """
        Initialize the LM Studio client.
        
        Args:
            base_url: Base URL for the LM Studio API server
            timeout: Request timeout in seconds
            api_key: Optional API key (usually not needed for local LM Studio)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.api_key = api_key
        
        # Set up session for connection reuse
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        self.session.headers.update({"Content-Type": "application/json"})
    
    def chat_completion(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stream: bool = False,
        stop: Optional[Union[str, List[str]]] = None
    ) -> CompletionResponse:
        """
        Create a chat completion using the LM Studio API.
        
        Args:
            messages: List of conversation messages
            model: Model identifier (optional, uses server default if None)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2.0 to 2.0)
            presence_penalty: Presence penalty (-2.0 to 2.0)
            stream: Whether to stream the response
            stop: Stop sequences
            
        Returns:
            CompletionResponse object with the API response
            
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If the response format is invalid
        """
        url = f"{self.base_url}/chat/completions"
        
        # Convert messages to dict format
        message_dicts = [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]
        
        payload: Dict[str, Any] = {
            "messages": message_dicts,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "stream": stream
        }
        
        # Add optional parameters
        if model:
            payload["model"] = model
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if stop:
            payload["stop"] = stop
        
        try:
            response = self.session.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            
            # Check if the response is an error and log the details
            if not response.ok:
                try:
                    error_data = response.json()
                    error_msg = f"LM Studio API request failed: {response.status_code} {response.reason} for url: {url}"
                    if 'error' in error_data:
                        error_msg += f"\nServer error: {error_data['error']}"
                        if isinstance(error_data['error'], dict) and 'message' in error_data['error']:
                            error_msg += f" - {error_data['error']['message']}"
                    raise requests.RequestException(error_msg)
                except ValueError:
                    # If we can't parse the error response as JSON
                    raise requests.RequestException(f"LM Studio API request failed: {response.status_code} {response.reason} for url: {url}\nResponse: {response.text[:500]}")
            
            response.raise_for_status()
            
            data = response.json()
            return self._parse_completion_response(data)
            
        except requests.RequestException as e:
            raise requests.RequestException(f"LM Studio API request failed: {e}")
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"Invalid response format from LM Studio API: {e}")
    
    def get_models(self) -> ModelsResponse:
        """
        Get list of available models from LM Studio.
        
        Returns:
            ModelsResponse object with available models
            
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If the response format is invalid
        """
        url = f"{self.base_url}/models"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_models_response(data)
            
        except requests.RequestException as e:
            raise requests.RequestException(f"LM Studio API request failed: {e}")
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"Invalid response format from LM Studio API: {e}")
    
    def simple_chat(
        self, 
        user_message: str, 
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Simple convenience method for single-turn chat.
        
        Args:
            user_message: The user's message
            system_message: Optional system message to set context
            **kwargs: Additional parameters passed to chat_completion
            
        Returns:
            The assistant's response as a string
        """
        messages = []
        
        if system_message:
            messages.append(Message(role=Role.SYSTEM, content=system_message))
        
        messages.append(Message(role=Role.USER, content=user_message))
        
        response = self.chat_completion(messages, **kwargs)
        
        if response.choices:
            return response.choices[0].message.content
        else:
            return ""
    
    def _parse_completion_response(self, data: Dict[str, Any]) -> CompletionResponse:
        """Parse the API response into a CompletionResponse dataclass."""
        choices = []
        for choice_data in data["choices"]:
            message_data = choice_data["message"]
            message = Message(
                role=Role(message_data["role"]),
                content=message_data["content"]
            )
            choice = CompletionChoice(
                index=choice_data["index"],
                message=message,
                finish_reason=choice_data.get("finish_reason")
            )
            choices.append(choice)
        
        usage_data = data["usage"]
        usage = CompletionUsage(
            prompt_tokens=usage_data["prompt_tokens"],
            completion_tokens=usage_data["completion_tokens"],
            total_tokens=usage_data["total_tokens"]
        )
        
        return CompletionResponse(
            id=data["id"],
            object=data["object"],
            created=data["created"],
            model=data["model"],
            choices=choices,
            usage=usage
        )
    
    def _parse_models_response(self, data: Dict[str, Any]) -> ModelsResponse:
        """Parse the models API response into a ModelsResponse dataclass."""
        models = []
        for model_data in data["data"]:
            model = ModelInfo(
                id=model_data["id"],
                object=model_data.get("object", "model"),
                created=model_data.get("created", 0),
                owned_by=model_data.get("owned_by", "unknown")
            )
            models.append(model)
        
        return ModelsResponse(
            object=data["object"],
            data=models
        )
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close the session."""
        self.session.close()