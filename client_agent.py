"""
Client Agent 模块
用于生成来访者的回复，使用 LLM 模拟来访者的反应
"""

from typing import Dict, Any, Optional
from module.base_llm_client import BaseLLMClient


class ClientAgent(BaseLLMClient):
    """来访者代理，使用 LLM 生成来访者的回复"""
    
    def generate_response(
        self,
        client_information: str,
        dialogue_count: int,
        session_number: int,
        therapist_message: str,
        historical_dialogs: str,
        current_therapy: str,
        all_dialogs: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成来访者的回复
        
        Args:
            client_information: 来访者个人信息
            dialogue_count: 对话轮数
            session_number: 会话编号
            therapist_message: 咨询师刚刚的回复
            historical_dialogs: 当前咨询的历史记录
            current_therapy: 当前的治疗方案
            all_dialogs: 所有的历史记录
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
            client_information=client_information,
            dialogue_count=dialogue_count,
            session_number=session_number,
            therapist_message=therapist_message,
            historical_dialogs=historical_dialogs,
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
        
        # 解析 JSON 字符串
        result = self._parse_json_response(content)
        
        return result
    
    def _format_prompt(
        self,
        client_information: str,
        dialogue_count: int,
        session_number: int,
        therapist_message: str,
        historical_dialogs: str,
        current_therapy: str,
        all_dialogs: str
    ) -> str:
        """
        将参数替换到 prompt 模板中
        
        Args:
            client_information: 来访者个人信息
            dialogue_count: 对话轮数
            session_number: 会话编号
            therapist_message: 咨询师刚刚的回复
            historical_dialogs: 当前咨询的历史记录
            current_therapy: 当前的治疗方案
            all_dialogs: 所有的历史记录
        
        Returns:
            格式化后的 prompt
        """
        formatted_prompt = self.prompt
        formatted_prompt = formatted_prompt.replace("{client_information}", str(client_information))
        formatted_prompt = formatted_prompt.replace("{dialogue_count}", str(dialogue_count))
        formatted_prompt = formatted_prompt.replace("{session_number}", str(session_number))
        formatted_prompt = formatted_prompt.replace("{therapist_message}", str(therapist_message))
        formatted_prompt = formatted_prompt.replace("{historical_dialogs}", str(historical_dialogs))
        formatted_prompt = formatted_prompt.replace("{current_therapy}", str(current_therapy))
        formatted_prompt = formatted_prompt.replace("{all_dialogs}", str(all_dialogs))
        
        return formatted_prompt


# 使用示例
if __name__ == "__main__":
    # 示例 1: 基本使用
    # 读取 prompt 文件
    with open("prompts/client/client_en.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    
    # 初始化来访者代理（client 会在内部自动创建，api_key 从环境变量读取）
    client_agent = ClientAgent(
        model="openai/gpt-4o",
        prompt=prompt
    )
    
    # 生成来访者回复
    try:
        result = client_agent.generate_response(
            client_information="A 25-year-old student experiencing anxiety about exams",
            dialogue_count=3,
            session_number=1,
            therapist_message="I understand you're feeling anxious. Can you tell me more about what specifically worries you about the exam?",
            historical_dialogs="Therapist: How are you feeling today?\nClient: I'm anxious about my upcoming exam.",
            current_therapy="Cognitive Behavioral Therapy (CBT)",
            all_dialogs="Session 1, Round 1: Initial greeting and assessment",
            temperature=0.7,
            max_tokens=200
        )
        print("来访者回复:", result)
        print("回复内容:", result.get("patient_response"))
    except Exception as e:
        print(f"错误: {e}")
    
    # 示例 2: 使用不同的推理参数
    try:
        result = client_agent.generate_response(
            client_information="A 30-year-old professional dealing with work stress",
            dialogue_count=5,
            session_number=2,
            therapist_message="Let's explore some coping strategies for your work stress.",
            historical_dialogs="Previous discussions about work-life balance",
            current_therapy="CBT with focus on stress management",
            all_dialogs="Complete session history from previous sessions",
            temperature=0.5,  # 更低的温度，更确定性的输出
            max_tokens=150
        )
        print("\n来访者回复:", result)
    except Exception as e:
        print(f"错误: {e}")

