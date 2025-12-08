# TheraMind Web 界面

基于 `counseling_manager.py` 的 Web 前端界面，提供友好的用户交互体验。

## 功能特性

- ✅ 文字输入作为来访者
- ✅ 输入对话框和发送按钮
- ✅ 当前会话历史记录显示
- ✅ 过去会话历史记录查看
- ✅ Debug 模式（显示所有中间结果）
- ✅ 存档文件选择和加载
- ✅ 自动保存对话记录

## 安装依赖

```bash
pip install flask flask-cors
```

或者使用项目根目录的 requirements.txt（已包含 Flask 相关依赖）。

## 运行应用

```bash
cd web_interface
python app.py
```

应用将在 `http://localhost:5000` 启动。

## 使用说明

1. **新建会话**：点击"新建会话"按钮开始新的咨询会话
2. **加载存档**：点击"加载存档"按钮选择之前的存档文件继续对话
3. **发送消息**：在输入框中输入您的问题或感受，点击"发送"按钮或按 Enter 键
4. **查看历史**：右侧面板显示所有历史会话记录
5. **Debug 模式**：打开 Debug 开关可以查看每次回复的详细中间结果信息

## 项目结构

```
web_interface/
├── app.py              # Flask 后端应用
├── templates/
│   └── index.html      # 前端 HTML 模板
├── static/
│   ├── css/
│   │   └── style.css   # 样式文件
│   └── js/
│       └── app.js      # 前端 JavaScript
└── README.md           # 本文件
```

## API 接口

- `GET /` - 主页面
- `POST /api/init` - 初始化新会话
- `POST /api/load` - 加载存档文件
- `GET /api/list_files` - 列出所有存档文件
- `POST /api/chat` - 发送消息并获取回复
- `GET /api/status` - 获取当前状态

## 注意事项

- 确保项目根目录存在 `default_config_zh.json` 或 `default_config.json` 配置文件
- 存档文件保存在 `counseling_records/` 目录下
- 应用会自动保存每次对话到存档文件

