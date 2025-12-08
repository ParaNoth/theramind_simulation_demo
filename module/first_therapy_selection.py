"""
First Therapy Selection 模块
用于根据医疗记录选择首次治疗方式，使用 LLM 进行推荐
"""

from typing import Dict, Any, Optional
from .base_llm_client import BaseLLMClient


class FirstTherapySelection(BaseLLMClient):
    """首次治疗方式选择器，使用 LLM 根据医疗记录推荐合适的治疗方式"""
    
    def _format_prompt(self, medical_record: str) -> str:
        """
        将医疗记录替换到 prompt 模板中
        
        Args:
            medical_record: 患者的医疗记录
        
        Returns:
            格式化后的 prompt
        """
        formatted_prompt = self.prompt
        if "{medical_record}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{medical_record}", medical_record)
        
        return formatted_prompt
    
    def select(
        self,
        medical_record: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[list] = None,
        **kwargs
    ) -> str:
        """
        根据医疗记录选择首次治疗方式
        
        Args:
            medical_record: 患者的医疗记录
            temperature: 温度参数（0-2），控制随机性
            max_tokens: 最大生成 token 数
            top_p: 核采样参数
            frequency_penalty: 频率惩罚（-2.0 到 2.0）
            presence_penalty: 存在惩罚（-2.0 到 2.0）
            stop: 停止序列列表
            **kwargs: 其他推理参数
        
        Returns:
            LLM 返回的治疗方式名称（字符串格式，可能是单个疗法或多个疗法用 '+' 分隔）
        """
        # 格式化 prompt
        formatted_prompt = self._format_prompt(medical_record)
        
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
        
        # 清理返回内容（去除可能的空白字符）
        result = content.strip()
        
        return result


# 使用示例
if __name__ == "__main__":
    # 示例 1: 基本使用
    # 读取 prompt 文件
    with open("prompts/first_therapy_selection/first_therapy_selection_en.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    
    # 初始化首次治疗方式选择器（client 会在内部自动创建，api_key 从环境变量读取）
    selector = FirstTherapySelection(
        model="openai/gpt-4o",
        prompt=prompt
    )
    
    # 选择首次治疗方式
    try:
        medical_record = "Patient presents with symptoms of anxiety and depression. History of panic attacks. No previous therapy experience."
        result = selector.select(
            medical_record=medical_record,
            temperature=0.7,
            max_tokens=200
        )
        print("推荐的治疗方式:", result)
    except Exception as e:
        print(f"错误: {e}")
    
    # 示例 2: 使用不同的推理参数
    try:
        medical_record = "Patient with social anxiety disorder. Moderate symptoms. Prefers structured approach."
        result = selector.select(
            medical_record=medical_record,
            temperature=0.3,  # 更低的温度，更确定性的输出
            max_tokens=150
        )
        print("\n推荐的治疗方式:", result)
    except Exception as e:
        print(f"错误: {e}")

