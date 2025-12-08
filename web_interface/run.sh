#!/bin/bash
# TheraMind Web 界面启动脚本

# 获取脚本所在目录（web_interface 目录）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 切换到 web_interface 目录
cd "$SCRIPT_DIR" || exit 1

# 检查 app.py 是否存在
if [ ! -f "app.py" ]; then
    echo "错误: 找不到 app.py 文件"
    echo "当前目录: $(pwd)"
    exit 1
fi

# 运行 app.py（使用绝对路径确保正确）
python "$SCRIPT_DIR/app.py"

