"""
Counselor Agent 模块
用于生成心理咨询师的回复，使用 LLM 基于患者输入、记忆、情绪等信息生成专业的咨询回复
"""

from typing import Dict, Any, Optional, Union
from .base_llm_client import BaseLLMClient


class CounselorAgent(BaseLLMClient):
    """心理咨询师代理，使用 LLM 生成专业的咨询回复"""
    
    def generate_response(
        self,
        utter: str,
        memory_result: str,
        primary_emotion: str,
        emotional_intensity: Union[float, str],
        current_therapy: str,
        current_stage: str,
        current_strategy_text: str,
        session_memory: str,
        current_strategy: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成心理咨询师的回复
        
        Args:
            utter: 用户当前的输入（utterance）
            memory_result: 记忆总结
            primary_emotion: 来访者主要情绪
            emotional_intensity: 情绪强度（float 或 str）
            current_therapy: 当前治疗方案
            current_stage: 当前治疗阶段
            current_strategy_text: 当前治疗方案说明
            session_memory: 到目前为止的历史记录
            current_strategy: 当前策略（可选，如果未提供则使用 current_strategy_text）
            temperature: 温度参数（0-2），控制随机性
            max_tokens: 最大生成 token 数
            top_p: 核采样参数
            frequency_penalty: 频率惩罚（-2.0 到 2.0）
            presence_penalty: 存在惩罚（-2.0 到 2.0）
            stop: 停止序列列表
            **kwargs: 其他推理参数
        
        Returns:
            反序列化后的 JSON 结果（字典格式）
        """
        # 格式化 prompt
        formatted_prompt = self._format_prompt(
            utter=utter,
            memory_result=memory_result,
            primary_emotion=primary_emotion,
            emotional_intensity=emotional_intensity,
            current_therapy=current_therapy,
            current_stage=current_stage,
            current_strategy=current_strategy or current_strategy_text,
            current_strategy_text=current_strategy_text,
            session_memory=session_memory
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
        memory_result: str,
        primary_emotion: str,
        emotional_intensity: Union[float, str],
        current_therapy: str,
        current_stage: str,
        current_strategy: str,
        current_strategy_text: str,
        session_memory: str
    ) -> str:
        """
        将参数替换到 prompt 模板中
        
        Args:
            utter: 用户当前的输入
            memory_result: 记忆总结
            primary_emotion: 来访者主要情绪
            emotional_intensity: 情绪强度
            current_therapy: 当前治疗方案
            current_stage: 当前治疗阶段
            current_strategy: 当前策略
            current_strategy_text: 当前策略说明
            session_memory: 历史记录
        
        Returns:
            格式化后的 prompt
        """
        formatted_prompt = self.prompt
        
        # 替换所有占位符
        replacements = {
            "{patient_input}": str(utter),
            "{memory_result}": str(memory_result),
            "{primary_emotion}": str(primary_emotion),
            "{emotional_intensity}": str(emotional_intensity),
            "{current_therapy}": str(current_therapy),
            "{current_stage}": str(current_stage),
            "{current_strategy}": str(current_strategy),
            "{current_strategy_text}": str(current_strategy_text),
            "{session_memory}": str(session_memory)
        }
        
        for placeholder, value in replacements.items():
            formatted_prompt = formatted_prompt.replace(placeholder, value)
        
        return formatted_prompt


# 使用示例
if __name__ == "__main__":
    # 示例 1: 基本使用
    # 读取 prompt 文件
    with open("prompts/counselor/counselor_en.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    
    # 初始化咨询师代理（client 会在内部自动创建，api_key 从环境变量读取）
    counselor = CounselorAgent(
        model="openai/gpt-4o",
        prompt=prompt
    )
    
    # 生成回复
    try:
        result = counselor.generate_response(
            utter="I feel really anxious about the upcoming exam.",
            memory_result="Patient has been struggling with anxiety for 3 months.",
            primary_emotion="anxiety",
            emotional_intensity=0.8,
            current_therapy="CBT",
            current_stage="exploration",
            current_strategy_text="Use empathetic listening and validate emotions.",
            session_memory="Previous conversation about work stress.",
            temperature=0.7,
            max_tokens=200
        )
        print("咨询师回复:", result)
        print("回复内容:", result.get("counselor_response"))
    except Exception as e:
        print(f"错误: {e}")
    
    # 示例 2: 使用不同的推理参数
    try:
        result = counselor.generate_response(
            utter="I'm feeling better today.",
            memory_result="Patient showed improvement in mood.",
            primary_emotion="neutral",
            emotional_intensity="low",
            current_therapy="CBT",
            current_stage="consolidation",
            current_strategy_text="Reinforce positive changes.",
            session_memory="Previous sessions focused on coping strategies.",
            temperature=0.5,  # 更低的温度，更确定性的输出
            max_tokens=150
        )
        print("\n咨询师回复:", result)
    except Exception as e:
        print(f"错误: {e}")

