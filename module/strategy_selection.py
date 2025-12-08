"""
Strategy Selection 模块
用于根据用户输入和状态信息选择响应策略，使用 LLM 进行策略选择
"""

from typing import Dict, Any, Optional, Union
from .base_llm_client import BaseLLMClient


class StrategySelection(BaseLLMClient):
    """策略选择器，使用 LLM 根据用户输入和状态信息选择响应策略"""
    
    def select_strategy(
        self,
        utter: str,
        primary_emotion: str,
        emotional_intensity: Union[float, str],
        resistance: bool,
        session_strategy_memory: Optional[list[str]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        根据用户输入和状态信息选择响应策略
        
        Args:
            utter: 用户的当前输入（utterance）
            primary_emotion: 用户的主要情感（字符串）
            emotional_intensity: 情感强度（浮点数或字符串，范围 0-1）
            resistance: 用户是否在抗拒或偏离话题（布尔值）
            session_strategy_memory: 本次会话中已使用的策略记录列表（可选，默认为空列表）
            temperature: 温度参数（0-2），控制随机性
            max_tokens: 最大生成 token 数
            top_p: 核采样参数
            frequency_penalty: 频率惩罚（-2.0 到 2.0）
            presence_penalty: 存在惩罚（-2.0 到 2.0）
            stop: 停止序列列表
            **kwargs: 其他推理参数
        
        Returns:
            反序列化后的 JSON 结果（字典格式），包含 strategy 和 strategy_text
        """
        # 格式化 prompt（如果 session_strategy_memory 为 None，则使用空列表）
        if session_strategy_memory is None:
            session_strategy_memory = []
        formatted_prompt = self._format_prompt(
            utter=utter,
            primary_emotion=primary_emotion,
            emotional_intensity=emotional_intensity,
            resistance=resistance,
            session_strategy_memory=session_strategy_memory
        )
        
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
    
    def _format_prompt(
        self,
        utter: str,
        primary_emotion: str,
        emotional_intensity: Union[float, str],
        resistance: bool,
        session_strategy_memory: Optional[list[str]] = None
    ) -> str:
        """
        将用户输入和状态信息替换到 prompt 模板中
        
        Args:
            utter: 用户的当前输入（utterance）
            primary_emotion: 用户的主要情感（字符串）
            emotional_intensity: 情感强度（浮点数或字符串）
            resistance: 用户是否在抗拒或偏离话题（布尔值）
            session_strategy_memory: 本次会话中已使用的策略记录列表
        
        Returns:
            格式化后的 prompt
        """
        formatted_prompt = self.prompt
        
        # 替换各个占位符
        if "{patient_input}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{patient_input}", utter)
        
        if "{primary_emotion}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{primary_emotion}", str(primary_emotion))
        
        if "{emotional_intensity}" in formatted_prompt:
            # 确保 emotional_intensity 是字符串格式
            intensity_str = str(emotional_intensity)
            formatted_prompt = formatted_prompt.replace("{emotional_intensity}", intensity_str)
        
        # 处理 resistance 占位符
        # prompt 中可能是 {"Yes" if is_rejecting else "No"} 这样的格式
        # 需要替换为实际的 "Yes" 或 "No"
        resistance_str = "Yes" if resistance else "No"
        if '{"Yes" if is_rejecting else "No"}' in formatted_prompt:
            formatted_prompt = formatted_prompt.replace('{"Yes" if is_rejecting else "No"}', resistance_str)
        elif "{is_rejecting}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{is_rejecting}", resistance_str)
        
        if "{session_strategy_memory}" in formatted_prompt:
            # 将策略列表转换为字符串（用逗号和空格连接）
            if session_strategy_memory is None:
                session_strategy_memory = []
            memory_str = ", ".join(session_strategy_memory) if session_strategy_memory else ""
            formatted_prompt = formatted_prompt.replace("{session_strategy_memory}", memory_str)
        
        return formatted_prompt


# 使用示例
if __name__ == "__main__":
    # 示例 1: 基本使用
    # 读取 prompt 文件
    with open("prompts/strategy_selection/strategy_selection_en.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    
    # 初始化策略选择器（client 会在内部自动创建，api_key 从环境变量读取）
    strategy_selector = StrategySelection(
        model="openai/gpt-4o",
        prompt=prompt
    )
    
    # 选择策略
    try:
        result = strategy_selector.select_strategy(
            utter="I feel really anxious about the upcoming exam.",
            primary_emotion="fear",
            emotional_intensity=0.8,
            resistance=False,
            session_strategy_memory=[],
            temperature=0.7,
            max_tokens=200
        )
        print("策略选择结果:", result)
        print("选择的策略:", result.get("strategy"))
        print("策略文本:", result.get("strategy_text"))
    except Exception as e:
        print(f"错误: {e}")
    
    # 示例 2: 用户有抗拒情绪的情况
    try:
        result = strategy_selector.select_strategy(
            utter="I don't want to talk about this anymore.",
            primary_emotion="anger",
            emotional_intensity=0.6,
            resistance=True,
            session_strategy_memory=["Restatement", "Reflection of Feelings"],
            temperature=0.7,
            max_tokens=200
        )
        print("\n策略选择结果:", result)
        print("选择的策略:", result.get("strategy"))
        print("策略文本:", result.get("strategy_text"))
    except Exception as e:
        print(f"错误: {e}")

