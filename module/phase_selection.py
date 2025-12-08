"""
Phase Selection 模块
用于分析当前治疗阶段，使用 LLM 进行阶段分析和总结
"""

from typing import Optional
from .base_llm_client import BaseLLMClient


class PhaseSelection(BaseLLMClient):
    """阶段选择器，使用 LLM 分析当前治疗阶段"""
    
    def analyze_phase(
        self,
        utter: str,
        current_therapy: str,
        all_dialogs: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[list] = None,
        **kwargs
    ) -> str:
        """
        分析当前治疗阶段
        
        Args:
            utter: 用户的当前输入（utterance）
            current_therapy: 当前治疗内容
            all_dialogs: 所有历史对话记录
            temperature: 温度参数（0-2），控制随机性
            max_tokens: 最大生成 token 数
            top_p: 核采样参数
            frequency_penalty: 频率惩罚（-2.0 到 2.0）
            presence_penalty: 存在惩罚（-2.0 到 2.0）
            stop: 停止序列列表
            **kwargs: 其他推理参数
        
        Returns:
            分析结果（字符串格式的段落）
        """
        # 格式化 prompt
        formatted_prompt = self._format_prompt(
            utter=utter,
            current_therapy=current_therapy,
            all_dialogs=all_dialogs
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
        
        # 返回结果（去除首尾空白）
        result = content.strip()
        
        return result
    
    def _format_prompt(
        self,
        utter: str,
        current_therapy: str,
        all_dialogs: str
    ) -> str:
        """
        将用户输入和历史对话替换到 prompt 模板中
        
        Args:
            utter: 用户的当前输入（utterance）
            current_therapy: 当前治疗内容
            all_dialogs: 所有历史对话记录
        
        Returns:
            格式化后的 prompt
        """
        formatted_prompt = self.prompt
        
        # 替换各个占位符
        if "{current_therapy}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{current_therapy}", current_therapy)
        
        if "{all_dialogs}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{all_dialogs}", all_dialogs)
        
        return formatted_prompt


# 使用示例
if __name__ == "__main__":
    # 示例 1: 基本使用
    # 读取 prompt 文件
    with open("prompts/phase_selection/phase_selection_en.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    
    # 初始化阶段选择器（client 会在内部自动创建，api_key 从环境变量读取）
    phase_selector = PhaseSelection(
        model="openai/gpt-4o",
        prompt=prompt
    )
    
    # 分析阶段
    try:
        result = phase_selector.analyze_phase(
            utter="I've been practicing the breathing exercises you taught me, and they help a bit.",
            current_therapy="Cognitive Behavioral Therapy focusing on anxiety management through breathing exercises and thought challenging",
            all_dialogs="Therapist: How have you been feeling lately?\nPatient: I've been very anxious about work.\nTherapist: Can you tell me more about what triggers this anxiety?\nPatient: I think it's the pressure from my boss.",
            temperature=0.7,
            max_tokens=200
        )
        print("阶段分析结果:", result)
    except Exception as e:
        print(f"错误: {e}")
    
    # 示例 2: 使用不同的推理参数
    try:
        result = phase_selector.analyze_phase(
            utter="I'm starting to understand my thought patterns better now.",
            current_therapy="CBT session focusing on identifying and challenging negative thought patterns",
            all_dialogs="Therapist: Let's explore your thoughts about this situation.\nPatient: I always think the worst will happen.\nTherapist: That's a common pattern. Let's work on challenging these thoughts.",
            temperature=0.5,  # 更低的温度，更确定性的输出
            max_tokens=150
        )
        print("\n阶段分析结果:", result)
    except Exception as e:
        print(f"错误: {e}")

