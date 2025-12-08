"""
咨询管理模块
维护整个咨询流程，管理 all_dialogs 的存储和读取，协调 in_session 和 cross_session
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from in_session import InSession
from cross_session import CrossSession


class CounselingManager:
    """咨询管理类，维护整个咨询流程和 all_dialogs 的管理"""
    
    def __init__(
        self,
        config_path: str = "model_config/default_config.json",
        all_dialogs_file: Optional[str] = None,
        storage_dir: str = "counseling_records",
        initial_therapy: Optional[str] = None
    ):
        """
        初始化咨询管理器
        
        Args:
            config_path: 配置文件路径（JSON 格式），默认：model_config/default_config.json
            all_dialogs_file: all_dialogs 存档文件路径（可选）
                            - 如果提供，则从该文件加载历史记录继续咨询
                            - 如果不提供，则创建新的咨询记录文件
            storage_dir: 存储目录，用于存放咨询记录文件（默认：counseling_records）
            initial_therapy: 首次咨询的治疗方案（可选）
                           - 如果创建新咨询且未指定，则使用默认值"认知行为疗法（CBT）"
                           - 如果从文件加载，此参数将被忽略
        """
        self.config_path = config_path
        self.storage_dir = storage_dir
        self.all_dialogs_file = all_dialogs_file
        
        # 确保存储目录存在
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        
        # 加载或创建 all_dialogs
        if all_dialogs_file:
            # 从文件加载历史记录
            self.all_dialogs, self.current_therapy = self._load_all_dialogs(all_dialogs_file)
            self.all_dialogs_file = all_dialogs_file
        else:
            # 创建新的咨询记录
            self.all_dialogs, self.current_therapy = self._create_new_counseling(initial_therapy)
        
        # 初始化 in_session 和 cross_session
        self.in_session = InSession(
            config_path=config_path,
            current_therapy=self.current_therapy,
            all_dialogs=self.all_dialogs
        )
        
        self.cross_session = CrossSession(
            config_path=config_path
        )
    
    def _create_new_counseling(self, initial_therapy: Optional[str] = None) -> tuple[List[Dict], str]:
        """
        创建新的咨询记录
        
        Args:
            initial_therapy: 首次咨询的治疗方案（可选）
                           - 如果未指定，则使用默认值"认知行为疗法（CBT）"
        
        Returns:
            (all_dialogs, current_therapy) 元组
        """
        # 创建独特名称的文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"counseling_{timestamp}.json"
        self.all_dialogs_file = os.path.join(self.storage_dir, file_name)
        
        # 初始化 therapy，如果未指定则使用默认值
        if initial_therapy is None:
            current_therapy = "认知行为疗法（CBT）"
        else:
            current_therapy = initial_therapy
        
        # 第一次的理由为空
        all_dialogs = [self._create_empty_session_log(therapy=current_therapy, therapy_reason="")]
        
        # 保存到文件
        self._save_all_dialogs(self.all_dialogs_file, all_dialogs, current_therapy)
        
        return all_dialogs, current_therapy
    
    def _create_empty_session_log(self, therapy: str = "", therapy_reason: str = "") -> Dict:
        """
        创建一个空的 session log_dict
        
        Args:
            therapy: 该 session 使用的治疗方案
            therapy_reason: 选择该治疗方案的理由
        
        Returns:
            空的 session log_dict
        """
        return {
            "dialogue": [],
            "reaction_results": [],
            "resistance_results": [],
            "strategy_results": [],
            "memory_results": [],
            "current_stage_results": [],
            "therapy": therapy,  # 该 session 使用的治疗方案
            "therapy_reason": therapy_reason,  # 选择该治疗方案的理由
            "is_ended": False  # 标记当前 dialog 是否结束
        }
    
    def _load_all_dialogs(self, file_path: str) -> tuple[List[Dict], str]:
        """
        从文件加载 all_dialogs 和 current_therapy
        
        Args:
            file_path: 文件路径
        
        Returns:
            (all_dialogs, current_therapy) 元组
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"咨询记录文件不存在: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 兼容不同的文件格式
        if isinstance(data, list):
            # 旧格式：直接是 all_dialogs 列表
            all_dialogs = data
            current_therapy = ""
        elif isinstance(data, dict):
            # 新格式：包含 all_dialogs 和 current_therapy
            all_dialogs = data.get("all_dialogs", [])
            current_therapy = data.get("current_therapy", "")
        else:
            raise ValueError(f"不支持的咨询记录文件格式: {type(data)}")
        
        # 确保 all_dialogs 不为空
        if not all_dialogs:
            all_dialogs = [self._create_empty_session_log(therapy=current_therapy, therapy_reason="")]
        
        # 确保每个 session 都有必需的字段（向后兼容）
        for session in all_dialogs:
            if "therapy" not in session:
                session["therapy"] = current_therapy
            if "therapy_reason" not in session:
                session["therapy_reason"] = ""  # 第一次的理由为空
            if "current_stage_results" not in session:
                session["current_stage_results"] = []  # 添加 current_stage_results 字段
            if "is_ended" not in session:
                # 向后兼容：如果旧数据没有 is_ended 字段，默认设为未结束
                # 这样用户可以继续在当前 dialog 下对话，而不是创建新的 dialog
                session["is_ended"] = False
        
        # 检查最后一个 dialog 是否结束
        last_dialog = all_dialogs[-1]
        is_last_dialog_ended = last_dialog.get("is_ended", False)
        
        if is_last_dialog_ended:
            # 如果最后的 dialog 已结束，创建新的 dialog 并开始对话
            new_dialog = self._create_empty_session_log(
                therapy=current_therapy,
                therapy_reason=""
            )
            all_dialogs.append(new_dialog)
        # 如果 dialog 未结束，则继续在当前 dialog 下对话（不需要创建新的）
        
        return all_dialogs, current_therapy
    
    def _save_all_dialogs(self, file_path: str, all_dialogs: List[Dict], current_therapy: str):
        """
        保存 all_dialogs 和 current_therapy 到文件
        
        Args:
            file_path: 文件路径
            all_dialogs: 所有对话记录
            current_therapy: 当前治疗方案
        """
        data = {
            "all_dialogs": all_dialogs,
            "current_therapy": current_therapy,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def process(
        self,
        patient_input: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        处理用户输入，返回咨询师的回复
        
        Args:
            patient_input: 用户的当前输入
            temperature: 温度参数（0-2），控制随机性
            max_tokens: 最大生成 token 数
            top_p: 核采样参数
            frequency_penalty: 频率惩罚（-2.0 到 2.0）
            presence_penalty: 存在惩罚（-2.0 到 2.0）
            stop: 停止序列列表
            **kwargs: 其他推理参数
        
        Returns:
            包含所有中间结果和最终回复的字典，以及是否开始新 session 的信息
        """
        # 调用 in_session 处理用户输入
        result = self.in_session.process(
            patient_input=patient_input,
            current_therapy=self.current_therapy,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            **kwargs
        )
        
        # 更新本地的 all_dialogs（in_session 已经更新了）
        self.all_dialogs = self.in_session.get_dialogs()
        
        # 检查是否结束会话
        end_session = result.get("end_session", False)
        
        if end_session:
            # 会话结束，启动 cross_session 评估并选择新的 therapy
            cross_session_result = self._process_session_end(
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
                **kwargs
            )
            
            # 将 cross_session 的结果添加到返回结果中
            result["cross_session"] = cross_session_result
            result["new_session_started"] = True
        else:
            result["new_session_started"] = False
        
        # 保存到文件
        self._save_all_dialogs(
            self.all_dialogs_file,
            self.all_dialogs,
            self.current_therapy
        )
        
        return result
    
    def _process_session_end(
        self,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        处理会话结束，调用 cross_session 评估并选择新的 therapy
        
        Args:
            temperature: 温度参数
            max_tokens: 最大生成 token 数
            top_p: 核采样参数
            frequency_penalty: 频率惩罚
            presence_penalty: 存在惩罚
            stop: 停止序列列表
            **kwargs: 其他推理参数
        
        Returns:
            cross_session 的处理结果
        """
        # 获取当前 session 的 dialogue（最后一个 session）
        if not self.all_dialogs:
            raise ValueError("all_dialogs 为空，无法处理会话结束")
        
        current_session = self.all_dialogs[-1]
        current_dialogue = current_session.get("dialogue", [])
        
        # 调用 cross_session 选择新的 therapy
        cross_result = self.cross_session.process(
            last_dialogs=current_dialogue,
            last_therapy=self.current_therapy,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            **kwargs
        )
        
        # 更新 current_therapy
        new_therapy = cross_result.get("new_therapy", "")
        new_reason = cross_result.get("reason", "")
        if new_therapy:
            self.current_therapy = new_therapy
        
        # 将新的 therapy 和 reason 存储到当前 session 的 log_dict 中
        current_session["therapy"] = self.current_therapy
        current_session["therapy_reason"] = new_reason
        
        # 标记当前 session 已结束
        current_session["is_ended"] = True
        
        # 更新 in_session 的 therapy
        self.in_session.update_therapy(new_therapy)
        
        # 重置 in_session 的 session（开始新的 session）
        self.in_session.reset_session()
        
        # 更新本地的 all_dialogs（reset_session 后会有新的空 session）
        self.all_dialogs = self.in_session.get_dialogs()
        
        # 确保新的 session 也有 therapy 和 therapy_reason 字段
        if self.all_dialogs and self.all_dialogs[-1]:
            if "therapy" not in self.all_dialogs[-1]:
                self.all_dialogs[-1]["therapy"] = new_therapy
            if "therapy_reason" not in self.all_dialogs[-1]:
                self.all_dialogs[-1]["therapy_reason"] = ""
        
        return cross_result
    
    def get_all_dialogs(self) -> List[Dict]:
        """
        获取所有历史对话记录
        
        Returns:
            所有历史对话记录，格式为 List[Dict]
        """
        return self.all_dialogs
    
    def get_current_therapy(self) -> str:
        """
        获取当前治疗方案
        
        Returns:
            当前治疗方案字符串
        """
        return self.current_therapy
    
    def get_all_dialogs_file(self) -> str:
        """
        获取当前使用的 all_dialogs 文件路径
        
        Returns:
            文件路径
        """
        return self.all_dialogs_file
    
    def save(self):
        """
        手动保存当前状态到文件
        """
        self._save_all_dialogs(
            self.all_dialogs_file,
            self.all_dialogs,
            self.current_therapy
        )


# 使用示例
if __name__ == "__main__":
    # 示例 1: 创建新的咨询（使用默认 therapy）
    print("=== 示例 1: 创建新的咨询（使用默认 therapy） ===")
    manager = CounselingManager(
        config_path="model_config/default_config.json",
        all_dialogs_file=None  # 不指定文件，创建新咨询
    )
    
    print(f"创建的咨询记录文件: {manager.get_all_dialogs_file()}")
    print(f"当前治疗方案: {manager.get_current_therapy()}")
    
    # 示例 1.5: 创建新的咨询（指定初始 therapy）
    print("\n=== 示例 1.5: 创建新的咨询（指定初始 therapy） ===")
    manager_custom = CounselingManager(
        config_path="model_config/default_config.json",
        all_dialogs_file=None,
        initial_therapy="正念认知疗法（MBCT）"  # 指定初始 therapy
    )
    
    print(f"创建的咨询记录文件: {manager_custom.get_all_dialogs_file()}")
    print(f"当前治疗方案: {manager_custom.get_current_therapy()}")
    
    # 处理第一个用户输入
    try:
        result1 = manager.process(
            patient_input="I've been feeling very anxious about my job interview next week.",
            temperature=0.7,
            max_tokens=200
        )
        print("\n=== 第一次对话 ===")
        print(f"用户输入: {result1['patient_input']}")
        print(f"咨询师回复: {result1['counselor_response']}")
        print(f"是否结束会话: {result1['end_session']}")
        print(f"是否开始新 session: {result1.get('new_session_started', False)}")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 示例 2: 从文件加载继续咨询
    print("\n\n=== 示例 2: 从文件加载继续咨询 ===")
    if manager.get_all_dialogs_file():
        saved_file = manager.get_all_dialogs_file()
        print(f"从文件加载: {saved_file}")
        
        manager2 = CounselingManager(
            config_path="model_config/default_config.json",
            all_dialogs_file=saved_file
        )
        
        print(f"当前治疗方案: {manager2.get_current_therapy()}")
        print(f"历史 session 数量: {len(manager2.get_all_dialogs())}")
        
        # 继续处理用户输入
        try:
            result2 = manager2.process(
                patient_input="I'm worried I won't be able to answer their questions properly.",
                temperature=0.7,
                max_tokens=200
            )
            print("\n=== 继续对话 ===")
            print(f"用户输入: {result2['patient_input']}")
            print(f"咨询师回复: {result2['counselor_response']}")
            print(f"是否结束会话: {result2['end_session']}")
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()

