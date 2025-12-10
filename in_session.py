"""
In-Session 模块
整合所有子模块，实现完整的咨询会话流程
"""

import json
import os
from typing import Dict, Any, Optional, Union, List
from module.reaction_classifier import ReactionClassifier
from module.resistance_detection import ResistanceDetection
from module.strategy_selection import StrategySelection
from module.phase_selection import PhaseSelection
from module.memory_retrieve import MemoryRetrieve
from module.counselor_agent import CounselorAgent
from module.end_detection import EndDetection


class InSession:
    """会话管理类，整合所有子模块实现完整的咨询流程"""
    
    def __init__(
        self,
        config_path: str = "model_config/default_config.json",
        current_therapy: str = "",
        all_dialogs: Union[str, List[Dict]] = None
    ):
        """
        初始化会话管理器
        
        Args:
            config_path: 配置文件路径（JSON 格式），默认：model_config/default_config.json
                        配置文件应包含每个模块的 model 和 prompt_path 配置
                        示例格式：
                        {
                          "reaction_classifier": {
                            "model": "openai/gpt-4o",
                            "prompt_path": "prompts/reaction_classifier/reaction_classifier_en.txt"
                          },
                          ...
                          "dialog_labels": {
                            "user_label": "Patient",
                            "assistant_label": "Therapist"
                          }
                        }
            current_therapy: 当前治疗方案（可选，默认为空字符串）
            all_dialogs: 所有历史对话记录（可选，默认为空列表）
                        格式：List[Dict]，每个 Dict 代表一个 session 的 log_dict，包含：
                        - dialogue: List[Dict[str, str]] - 此 session 的聊天记录，格式为 [{'role': 'user/assistant', 'content': 'content'}, ...]
                        - reaction_results: List[Dict] - 每一轮的 reaction_result 结果列表（包含 model 字段）
                        - resistance_results: List[Dict] - 每一轮的 resistance 结果列表（格式：{"resistance": bool, "model": str}）
                        - strategy_results: List[Dict] - 每一轮 strategy_result 的结果列表（包含 model 字段）
                        - memory_results: List[Dict] - 每一轮 memory_result 的列表（格式：{"content": str, "model": str}）
                        - current_stage_results: List[Dict] - 每一轮 current_stage 的结果列表（格式：{"content": str, "model": str}）
                        每个 Dict 代表一个 session 的历史记录，按时间从早到晚排列
                        当前 session 的记录为 all_dialogs[-1]
        """
        self.config_path = config_path
        self.current_therapy = current_therapy
        
        # 初始化 all_dialogs
        if all_dialogs is None:
            self.all_dialogs: List[Dict] = [self._create_empty_session_log()]
        elif isinstance(all_dialogs, str):
            # 向后兼容：如果传入字符串，转换为新格式
            if all_dialogs.strip() == "":
                self.all_dialogs: List[Dict] = [self._create_empty_session_log()]
            else:
                # 如果传入非空字符串，暂时初始化为包含一个空 session 的列表
                self.all_dialogs: List[Dict] = [self._create_empty_session_log()]
        else:
            # 已经是 List[Dict] 格式
            self.all_dialogs: List[Dict] = all_dialogs
        
        # 检查 self.all_dialogs 最后一个元素的状态
        # 只有当最后一个 session 已结束（is_ended=True）时，才创建新的 session
        if not self.all_dialogs:
            self.all_dialogs = [self._create_empty_session_log()]
        else:
            last_session = self.all_dialogs[-1]
            is_ended = last_session.get("is_ended", False)
            # 只有当最后一个 session 已结束时，才创建新的 session
            if is_ended:
                self.all_dialogs.append(self._create_empty_session_log())
        
        self.session_strategy_memory = []  # 本次会话中已使用的策略记录列表
        
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 读取对话标签配置，设置默认值
        dialog_labels = self.config.get("dialog_labels", {})
        self.user_label = dialog_labels.get("user_label", "Patient")
        self.assistant_label = dialog_labels.get("assistant_label", "Therapist")
        
        # 初始化所有子模块
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
        required_modules = [
            "reaction_classifier",
            "resistance_detection",
            "strategy_selection",
            "phase_selection",
            "memory_retrieve",
            "counselor",
            "end_detection"
        ]
        
        for module in required_modules:
            if module not in config:
                raise ValueError(f"配置文件中缺少必需的模块: {module}")
            if "model" not in config[module]:
                raise ValueError(f"模块 {module} 缺少 'model' 配置")
            if "prompt_path" not in config[module]:
                raise ValueError(f"模块 {module} 缺少 'prompt_path' 配置")
        
        return config
    
    def _create_empty_session_log(self) -> Dict:
        """
        创建一个空的 session log_dict
        
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
            "is_ended": False  # 标记当前 dialog 是否结束
        }
    
    def _is_empty_session(self, session_log: Dict) -> bool:
        """
        检查 session log 是否为空（没有任何对话记录）
        
        Args:
            session_log: session log_dict
        
        Returns:
            True 如果 session 为空，False 否则
        """
        return len(session_log.get("dialogue", [])) == 0
    
    def _session_dialogs_to_string(self, session_dialogs: List[Dict[str, str]]) -> str:
        """
        将单个 session 的 dialogs (list[dict]) 转换为字符串格式
        
        Args:
            session_dialogs: 单个 session 的对话记录列表，格式为 [{'role': 'user/assistant', 'content': 'content'}, ...]
        
        Returns:
            字符串格式的对话记录
        """
        if not session_dialogs:
            return ""
        
        dialog_lines = []
        for dialog in session_dialogs:
            role = dialog.get("role", "")
            content = dialog.get("content", "")
            if role == "user":
                dialog_lines.append(f"{self.user_label}: {content}")
            elif role == "assistant":
                dialog_lines.append(f"{self.assistant_label}: {content}")
        
        return "\n".join(dialog_lines)
    
    def _all_dialogs_to_string(self) -> str:
        """
        将 all_dialogs (List[Dict]) 转换为字符串格式，用于传递给其他模块
        
        Returns:
            字符串格式的历史对话记录
        """
        if not self.all_dialogs:
            return ""
        
        dialog_lines = []
        for session_idx, session_log in enumerate(self.all_dialogs):
            dialogue = session_log.get("dialogue", [])
            if dialogue:
                dialog_lines.append(f"Session {session_idx + 1}:")
                dialog_lines.append(self._session_dialogs_to_string(dialogue))
                dialog_lines.append("")  # 空行分隔不同 session
        
        return "\n".join(dialog_lines)
    
    def _current_session_to_string(self) -> str:
        """
        将当前 session 的 dialogue 转换为字符串格式
        
        Returns:
            当前 session 的字符串格式历史对话记录
        """
        if not self.all_dialogs:
            return ""
        
        current_session = self.all_dialogs[-1]
        dialogue = current_session.get("dialogue", [])
        if not dialogue:
            return ""
        
        return self._session_dialogs_to_string(dialogue)
    
    def _init_modules(self):
        """初始化所有子模块"""
        # 读取各个模块的 prompt 文件并初始化模块
        reaction_config = self.config["reaction_classifier"]
        with open(reaction_config["prompt_path"], "r", encoding="utf-8") as f:
            reaction_prompt = f.read()
        self.reaction_classifier = ReactionClassifier(
            model=reaction_config["model"],
            prompt=reaction_prompt
        )
        
        resistance_config = self.config["resistance_detection"]
        with open(resistance_config["prompt_path"], "r", encoding="utf-8") as f:
            resistance_prompt = f.read()
        self.resistance_detector = ResistanceDetection(
            model=resistance_config["model"],
            prompt=resistance_prompt
        )
        
        strategy_config = self.config["strategy_selection"]
        with open(strategy_config["prompt_path"], "r", encoding="utf-8") as f:
            strategy_prompt = f.read()
        self.strategy_selector = StrategySelection(
            model=strategy_config["model"],
            prompt=strategy_prompt
        )
        
        phase_config = self.config["phase_selection"]
        with open(phase_config["prompt_path"], "r", encoding="utf-8") as f:
            phase_prompt = f.read()
        self.phase_selector = PhaseSelection(
            model=phase_config["model"],
            prompt=phase_prompt
        )
        
        memory_config = self.config["memory_retrieve"]
        with open(memory_config["prompt_path"], "r", encoding="utf-8") as f:
            memory_prompt = f.read()
        self.memory_retriever = MemoryRetrieve(
            model=memory_config["model"],
            prompt=memory_prompt
        )
        
        counselor_config = self.config["counselor"]
        with open(counselor_config["prompt_path"], "r", encoding="utf-8") as f:
            counselor_prompt = f.read()
        self.counselor_agent = CounselorAgent(
            model=counselor_config["model"],
            prompt=counselor_prompt
        )
        
        end_detection_config = self.config["end_detection"]
        with open(end_detection_config["prompt_path"], "r", encoding="utf-8") as f:
            end_detection_prompt = f.read()
        self.end_detector = EndDetection(
            model=end_detection_config["model"],
            prompt=end_detection_prompt
        )
    
    def process(
        self,
        patient_input: str,
        current_therapy: Optional[str] = None,
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
            current_therapy: 当前治疗方案（可选，如果不提供则使用初始化时的值）
            temperature: 温度参数（0-2），控制随机性
            max_tokens: 最大生成 token 数
            top_p: 核采样参数
            frequency_penalty: 频率惩罚（-2.0 到 2.0）
            presence_penalty: 存在惩罚（-2.0 到 2.0）
            stop: 停止序列列表
            **kwargs: 其他推理参数
        
        Returns:
            包含所有中间结果和最终回复的字典
        """
        # 使用传入的 current_therapy 或默认值
        therapy = current_therapy if current_therapy is not None else self.current_therapy
        
        # 确保当前 session 存在
        if not self.all_dialogs:
            self.all_dialogs = [self._create_empty_session_log()]
        current_session = self.all_dialogs[-1]
        
        # 步骤 1: 情感分类和抵抗检测
        reaction_result = self.reaction_classifier.classify(
            utter=patient_input,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            **kwargs
        )
        
        primary_emotion = reaction_result.get("primary_emotion", "")
        emotional_intensity = reaction_result.get("emotional_intensity", 0.0)
        
        # 存储 reaction_result 到当前 session（添加模型名称）
        reaction_result_with_model = reaction_result.copy()
        reaction_model = getattr(self.reaction_classifier, 'model', None)
        if reaction_model:
            reaction_result_with_model["model"] = reaction_model
        current_session["reaction_results"].append(reaction_result_with_model)
        
        resistance = self.resistance_detector.detect(
            utter=patient_input,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            **kwargs
        )
        
        # 存储 resistance 结果到当前 session（改为 Dict 格式，包含模型名称）
        resistance_model = getattr(self.resistance_detector, 'model', None)
        resistance_entry = {"resistance": resistance}
        if resistance_model:
            resistance_entry["model"] = resistance_model
        current_session["resistance_results"].append(resistance_entry)
        
        # 步骤 2: 策略选择
        strategy_result = self.strategy_selector.select_strategy(
            utter=patient_input,
            primary_emotion=primary_emotion,
            emotional_intensity=emotional_intensity,
            resistance=resistance,
            session_strategy_memory=self.session_strategy_memory,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            **kwargs
        )
        
        strategy_name = strategy_result.get("strategy", "")
        strategy_text = strategy_result.get("strategy_text", "")
        
        # 存储 strategy_result 到当前 session（添加模型名称）
        strategy_result_with_model = strategy_result.copy()
        strategy_model = getattr(self.strategy_selector, 'model', None)
        if strategy_model:
            strategy_result_with_model["model"] = strategy_model
        current_session["strategy_results"].append(strategy_result_with_model)
        
        # 更新策略记忆（将新策略添加到列表中）
        if strategy_name and strategy_name not in self.session_strategy_memory:
            self.session_strategy_memory.append(strategy_name)
        
        # 步骤 3: 阶段分析
        current_stage = self.phase_selector.analyze_phase(
            utter=patient_input,
            current_therapy=therapy,
            all_dialogs=self._current_session_to_string(),
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            **kwargs
        )
        
        # 存储 current_stage 到当前 session（改为 Dict 格式，包含模型名称）
        phase_model = getattr(self.phase_selector, 'model', None)
        current_stage_entry = {"content": current_stage}
        if phase_model:
            current_stage_entry["model"] = phase_model
        current_session["current_stage_results"].append(current_stage_entry)
        
        # 步骤 4: 记忆检索
        memory_result = self.memory_retriever.retrieve(
            utter=patient_input,
            all_dialogs=self._all_dialogs_to_string(),
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            **kwargs
        )
        
        # 存储 memory_result 到当前 session（改为 Dict 格式，包含模型名称）
        memory_model = getattr(self.memory_retriever, 'model', None)
        memory_entry = {"content": memory_result}
        if memory_model:
            memory_entry["model"] = memory_model
        current_session["memory_results"].append(memory_entry)
        
        # 步骤 5: 生成咨询师回复
        counselor_result = self.counselor_agent.generate_response(
            utter=patient_input,
            memory_result=memory_result,
            primary_emotion=primary_emotion,
            emotional_intensity=emotional_intensity,
            current_therapy=therapy,
            current_stage=current_stage,
            current_strategy_text=strategy_text,
            session_memory=self._current_session_to_string(),
            current_strategy=strategy_name,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            **kwargs
        )
        
        counselor_response = counselor_result.get("counselor_response", "")
        
        # 步骤 6: 结束检测（在生成回复后）
        end_session = self.end_detector.detect(
            utter=patient_input,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            **kwargs
        )
        
        # 步骤 7: 更新历史记录（包括 dialogue）
        # 获取 counselor 模型名称
        counselor_model = getattr(self.counselor_agent, 'model', None)
        self._update_dialogs(patient_input, counselor_response, model_name=counselor_model)
        
        # 返回所有结果
        return {
            "patient_input": patient_input,
            "reaction_classification": {
                "primary_emotion": primary_emotion,
                "emotional_intensity": emotional_intensity
            },
            "resistance": resistance,
            "strategy_selection": {
                "strategy": strategy_name,
                "strategy_text": strategy_text
            },
            "phase_analysis": current_stage,
            "memory_result": memory_result,
            "counselor_response": counselor_response,
            "end_session": end_session,  # 是否结束会话
            "all_results": counselor_result  # 包含 counselor_agent 返回的所有字段
        }
    
    def _update_dialogs(self, patient_input: str, counselor_response: str, model_name: Optional[str] = None):
        """
        更新历史对话记录（dialogue 部分）
        
        Args:
            patient_input: 用户输入
            counselor_response: 咨询师回复
            model_name: 生成回复的模型名称（可选）
        """
        # 确保 all_dialogs 不为空
        if not self.all_dialogs:
            self.all_dialogs = [self._create_empty_session_log()]
        
        # 获取当前 session（最后一个 Dict）
        current_session = self.all_dialogs[-1]
        
        # 添加用户输入和咨询师回复到当前 session 的 dialogue
        # 用户输入不需要模型名称
        current_session["dialogue"].append({"role": "user", "content": patient_input})
        # 咨询师回复包含模型名称
        assistant_entry = {"role": "assistant", "content": counselor_response}
        if model_name:
            assistant_entry["model"] = model_name
        current_session["dialogue"].append(assistant_entry)
    
    def update_therapy(self, new_therapy: str):
        """
        更新当前治疗方案
        
        Args:
            new_therapy: 新的治疗方案
        """
        self.current_therapy = new_therapy
    
    def get_dialogs(self) -> List[Dict]:
        """
        获取所有历史对话记录
        
        Returns:
            所有历史对话记录，格式为 List[Dict]
            每个 Dict 代表一个 session 的 log_dict，包含：
            - dialogue: List[Dict[str, str]] - 此 session 的聊天记录（assistant 条目包含 model 字段）
            - reaction_results: List[Dict] - 每一轮的 reaction_result 结果列表（包含 model 字段）
            - resistance_results: List[Dict] - 每一轮的 resistance 结果列表（格式：{"resistance": bool, "model": str}）
            - strategy_results: List[Dict] - 每一轮 strategy_result 的结果列表（包含 model 字段）
            - memory_results: List[Dict] - 每一轮 memory_result 的列表（格式：{"content": str, "model": str}）
            - current_stage_results: List[Dict] - 每一轮 current_stage 的结果列表（格式：{"content": str, "model": str}）
            每个 Dict 代表一个 session 的历史记录，按时间从早到晚排列
            当前 session 的记录为 all_dialogs[-1]
        """
        return self.all_dialogs
    
    def get_dialogs_string(self) -> str:
        """
        获取所有历史对话记录的字符串格式（用于兼容性）
        
        Returns:
            所有历史对话记录字符串
        """
        return self._all_dialogs_to_string()
    
    def reset_session(self):
        """
        重置本次会话的策略记忆（但保留历史对话记录）
        开始新的 session，将当前 session 保存，并创建新的空 session
        """
        self.session_strategy_memory = []
        # 如果当前 session 不为空，保留它；然后创建新的空 session
        if self.all_dialogs and not self._is_empty_session(self.all_dialogs[-1]):
            self.all_dialogs.append(self._create_empty_session_log())
        elif not self.all_dialogs:
            self.all_dialogs = [self._create_empty_session_log()]
    
    def clear_dialogs(self):
        """清空所有历史对话记录"""
        self.all_dialogs = [self._create_empty_session_log()]  # 重置为包含一个空 session 的列表
        self.session_strategy_memory = []


