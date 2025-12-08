"""
Resistance Detection 模块
用于检测用户输入是否表现出抵抗或偏离咨询主题
"""

import re
from typing import Optional
from .base_llm_client import BaseLLMClient


class ResistanceDetection(BaseLLMClient):
    """抵抗检测器，使用 LLM 检测用户是否表现出抵抗或偏离主题"""
    
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
        检测用户输入是否表现出抵抗或偏离主题
        
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
            True 或 False（布尔值）
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
        
        # 解析响应，提取 True 或 False
        result = self._parse_boolean_response(content)
        
        return result
    
    def _parse_boolean_response(self, content: str) -> bool:
        """
        从 LLM 响应中解析布尔值
        
        Args:
            content: LLM 返回的文本内容
        
        Returns:
            True 或 False（布尔值）
        """
        # 去除首尾空白
        content = content.strip()
        
        # 尝试直接匹配 True 或 False（不区分大小写）
        true_patterns = [
            r'^True$',
            r'^true$',
            r'^TRUE$',
        ]
        false_patterns = [
            r'^False$',
            r'^false$',
            r'^FALSE$',
        ]
        
        # 检查是否为 True
        for pattern in true_patterns:
            if re.match(pattern, content):
                return True
        
        # 检查是否为 False
        for pattern in false_patterns:
            if re.match(pattern, content):
                return False
        
        # 如果直接匹配失败，尝试在文本中查找
        content_lower = content.lower()
        
        # 查找 True（优先）
        if re.search(r'\btrue\b', content_lower):
            return True
        
        # 查找 False
        if re.search(r'\bfalse\b', content_lower):
            return False
        
        # 如果所有方法都失败，抛出异常
        raise ValueError(
            f"无法从 LLM 响应中解析布尔值。响应内容: {content}"
        )


# 使用示例
if __name__ == "__main__":
    # 示例 1: 基本使用
    # 读取 prompt 文件
    with open("prompts/resistance_detection/resistance_detection_en.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    
    # 初始化检测器（client 会在内部自动创建，api_key 从环境变量读取）
    detector = ResistanceDetection(
        model="openai/gpt-4o",
        prompt=prompt
    )
    
    # 进行检测
    try:
        result = detector.detect(
            utter="I don't want to talk about this anymore. Can we change the topic?",
            temperature=0.7,
            max_tokens=50
        )
        print("检测结果:", result)
        print("是否抵抗:", result)
    except Exception as e:
        print(f"错误: {e}")
    
    # 示例 2: 正常对话（应该返回 False）
    try:
        result = detector.detect(
            utter="I've been feeling anxious about my work lately.",
            temperature=0.7,
            max_tokens=50
        )
        print("\n检测结果:", result)
        print("是否抵抗:", result)
    except Exception as e:
        print(f"错误: {e}")
    
    # 示例 3: 使用不同的推理参数
    try:
        result = detector.detect(
            utter="This is not helpful at all. I think we should stop here.",
            temperature=0.3,  # 更低的温度，更确定性的输出
            max_tokens=50
        )
        print("\n检测结果:", result)
    except Exception as e:
        print(f"错误: {e}")

