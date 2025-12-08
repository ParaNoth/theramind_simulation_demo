"""
Therapy Selection 模块
用于根据上一轮会话历史和治疗方式，选择新的治疗方式
"""

from typing import Dict, Any, Optional
from .base_llm_client import BaseLLMClient


class TherapySelection(BaseLLMClient):
    """治疗方式选择器，使用 LLM 根据历史记录选择新的治疗方式"""
    
    def _format_prompt(self, last_dialogs: str, last_therapy: str) -> str:
        """
        将上一轮会话历史和治疗方式替换到 prompt 模板中
        
        Args:
            last_dialogs: 上一轮会话的历史记录
            last_therapy: 上一轮使用的治疗方式
        
        Returns:
            格式化后的 prompt
        """
        formatted_prompt = self.prompt
        if "{last_dialogs}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{last_dialogs}", last_dialogs)
        if "{last_therapy}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{last_therapy}", last_therapy)
        
        return formatted_prompt
    
    def select(
        self,
        last_dialogs: str,
        last_therapy: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        根据上一轮会话历史和治疗方式选择新的治疗方式
        
        Args:
            last_dialogs: 上一轮会话的历史记录
            last_therapy: 上一轮使用的治疗方式
            temperature: 温度参数（0-2），控制随机性
            max_tokens: 最大生成 token 数
            top_p: 核采样参数
            frequency_penalty: 频率惩罚（-2.0 到 2.0）
            presence_penalty: 存在惩罚（-2.0 到 2.0）
            stop: 停止序列列表
            **kwargs: 其他推理参数
        
        Returns:
            反序列化后的 JSON 结果（字典格式），包含 new_therapy 和 reason 字段
        """
        # 格式化 prompt
        formatted_prompt = self._format_prompt(last_dialogs, last_therapy)
        
        # 调用 LLM
        content = self._call_llm(
            formatted_prompt=formatted_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            **kwargs
        )
        
        # 解析 JSON 字符串
        result = self._parse_json_response(content)
        
        return result


# 使用示例
if __name__ == "__main__":
    # 示例 1: 基本使用
    # 读取 prompt 文件
    with open("prompts/therapy_selection/therapy_selection_en.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    
    # 初始化治疗方式选择器（client 会在内部自动创建，api_key 从环境变量读取）
    selector = TherapySelection(
        model="openai/gpt-4o",
        prompt=prompt
    )
    
    # 选择新的治疗方式
    try:
        result = selector.select(
            last_dialogs="Counselor: How are you feeling today?\nClient: I'm still very anxious about the exam.",
            last_therapy="Cognitive Restructuring",
            temperature=0.7,
            max_tokens=200
        )
        print("选择结果:", result)
        print("新治疗方式:", result.get("new_therapy"))
        print("选择原因:", result.get("reason"))
    except Exception as e:
        print(f"错误: {e}")
    
    # 示例 2: 使用不同的推理参数
    try:
        result = selector.select(
            last_dialogs="Counselor: Let's try some breathing exercises.\nClient: That helped me feel calmer.",
            last_therapy="Breathing Exercise",
            temperature=0.3,  # 更低的温度，更确定性的输出
            max_tokens=150
        )
        print("\n选择结果:", result)
    except Exception as e:
        print(f"错误: {e}")

