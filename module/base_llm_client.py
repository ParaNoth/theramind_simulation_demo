"""
基础 LLM 客户端模块
提供通用的 LLM 调用功能，供子类继承使用
可用于分类、检测、聊天等多种 LLM 应用场景
"""

import os
import json
import re
from typing import Dict, Any, Optional
from .openrouter_client import OpenRouterClient


class BaseLLMClient:
    """基础 LLM 客户端类，提供通用的初始化和 LLM 调用功能"""
    
    def __init__(
        self,
        model: str,
        prompt: str,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout: int = 60
    ):
        """
        初始化基础客户端实例
        
        Args:
            model: 要使用的模型名称（如 'openai/gpt-4o', 'anthropic/claude-3-opus'）
            prompt: prompt 模板内容，应包含 {patient_input} 或类似的占位符
            base_url: OpenRouter API 的基础 URL（可选，默认值：https://openrouter.ai/api/v1）
            timeout: 请求超时时间（秒，可选，默认值：60）
        """
        # 从环境变量读取 API key
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        # 内部初始化 OpenRouterClient
        self.client = OpenRouterClient(
            api_key=api_key,
            base_url=base_url,
            default_model=model,
            timeout=timeout
        )
        self.model = model
        self.prompt = prompt
    
    def _format_prompt(self, utter: str) -> str:
        """
        将用户输入替换到 prompt 模板中
        
        Args:
            utter: 用户的当前输入（utterance）
        
        Returns:
            格式化后的 prompt
        """
        formatted_prompt = self.prompt
        if "{patient_input}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{patient_input}", utter)
        elif "{utter}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{utter}", utter)
        elif "{input}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{input}", utter)
        else:
            # 如果没有找到占位符，直接追加用户输入
            formatted_prompt = f"{self.prompt}\n\n用户输入: {utter}"
        
        return formatted_prompt
    
    def _call_llm(
        self,
        formatted_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[list] = None,
        **kwargs
    ) -> str:
        """
        调用 LLM 并返回响应内容
        
        Args:
            formatted_prompt: 格式化后的 prompt
            temperature: 温度参数（0-2），控制随机性
            max_tokens: 最大生成 token 数
            top_p: 核采样参数
            frequency_penalty: 频率惩罚（-2.0 到 2.0）
            presence_penalty: 存在惩罚（-2.0 到 2.0）
            stop: 停止序列列表
            **kwargs: 其他推理参数
        
        Returns:
            LLM 返回的文本内容
        """
        # 构建消息
        messages = [
            {"role": "user", "content": formatted_prompt}
        ]
        
        # 调用 LLM
        response = self.client.chat(
            messages=messages,
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            **kwargs
        )
        
        # 提取响应内容
        if isinstance(response, dict):
            content = response["choices"][0]["message"]["content"]
        else:
            # 如果是 OpenAI SDK 返回的对象
            content = response.choices[0].message.content
        
        return content
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """
        从 LLM 响应中解析 JSON
        
        Args:
            content: LLM 返回的文本内容
        
        Returns:
            解析后的 JSON 字典
        """
        # 尝试直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # 如果直接解析失败，尝试提取 JSON 部分
        # 查找 JSON 对象（可能被代码块包裹）
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',  # 被 ```json ... ``` 包裹
            r'```\s*(\{.*?\})\s*```',      # 被 ``` ... ``` 包裹
            r'(\{.*\})',                    # 直接查找 JSON 对象
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue
        
        # 如果所有方法都失败，抛出异常
        raise ValueError(
            f"无法从 LLM 响应中解析 JSON。响应内容: {content}"
        )

