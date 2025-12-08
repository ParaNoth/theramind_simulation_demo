"""
Post Session Evaluation 模块
用于对整个咨询会话进行评估，使用 LLM 对咨询师的表现进行评分
"""

from typing import Dict, Any, Optional
from .base_llm_client import BaseLLMClient


class PostSessionEvaluation(BaseLLMClient):
    """会话后评估器，使用 LLM 对整个咨询会话进行评估"""
    
    def _format_prompt(self, session_dialogs: str, session_name: Optional[str] = None) -> str:
        """
        将会话对话历史替换到 prompt 模板中
        
        Args:
            session_dialogs: 所有会话的对话历史
            session_name: 会话名称（可选，用于新格式的 prompt）
        
        Returns:
            格式化后的 prompt
        """
        formatted_prompt = self.prompt
        
        # 支持新格式：{session_name} 和 {session_content["dialogs"]}
        if "{session_name}" in formatted_prompt:
            session_name_str = session_name if session_name else "the session"
            formatted_prompt = formatted_prompt.replace("{session_name}", session_name_str)
        
        if "{session_content[\"dialogs\"]}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{session_content[\"dialogs\"]}", session_dialogs)
        elif "{session_dialogs}" in formatted_prompt:
            # 向后兼容旧格式
            formatted_prompt = formatted_prompt.replace("{session_dialogs}", session_dialogs)
        else:
            # 如果没有找到占位符，直接追加会话对话
            formatted_prompt = f"{self.prompt}\n\n心理咨询记录: {session_dialogs}"
        
        return formatted_prompt
    
    def evaluate(
        self,
        session_dialogs: str,
        session_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        对整个咨询会话进行评估
        
        Args:
            session_dialogs: 所有会话的对话历史记录
            session_name: 会话名称（可选，用于新格式的 prompt）
            temperature: 温度参数（0-2），控制随机性
            max_tokens: 最大生成 token 数
            top_p: 核采样参数
            frequency_penalty: 频率惩罚（-2.0 到 2.0）
            presence_penalty: 存在惩罚（-2.0 到 2.0）
            stop: 停止序列列表
            **kwargs: 其他推理参数
        
        Returns:
            反序列化后的 JSON 结果（字典格式），包含两个评估维度的分数：
            - "Therapeutic Alliance Assessment": 治疗联盟评估分数 (0-3)
            - "Interaction Assessment": 互动评估分数 (0-3)
        """
        # 格式化 prompt
        formatted_prompt = self._format_prompt(session_dialogs, session_name)
        
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
    # 读取 prompt 文件
    with open("prompts/post_session_evaluation/post_session_evaluation_en.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    
    # 初始化评估器（client 会在内部自动创建，api_key 从环境变量读取）
    evaluator = PostSessionEvaluation(
        model="openai/gpt-4o",
        prompt=prompt
    )
    
    # 示例会话对话历史
    sample_session_dialogs = """
    Session 1:
    Patient: I've been feeling very anxious about my job interview next week.
    Counselor: I understand that job interviews can be stressful. Can you tell me more about what specifically makes you anxious?
    
    Session 2:
    Patient: I'm still worried about the interview. I keep thinking about all the things that could go wrong.
    Counselor: It sounds like you're experiencing a lot of negative thoughts. Let's work on challenging those thoughts together.
    """
    
    # 进行评估
    try:
        result = evaluator.evaluate(
            session_dialogs=sample_session_dialogs,
            temperature=0.7,
            max_tokens=500
        )
        print("评估结果:", result)
        print("治疗联盟评估:", result.get("Therapeutic Alliance Assessment"))
        print("互动评估:", result.get("Interaction Assessment"))
    except Exception as e:
        print(f"错误: {e}")
    
    # 示例 2: 使用不同的推理参数
    try:
        result = evaluator.evaluate(
            session_dialogs=sample_session_dialogs,
            temperature=0.3,  # 更低的温度，更确定性的输出
            max_tokens=400
        )
        print("\n评估结果:", result)
    except Exception as e:
        print(f"错误: {e}")

