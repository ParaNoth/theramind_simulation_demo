"""
End Detection 模块
用于检测用户输入是否表示会话结束，使用 LLM 进行判断
"""

from typing import Optional
from .base_llm_client import BaseLLMClient


class EndDetection(BaseLLMClient):
    """结束检测器，使用 LLM 判断用户是否想要结束会话"""
    
    def detect(
        self,
        utter: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[list] = None,
        **kwargs
    ) -> bool:
        """
        检测用户输入是否表示会话结束
        
        Args:
            utter: 用户的当前输入（utterance）
            temperature: 温度参数（0-2），控制随机性
            max_tokens: 最大生成 token 数
            top_p: 核采样参数
            frequency_penalty: 频率惩罚（-2.0 到 2.0）
            presence_penalty: 存在惩罚（-2.0 到 2.0）
            stop: 停止序列列表
            **kwargs: 其他推理参数
        
        Returns:
            bool: True 表示用户想要结束会话，False 表示继续会话
        """
        # 格式化 prompt
        formatted_prompt = self._format_prompt(utter)
        
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
        
        # 解析布尔值结果
        result = self._parse_boolean_response(content)
        
        return result
    
    def _parse_boolean_response(self, content: str) -> bool:
        """
        从 LLM 响应中解析布尔值
        
        Args:
            content: LLM 返回的文本内容
        
        Returns:
            解析后的布尔值
        """
        # 去除首尾空白字符
        content = content.strip()
        
        # 尝试直接匹配 True/False（不区分大小写）
        if content.lower() == "true":
            return True
        elif content.lower() == "false":
            return False
        
        # 如果直接匹配失败，尝试在文本中查找 True/False
        content_lower = content.lower()
        if "true" in content_lower:
            # 检查是否包含 "false"，如果同时包含，以最后出现的为准
            true_pos = content_lower.rfind("true")
            false_pos = content_lower.rfind("false")
            if false_pos > true_pos:
                return False
            return True
        elif "false" in content_lower:
            return False
        
        # 如果无法解析，默认返回 False（继续会话）
        return False


# 使用示例
if __name__ == "__main__":
    # 示例 1: 基本使用
    # 读取 prompt 文件
    with open("prompts/end_detection/end_detection_en.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    
    # 初始化检测器（client 会在内部自动创建，api_key 从环境变量读取）
    detector = EndDetection(
        model="openai/gpt-4o",
        prompt=prompt
    )
    
    # 进行检测
    try:
        result = detector.detect(
            utter="That's all for today. Thank you for your help.",
            temperature=0.7,
            max_tokens=10
        )
        print("检测结果:", result)
        print("是否结束会话:", "是" if result else "否")
    except Exception as e:
        print(f"错误: {e}")
    
    # 示例 2: 继续会话的情况
    try:
        result = detector.detect(
            utter="I feel really anxious about the upcoming exam.",
            temperature=0.3,
            max_tokens=10
        )
        print("\n检测结果:", result)
        print("是否结束会话:", "是" if result else "否")
    except Exception as e:
        print(f"错误: {e}")

