"""
OpenRouter API 客户端类
用于向 OpenRouter API 发送请求，支持灵活的模型和参数配置
"""

import requests
import json
from typing import List, Dict, Optional, Any, Iterator
import os


class OpenRouterClient:
    """OpenRouter API 客户端类，支持多种模型和可配置参数"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1",
        default_model: Optional[str] = None,
        default_temperature: float = 0.7,
        default_max_tokens: Optional[int] = None,
        timeout: int = 60
    ):
        """
        初始化 OpenRouterClient 实例
        
        Args:
            api_key: OpenRouter API 密钥。如果为 None，将从环境变量 OPENROUTER_API_KEY 读取
            base_url: OpenRouter API 的基础 URL
            default_model: 默认使用的模型名称（如 'openai/gpt-4o', 'anthropic/claude-3-opus'）
            default_temperature: 默认温度参数（0-2）
            default_max_tokens: 默认最大生成 token 数
            timeout: 请求超时时间（秒）
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("API key 未提供，请通过参数传入或设置环境变量 OPENROUTER_API_KEY")
        
        self.base_url = base_url
        self.default_model = default_model
        self.default_temperature = default_temperature
        self.default_max_tokens = default_max_tokens
        self.timeout = timeout
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repo",  # 可选：用于统计
            "X-Title": "TheraMind Simulation Demo"  # 可选：应用名称
        }
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[List[str]] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送聊天请求到 OpenRouter API
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 模型名称（如 'openai/gpt-4o'）。如果为 None，使用默认模型
            temperature: 温度参数（0-2），控制随机性
            max_tokens: 最大生成 token 数
            top_p: 核采样参数
            frequency_penalty: 频率惩罚（-2.0 到 2.0）
            presence_penalty: 存在惩罚（-2.0 到 2.0）
            stop: 停止序列列表
            stream: 是否使用流式响应
            **kwargs: 其他 OpenRouter API 支持的参数
        
        Returns:
            API 响应的 JSON 数据
        """
        url = f"{self.base_url}/chat/completions"
        
        # 使用提供的参数或默认值
        model = model or self.default_model
        if not model:
            raise ValueError("模型名称未指定，请通过 model 参数传入或设置 default_model")
        
        payload = {
            "model": model,
            "messages": messages,
        }
        
        # 添加可选参数
        if temperature is not None:
            payload["temperature"] = temperature
        elif self.default_temperature is not None:
            payload["temperature"] = self.default_temperature
        
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        elif self.default_max_tokens is not None:
            payload["max_tokens"] = self.default_max_tokens
        
        if top_p is not None:
            payload["top_p"] = top_p
        
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        
        if stop is not None:
            payload["stop"] = stop
        
        if stream:
            payload["stream"] = True
        
        # 添加其他自定义参数
        payload.update(kwargs)
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout,
                stream=stream
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_stream_response(response)
            else:
                return response.json()
        
        except requests.exceptions.RequestException as e:
            error_msg = f"请求失败: {str(e)}"
            if hasattr(e.response, 'text'):
                error_msg += f"\n响应内容: {e.response.text}"
            raise Exception(error_msg) from e
    
    def _handle_stream_response(self, response: requests.Response) -> Iterator[Dict[str, Any]]:
        """
        处理流式响应
        
        Args:
            response: requests Response 对象
        
        Yields:
            每个数据块的 JSON 数据
        """
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    data_str = line_text[6:]  # 移除 'data: ' 前缀
                    if data_str.strip() == '[DONE]':
                        break
                    try:
                        yield json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
    
    def get_models(self) -> Dict[str, Any]:
        """
        获取可用的模型列表
        
        Returns:
            包含模型列表的字典
        """
        url = f"{self.base_url}/models"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"获取模型列表失败: {str(e)}"
            if hasattr(e.response, 'text'):
                error_msg += f"\n响应内容: {e.response.text}"
            raise Exception(error_msg) from e
    
    def get_usage(self) -> Dict[str, Any]:
        """
        获取 API 使用情况
        
        Returns:
            包含使用统计的字典
        """
        url = f"{self.base_url}/usage"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"获取使用情况失败: {str(e)}"
            if hasattr(e.response, 'text'):
                error_msg += f"\n响应内容: {e.response.text}"
            raise Exception(error_msg) from e
    
    def set_default_model(self, model: str):
        """设置默认模型"""
        self.default_model = model
    
    def set_default_temperature(self, temperature: float):
        """设置默认温度"""
        self.default_temperature = temperature
    
    def set_default_max_tokens(self, max_tokens: int):
        """设置默认最大 token 数"""
        self.default_max_tokens = max_tokens


# 使用示例
if __name__ == "__main__":
    # 示例 1: 基本使用
    client = OpenRouterClient(
        api_key="your-api-key-here",  # 或从环境变量读取
        default_model="openai/gpt-4o"
    )
    
    messages = [
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ]
    
    try:
        response = client.chat(messages=messages)
        print("响应:", response)
        print("内容:", response["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"错误: {e}")
    
    # 示例 2: 使用不同模型和参数
    try:
        response = client.chat(
            messages=messages,
            model="anthropic/claude-3-opus",
            temperature=0.9,
            max_tokens=200
        )
        print("响应:", response)
    except Exception as e:
        print(f"错误: {e}")
    
    # 示例 3: 流式响应
    try:
        for chunk in client.chat(
            messages=messages,
            model="openai/gpt-4o",
            stream=True
        ):
            if "choices" in chunk and len(chunk["choices"]) > 0:
                delta = chunk["choices"][0].get("delta", {})
                if "content" in delta:
                    print(delta["content"], end="", flush=True)
        print()  # 换行
    except Exception as e:
        print(f"错误: {e}")


# ============================================================================
# 基于 OpenAI SDK 的实现
# ============================================================================

try:
    from openai import OpenAI
    OPENAI_SDK_AVAILABLE = True
except ImportError:
    OPENAI_SDK_AVAILABLE = False


class OpenRouterClientSDK:
    """基于 OpenAI SDK 的 OpenRouter API 客户端类，支持多种模型和可配置参数"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1",
        default_model: Optional[str] = None,
        default_temperature: float = 0.7,
        default_max_tokens: Optional[int] = None,
        timeout: int = 60,
        http_client: Optional[Any] = None
    ):
        """
        初始化 OpenRouterClientSDK 实例
        
        Args:
            api_key: OpenRouter API 密钥。如果为 None，将从环境变量 OPENROUTER_API_KEY 读取
            base_url: OpenRouter API 的基础 URL
            default_model: 默认使用的模型名称（如 'openai/gpt-4o', 'anthropic/claude-3-opus'）
            default_temperature: 默认温度参数（0-2）
            default_max_tokens: 默认最大生成 token 数
            timeout: 请求超时时间（秒）
            http_client: 自定义 HTTP 客户端（可选）
        """
        if not OPENAI_SDK_AVAILABLE:
            raise ImportError(
                "OpenAI SDK 未安装。请运行: pip install openai"
            )
        
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("API key 未提供，请通过参数传入或设置环境变量 OPENROUTER_API_KEY")
        
        self.base_url = base_url
        self.default_model = default_model
        self.default_temperature = default_temperature
        self.default_max_tokens = default_max_tokens
        self.timeout = timeout
        
        # 初始化 OpenAI 客户端，配置为使用 OpenRouter
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url,
            timeout=timeout,
            http_client=http_client,
            default_headers={
                "HTTP-Referer": "https://github.com/your-repo",  # 可选：用于统计
                "X-Title": "TheraMind Simulation Demo"  # 可选：应用名称
            }
        )
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[List[str]] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        发送聊天请求到 OpenRouter API
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 模型名称（如 'openai/gpt-4o'）。如果为 None，使用默认模型
            temperature: 温度参数（0-2），控制随机性
            max_tokens: 最大生成 token 数
            top_p: 核采样参数
            frequency_penalty: 频率惩罚（-2.0 到 2.0）
            presence_penalty: 存在惩罚（-2.0 到 2.0）
            stop: 停止序列列表
            stream: 是否使用流式响应
            **kwargs: 其他 OpenRouter API 支持的参数
        
        Returns:
            如果 stream=False，返回 ChatCompletion 对象
            如果 stream=True，返回流式响应迭代器
        """
        # 使用提供的参数或默认值
        model = model or self.default_model
        if not model:
            raise ValueError("模型名称未指定，请通过 model 参数传入或设置 default_model")
        
        # 构建参数字典
        params = {
            "model": model,
            "messages": messages,
        }
        
        # 添加可选参数
        if temperature is not None:
            params["temperature"] = temperature
        elif self.default_temperature is not None:
            params["temperature"] = self.default_temperature
        
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        elif self.default_max_tokens is not None:
            params["max_tokens"] = self.default_max_tokens
        
        if top_p is not None:
            params["top_p"] = top_p
        
        if frequency_penalty is not None:
            params["frequency_penalty"] = frequency_penalty
        
        if presence_penalty is not None:
            params["presence_penalty"] = presence_penalty
        
        if stop is not None:
            params["stop"] = stop
        
        if stream:
            params["stream"] = True
        
        # 添加其他自定义参数
        params.update(kwargs)
        
        try:
            if stream:
                return self.client.chat.completions.create(**params)
            else:
                return self.client.chat.completions.create(**params)
        except Exception as e:
            error_msg = f"请求失败: {str(e)}"
            raise Exception(error_msg) from e
    
    def get_models(self) -> Any:
        """
        获取可用的模型列表
        
        Returns:
            包含模型列表的响应对象
        """
        try:
            # 使用 OpenAI SDK 的方式获取模型列表
            # 注意：OpenRouter 的模型列表需要通过 REST API 获取
            import requests
            url = f"{self.base_url}/models"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            error_msg = f"获取模型列表失败: {str(e)}"
            raise Exception(error_msg) from e
    
    def get_usage(self) -> Any:
        """
        获取 API 使用情况
        
        Returns:
            包含使用统计的响应对象
        """
        try:
            import requests
            url = f"{self.base_url}/usage"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            error_msg = f"获取使用情况失败: {str(e)}"
            raise Exception(error_msg) from e
    
    def set_default_model(self, model: str):
        """设置默认模型"""
        self.default_model = model
    
    def set_default_temperature(self, temperature: float):
        """设置默认温度"""
        self.default_temperature = temperature
    
    def set_default_max_tokens(self, max_tokens: int):
        """设置默认最大 token 数"""
        self.default_max_tokens = max_tokens


# 基于 OpenAI SDK 的使用示例
if __name__ == "__main__":
    print("\n" + "="*50)
    print("基于 OpenAI SDK 的实现示例")
    print("="*50 + "\n")
    
    # 示例 1: 基本使用
    try:
        client_sdk = OpenRouterClientSDK(
            api_key="your-api-key-here",  # 或从环境变量读取
            default_model="openai/gpt-4o"
        )
        
        messages = [
            {"role": "user", "content": "你好，请介绍一下你自己"}
        ]
        
        response = client_sdk.chat(messages=messages)
        print("响应类型:", type(response))
        print("内容:", response.choices[0].message.content)
        print("使用 token 数:", response.usage.total_tokens)
    except Exception as e:
        print(f"错误: {e}")
    
    # 示例 2: 使用不同模型和参数
    try:
        client_sdk = OpenRouterClientSDK(
            api_key="your-api-key-here",
            default_model="openai/gpt-4o"
        )
        
        messages = [
            {"role": "user", "content": "用一句话解释量子计算"}
        ]
        
        response = client_sdk.chat(
            messages=messages,
            model="anthropic/claude-3-opus",
            temperature=0.9,
            max_tokens=200
        )
        print("响应:", response.choices[0].message.content)
    except Exception as e:
        print(f"错误: {e}")
    
    # 示例 3: 流式响应
    try:
        client_sdk = OpenRouterClientSDK(
            api_key="your-api-key-here",
            default_model="openai/gpt-4o"
        )
        
        messages = [
            {"role": "user", "content": "请写一首关于AI的短诗"}
        ]
        
        stream = client_sdk.chat(
            messages=messages,
            model="openai/gpt-4o",
            stream=True
        )
        
        print("流式响应:")
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print()  # 换行
    except Exception as e:
        print(f"错误: {e}")

