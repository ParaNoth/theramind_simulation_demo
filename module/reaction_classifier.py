"""
Reaction Classifier 模块
用于对用户输入进行分类，使用 LLM 进行情感识别和强度评估
"""

from typing import Dict, Any, Optional
from .base_llm_client import BaseLLMClient


class ReactionClassifier(BaseLLMClient):
    """反应分类器，使用 LLM 对用户输入进行分类"""
    
    def classify(
        self,
        utter: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        对用户输入进行分类
        
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
            反序列化后的 JSON 结果（字典格式）
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
        
        # 解析 JSON 字符串
        result = self._parse_json_response(content)
        
        return result


# 使用示例
if __name__ == "__main__":
    # 示例 1: 基本使用
    # 读取 prompt 文件
    with open("prompts/reaction_classifier/reaction_classifier_en.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    
    # 初始化分类器（client 会在内部自动创建，api_key 从环境变量读取）
    classifier = ReactionClassifier(
        model="openai/gpt-4o",
        prompt=prompt
    )
    
    # 进行分类
    try:
        result = classifier.classify(
            utter="I feel really anxious about the upcoming exam.",
            temperature=0.7,
            max_tokens=200
        )
        print("分类结果:", result)
        print("主要情感:", result.get("primary_emotion"))
        print("情感强度:", result.get("emotional_intensity"))
    except Exception as e:
        print(f"错误: {e}")
    
    # 示例 2: 使用不同的推理参数
    try:
        result = classifier.classify(
            utter="I'm so happy that I got the job!",
            temperature=0.3,  # 更低的温度，更确定性的输出
            max_tokens=150
        )
        print("\n分类结果:", result)
    except Exception as e:
        print(f"错误: {e}")

