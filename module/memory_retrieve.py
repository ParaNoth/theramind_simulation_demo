"""
Memory Retrieve 模块
用于从历史对话中检索相关信息，使用 LLM 判断是否需要参考历史记录
"""

from typing import Optional
from .base_llm_client import BaseLLMClient


class MemoryRetrieve(BaseLLMClient):
    """记忆检索器，使用 LLM 从历史对话中检索相关信息"""
    
    def retrieve(
        self,
        utter: str,
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
        从历史对话中检索相关信息
        
        Args:
            utter: 用户的当前输入（utterance）
            all_dialogs: 所有的历史对话记录
            temperature: 温度参数（0-2），控制随机性
            max_tokens: 最大生成 token 数
            top_p: 核采样参数
            frequency_penalty: 频率惩罚（-2.0 到 2.0）
            presence_penalty: 存在惩罚（-2.0 到 2.0）
            stop: 停止序列列表
            **kwargs: 其他推理参数
        
        Returns:
            检索结果字符串（相关历史内容的摘要，或 "No need to consider historical conversation memory"）
        """
        # 格式化 prompt
        formatted_prompt = self._format_prompt(utter, all_dialogs)
        
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
        
        # 清理并返回结果
        result = content.strip()
        
        return result
    
    def _format_prompt(self, utter: str, all_dialogs: str) -> str:
        """
        将用户输入和历史对话替换到 prompt 模板中
        
        Args:
            utter: 用户的当前输入（utterance）
            all_dialogs: 所有的历史对话记录
        
        Returns:
            格式化后的 prompt
        """
        formatted_prompt = self.prompt
        
        # 替换 {patient_input} 或 {utter} 或 {input}
        if "{patient_input}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{patient_input}", utter)
        elif "{utter}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{utter}", utter)
        elif "{input}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{input}", utter)
        
        # 替换 {all_dialogs}
        if "{all_dialogs}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{all_dialogs}", all_dialogs)
        
        return formatted_prompt


# 使用示例
if __name__ == "__main__":
    # 示例 1: 基本使用
    # 读取 prompt 文件
    with open("prompts/memory_retrieve/memory_retrieve_en.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    
    # 初始化检索器（client 会在内部自动创建，api_key 从环境变量读取）
    retriever = MemoryRetrieve(
        model="openai/gpt-4o",
        prompt=prompt
    )
    
    # 准备历史对话
    all_dialogs = """
    Session 1:
    Patient: I've been feeling very anxious about my job interview next week.
    Therapist: I understand. Can you tell me more about what specifically makes you anxious?
    Patient: I'm worried I won't be able to answer their questions properly.
    
    Session 2:
    Patient: The interview went well, but I'm still nervous about the result.
    Therapist: That's a natural feeling. What are you most concerned about?
    """
    
    # 进行检索
    try:
        result = retriever.retrieve(
            utter="I have another interview coming up, and I'm feeling the same anxiety again.",
            all_dialogs=all_dialogs,
            temperature=0.7,
            max_tokens=100
        )
        print("检索结果:", result)
    except Exception as e:
        print(f"错误: {e}")
    
    # 示例 2: 不需要参考历史的情况
    try:
        result = retriever.retrieve(
            utter="I'm feeling great today! The weather is beautiful.",
            all_dialogs=all_dialogs,
            temperature=0.7,
            max_tokens=100
        )
        print("\n检索结果:", result)
    except Exception as e:
        print(f"错误: {e}")
    
    # 示例 3: 使用不同的推理参数
    try:
        result = retriever.retrieve(
            utter="I'm still worried about job interviews, just like before.",
            all_dialogs=all_dialogs,
            temperature=0.3,  # 更低的温度，更确定性的输出
            max_tokens=150
        )
        print("\n检索结果:", result)
    except Exception as e:
        print(f"错误: {e}")