# 使用示例
if __name__ == "__main__":
    # 使用默认配置文件（model_config/default_config.json）
    print("=== 使用默认配置文件 ===")
    session = InSession(
        config_path="model_config/default_config.json",
        current_therapy="Cognitive Behavioral Therapy focusing on anxiety management",
        all_dialogs=None  # 或传入 [] 表示空的历史记录
    )
    
    # 处理第一个用户输入
    try:
        result1 = session.process(
            patient_input="I've been feeling very anxious about my job interview next week.",
            temperature=0.7,
            max_tokens=200
        )
        print("=== 第一次对话 ===")
        print(f"用户输入: {result1['patient_input']}")
        print(f"主要情感: {result1['reaction_classification']['primary_emotion']}")
        print(f"情感强度: {result1['reaction_classification']['emotional_intensity']}")
        print(f"是否抵抗: {result1['resistance']}")
        print(f"选择策略: {result1['strategy_selection']['strategy']}")
        print(f"咨询师回复: {result1['counselor_response']}")
        print(f"是否结束会话: {result1['end_session']}")
        print()
    except Exception as e:
        print(f"错误: {e}")
    
    # 处理第二个用户输入（会使用历史记录）
    try:
        result2 = session.process(
            patient_input="I'm worried I won't be able to answer their questions properly.",
            temperature=0.7,
            max_tokens=200
        )
        print("=== 第二次对话 ===")
        print(f"用户输入: {result2['patient_input']}")
        print(f"主要情感: {result2['reaction_classification']['primary_emotion']}")
        print(f"情感强度: {result2['reaction_classification']['emotional_intensity']}")
        print(f"是否抵抗: {result2['resistance']}")
        print(f"选择策略: {result2['strategy_selection']['strategy']}")
        print(f"咨询师回复: {result2['counselor_response']}")
        print(f"是否结束会话: {result2['end_session']}")
        print()
    except Exception as e:
        print(f"错误: {e}")
    
    # 查看历史记录
    print("=== 历史对话记录 ===")
    print("格式化的历史记录:")
    print(session.get_dialogs_string())
    print("\n原始格式 (List[Dict]):")
    import json
    print(json.dumps(session.get_dialogs(), indent=2, ensure_ascii=False))

