# TheraMind 复现项目

本项目是对论文 [TheraMind: A Strategic and Adaptive Agent for Longitudinal Psychological Counseling](https://arxiv.org/abs/2510.25758) 的复现实现。

## 论文简介

TheraMind 是一个用于纵向心理咨询的战略性和适应性智能体。该系统的核心是一个新颖的双循环架构，将复杂的咨询过程解耦为：
- **会话内循环（Intra-Session Loop）**：用于战术性对话管理
- **会话间循环（Cross-Session Loop）**：用于战略性治疗规划

该系统能够感知患者的情绪状态，动态选择响应策略，并在多个会话中利用长期记忆确保连续性。通过评估每次会话后应用的治疗效果，系统能够调整后续交互的治疗方法。

## 环境要求

- Python 3.x
- 需要设置环境变量 `OPENROUTER_API_KEY`

## 安装

1. 克隆或下载本项目

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 设置环境变量：
```bash
export OPENROUTER_API_KEY="your_api_key_here"
```

或者在 Windows 上：
```cmd
set OPENROUTER_API_KEY=your_api_key_here
```

## 快速开始

项目提供两种使用方式：命令行界面和 Web 界面。

### 方式一：命令行界面

运行命令行界面开始咨询：

```bash
python counseling_cli.py
```

### 方式二：Web 界面

启动 Web 界面提供更友好的交互体验：

```bash
cd web_interface
python app.py
```

应用将在 `http://localhost:5000` 启动，在浏览器中打开该地址即可使用。

**Web 界面功能：**
- 文字输入作为来访者
- 实时显示当前会话和历史会话记录
- 支持新建会话和加载存档文件
- 可开启 Debug 模式查看详细中间结果
- 自动保存对话记录

### 基本用法

**创建新咨询（使用默认配置）：**
```bash
python counseling_cli.py
```

**指定配置文件：**
```bash
python counseling_cli.py --config_path my_config.json
```

**从已有记录继续咨询：**
```bash
python counseling_cli.py --all_dialogs_file counseling_records/counseling_20240101_120000.json
```

**启用调试模式（显示详细中间处理结果）：**
```bash
python counseling_cli.py --debug
```

### 命令行参数

- `--config_path`: 配置文件路径（默认: `default_config_zh.json`）
- `--all_dialogs_file`: 咨询记录文件路径（默认: None，创建新咨询）
- `--storage_dir`: 存储目录（默认: `counseling_records`）
- `--initial_therapy`: 首次咨询的治疗方案（仅在新咨询时使用）
- `--debug` / `-d`: 启用调试模式

### 使用示例

启动后，系统会提示您输入来访者的对话。输入 `quit` 或 `exit` 退出程序。

```
来访者: 我最近感到非常焦虑
咨询师: [系统生成的咨询回复]

来访者: 我晚上总是睡不着
咨询师: [系统生成的咨询回复]

来访者: quit
```

## 项目结构

```
.
├── counseling_cli.py          # 命令行界面入口
├── counseling_manager.py      # 咨询管理器
├── in_session.py              # 会话内处理逻辑
├── cross_session.py           # 会话间处理逻辑
├── client_agent.py            # 客户端代理
├── module/                    # 核心模块
│   ├── counselor_agent.py    # 咨询师智能体
│   ├── reaction_classifier.py # 反应分类器
│   ├── resistance_detection.py # 抵抗检测
│   ├── strategy_selection.py  # 策略选择
│   └── ...
├── prompts/                   # 提示词模板
│   ├── counselor/            # 咨询师提示词
│   ├── reaction_classifier/   # 反应分类提示词
│   └── ...
├── counseling_records/        # 咨询记录存储目录
└── default_config_zh.json    # 默认配置文件（中文）
```

## 配置文件

项目使用 JSON 格式的配置文件来指定各个模块使用的模型和提示词路径。配置文件包含以下主要配置项：

- `reaction_classifier`: 反应分类器模块的模型和提示词
- `resistance_detection`: 抵抗检测模块的模型和提示词
- `strategy_selection`: 策略选择模块的模型和提示词
- `phase_selection`: 阶段选择模块的模型和提示词
- `memory_retrieve`: 记忆检索模块的模型和提示词
- `counselor`: 咨询师智能体的模型和提示词
- `end_detection`: 会话结束检测模块的模型和提示词
- `therapy_selection`: 治疗方案选择模块的模型和提示词
- `dialog_labels`: 对话标签（用户和助手的显示名称）

### 默认配置文件

项目提供了两个默认配置文件，分别对应不同的语言环境：

- **`default_config_zh.json`**: 中文配置文件
  - 使用中文提示词模板（位于 `prompts/*/.*_zh.txt`）
  - 对话标签为"来访者"和"咨询师"
  - 默认使用 `deepseek/deepseek-chat-v3-0324` 模型

- **`default_config.json`**: 英文配置文件
  - 使用英文提示词模板（位于 `prompts/*/.*_en.txt`）
  - 对话标签为"Patient"和"Therapist"
  - 默认使用 `openai/gpt-4.1-mini` 模型

### 使用自定义配置文件

您可以通过 `--config_path` 参数指定自定义配置文件：

```bash
python counseling_cli.py --config_path my_custom_config.json
```

配置文件中的每个模块都需要指定：
- `model`: 使用的模型名称（需通过 OpenRouter API 访问）
- `prompt_path`: 对应的提示词文件路径

## 咨询记录

所有咨询记录会自动保存到 `counseling_records/` 目录下，文件名格式为 `counseling_YYYYMMDD_HHMMSS.json`。您可以使用这些记录文件来继续之前的咨询会话。

## 引用

原始论文：

```bibtex
@article{hu2025theramind,
  title={TheraMind: A Strategic and Adaptive Agent for Longitudinal Psychological Counseling},
  author={Hu, He and Zhou, Yucheng and Ma, Chiyuan and Wang, Qianning and Zhang, Zheng and Ma, Fei and Cui, Laizhong and Tian, Qi},
  journal={arXiv preprint arXiv:2510.25758},
  year={2025}
}
```

## 许可证

请参考原始论文和代码仓库的许可证信息。

## 注意事项

- 本项目仅用于研究和教育目的
- 不应用于实际的临床诊断或治疗
- 使用前请确保已正确配置 API 密钥
- 咨询记录包含敏感信息，请妥善保管

