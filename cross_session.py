"""
Cross-Session 模块
用于在会话之间选择新的治疗方案
"""

import json
import os
from typing import Dict, Any, Optional, Union, List
from module.therapy_selection import TherapySelection


class CrossSession:
    """跨会话管理类，用于根据上一轮会话历史选择新的治疗方案"""
    
    def __init__(
        self,
        config_path: str = "model_config/default_config.json"
    ):
        """
        初始化跨会话管理器
        
        Args:
            config_path: 配置文件路径（JSON 格式），默认：model_config/default_config.json
                        配置文件应包含 therapy_selection 模块的 model 和 prompt_path 配置
                        示例格式：
                        {
                          "therapy_selection": {
                            "model": "openai/gpt-4o",
                            "prompt_path": "prompts/therapy_selection/therapy_selection_en.txt"
                          },
                          "dialog_labels": {
                            "user_label": "Patient",
                            "assistant_label": "Therapist"
                          }
                        }
        """
        self.config_path = config_path
        
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 读取对话标签配置，设置默认值
        dialog_labels = self.config.get("dialog_labels", {})
        self.user_label = dialog_labels.get("user_label", "Patient")
        self.assistant_label = dialog_labels.get("assistant_label", "Therapist")
        
        # 初始化 therapy_selection 模块
        self._init_modules()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
        
        Returns:
            配置字典
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # 验证必需的模块配置
        required_modules = ["therapy_selection"]
        
        for module in required_modules:
            if module not in config:
                raise ValueError(f"配置文件中缺少必需的模块: {module}")
            if "model" not in config[module]:
                raise ValueError(f"模块 {module} 缺少 'model' 配置")
            if "prompt_path" not in config[module]:
                raise ValueError(f"模块 {module} 缺少 'prompt_path' 配置")
        
        return config
    
    def _dialogs_to_string(self, dialogs: Union[str, List[Dict[str, str]]]) -> str:
        """
        将对话记录转换为字符串格式
        
        Args:
            dialogs: 对话记录，可以是：
                    - 字符串格式：直接返回
                    - list[dict] 格式：每个 dict 为 {'role': 'user/assistant', 'content': 'content'}
        
        Returns:
            字符串格式的对话记录
        """
        if isinstance(dialogs, str):
            return dialogs
        
        if not isinstance(dialogs, list):
            raise ValueError(f"不支持的 dialogs 格式: {type(dialogs)}")
        
        if not dialogs:
            return ""
        
        dialog_lines = []
        for dialog in dialogs:
            role = dialog.get("role", "")
            content = dialog.get("content", "")
            if role == "user":
                dialog_lines.append(f"{self.user_label}: {content}")
            elif role == "assistant":
                dialog_lines.append(f"{self.assistant_label}: {content}")
        
        return "\n".join(dialog_lines)
    
    def _init_modules(self):
        """初始化所有子模块"""
        therapy_config = self.config["therapy_selection"]
        with open(therapy_config["prompt_path"], "r", encoding="utf-8") as f:
            therapy_prompt = f.read()
        self.therapy_selector = TherapySelection(
            model=therapy_config["model"],
            prompt=therapy_prompt
        )
    
    def process(
        self,
        last_dialogs: Union[str, List[Dict[str, str]]],
        last_therapy: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        根据上一轮会话历史和治疗方式选择新的治疗方式
        
        Args:
            last_dialogs: 上一轮会话的历史记录
                        可以是字符串格式或 list[dict] 格式
                        如果是 list[dict]，每个 dict 为 {'role': 'user/assistant', 'content': 'content'}
            last_therapy: 上一轮使用的治疗方式
            temperature: 温度参数（0-2），控制随机性
            max_tokens: 最大生成 token 数
            top_p: 核采样参数
            frequency_penalty: 频率惩罚（-2.0 到 2.0）
            presence_penalty: 存在惩罚（-2.0 到 2.0）
            stop: 停止序列列表
            **kwargs: 其他推理参数
        
        Returns:
            包含新疗法和说明的字典，格式为：
            {
                "new_therapy": "新的治疗方式",
                "reason": "选择原因",
                "last_therapy": "上一轮使用的治疗方式",
                "last_dialogs": "上一轮会话历史（字符串格式）"
            }
        """
        # 将 last_dialogs 转换为字符串格式
        last_dialogs_string = self._dialogs_to_string(last_dialogs)
        
        # 调用 therapy_selection 模块
        result = self.therapy_selector.select(
            last_dialogs=last_dialogs_string,
            last_therapy=last_therapy,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            **kwargs
        )
        
        # 提取结果
        new_therapy = result.get("new_therapy", "")
        reason = result.get("reason", "")
        
        # 返回结果
        return {
            "new_therapy": new_therapy,
            "reason": reason,
            "last_therapy": last_therapy,
            "last_dialogs": last_dialogs_string
        }


# 使用示例
if __name__ == "__main__":
    # 使用默认配置文件（model_config/default_config.json）
    print("=== 使用默认配置文件 ===")
    
    # 注意：需要确保配置文件中包含 therapy_selection 模块的配置
    # 如果配置文件中没有，需要先添加
    try:
        cross_session = CrossSession(
            config_path="model_config/default_config.json"
        )
        
        # 示例 1: 使用字符串格式的对话记录
        print("\n=== 示例 1: 字符串格式的对话记录 ===")
        result1 = cross_session.process(
            last_dialogs="Patient: I've been feeling very anxious about my job interview.\nTherapist: I understand. Let's work on some breathing exercises to help you manage this anxiety.",
            last_therapy="Cognitive Behavioral Therapy focusing on anxiety management",
            temperature=0.7,
            max_tokens=200
        )
        print(f"上一轮治疗方式: {result1['last_therapy']}")
        print(f"新治疗方式: {result1['new_therapy']}")
        print(f"选择原因: {result1['reason']}")
        
        # 示例 2: 使用 list[dict] 格式的对话记录
        print("\n=== 示例 2: list[dict] 格式的对话记录 ===")
        last_dialogs_list = [
            {"role": "user", "content": "I've been feeling very anxious about my job interview."},
            {"role": "assistant", "content": "I understand. Let's work on some breathing exercises to help you manage this anxiety."},
            {"role": "user", "content": "That helped a bit, but I'm still worried."},
            {"role": "assistant", "content": "That's normal. Let's try some cognitive restructuring techniques."}
        ]
        result2 = cross_session.process(
            last_dialogs=last_dialogs_list,
            last_therapy="Breathing Exercise",
            temperature=0.7,
            max_tokens=200
        )
        print(f"上一轮治疗方式: {result2['last_therapy']}")
        print(f"新治疗方式: {result2['new_therapy']}")
        print(f"选择原因: {result2['reason']}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

