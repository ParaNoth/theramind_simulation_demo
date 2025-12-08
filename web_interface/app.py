"""
Flask 后端应用
封装 counseling_manager.py 提供 Web API
"""

import os
import sys
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# 获取项目根目录和 web_interface 目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_INTERFACE_DIR = os.path.dirname(os.path.abspath(__file__))

# 切换到项目根目录，确保相对路径能正确找到 prompts 等目录
os.chdir(BASE_DIR)

# 添加父目录到路径，以便导入 counseling_manager
sys.path.insert(0, BASE_DIR)

from counseling_manager import CounselingManager

# 创建 Flask 应用，指定模板和静态文件目录
app = Flask(
    __name__,
    template_folder=os.path.join(WEB_INTERFACE_DIR, 'templates'),
    static_folder=os.path.join(WEB_INTERFACE_DIR, 'static')
)
CORS(app)

# 全局变量存储当前的咨询管理器
current_manager = None
storage_dir = os.path.join(BASE_DIR, "counseling_records")
config_dir = os.path.join(BASE_DIR, "model_config")


def get_config_path(config_path=None):
    """获取配置文件路径"""
    # 确保 model_config 目录存在
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    if config_path:
        # 如果提供了配置文件路径
        if os.path.isabs(config_path):
            # 绝对路径
            if os.path.exists(config_path):
                return config_path
            else:
                raise FileNotFoundError(f"配置文件不存在: {config_path}")
        else:
            # 相对路径，相对于 model_config 文件夹
            full_path = os.path.join(config_dir, config_path)
            if os.path.exists(full_path):
                return full_path
            else:
                raise FileNotFoundError(f"配置文件不存在: {full_path}")
    
    # 默认行为：从 model_config 文件夹优先使用中文配置
    config_zh = os.path.join(config_dir, "default_config_zh.json")
    config_en = os.path.join(config_dir, "default_config.json")
    
    # 如果 model_config 文件夹中没有，回退到项目根目录（向后兼容）
    if os.path.exists(config_zh):
        return config_zh
    elif os.path.exists(config_en):
        return config_en
    else:
        # 回退到项目根目录的旧配置文件
        fallback_zh = os.path.join(BASE_DIR, "default_config_zh.json")
        fallback_en = os.path.join(BASE_DIR, "default_config.json")
        if os.path.exists(fallback_zh):
            return fallback_zh
        elif os.path.exists(fallback_en):
            return fallback_en
        else:
            raise FileNotFoundError("找不到配置文件")


@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')


@app.route('/api/init', methods=['POST'])
def init_counseling():
    """初始化新的咨询会话"""
    global current_manager
    
    try:
        data = request.json or {}
        initial_therapy = data.get('initial_therapy', None)
        config_path_param = data.get('config_path', None)
        
        # 获取配置文件路径
        config_path = get_config_path(config_path_param)
        
        current_manager = CounselingManager(
            config_path=config_path,
            all_dialogs_file=None,
            storage_dir=storage_dir,
            initial_therapy=initial_therapy
        )
        
        return jsonify({
            'success': True,
            'message': '咨询会话已初始化',
            'file_path': current_manager.get_all_dialogs_file(),
            'current_therapy': current_manager.get_current_therapy(),
            'session_count': len(current_manager.get_all_dialogs()),
            'config_path': config_path
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'初始化失败: {str(e)}'
        }), 500


@app.route('/api/load', methods=['POST'])
def load_counseling():
    """加载存档文件继续咨询"""
    global current_manager
    
    try:
        data = request.json or {}
        file_path = data.get('file_path')
        config_path_param = data.get('config_path', None)
        
        if not file_path:
            return jsonify({
                'success': False,
                'message': '未提供文件路径'
            }), 400
        
        # 如果是相对路径，转换为绝对路径
        if not os.path.isabs(file_path):
            file_path = os.path.join(storage_dir, file_path)
        
        # 获取配置文件路径
        config_path = get_config_path(config_path_param)
        
        current_manager = CounselingManager(
            config_path=config_path,
            all_dialogs_file=file_path,
            storage_dir=storage_dir
        )
        
        # 获取所有历史记录
        all_dialogs = current_manager.get_all_dialogs()
        
        return jsonify({
            'success': True,
            'message': '存档文件加载成功',
            'file_path': current_manager.get_all_dialogs_file(),
            'current_therapy': current_manager.get_current_therapy(),
            'session_count': len(all_dialogs),
            'all_dialogs': all_dialogs,
            'config_path': config_path
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'加载失败: {str(e)}'
        }), 500


@app.route('/api/list_files', methods=['GET'])
def list_files():
    """列出所有存档文件"""
    try:
        if not os.path.exists(storage_dir):
            return jsonify({
                'success': True,
                'files': []
            })
        
        files = []
        for filename in os.listdir(storage_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(storage_dir, filename)
                file_stat = os.stat(file_path)
                files.append({
                    'filename': filename,
                    'file_path': file_path,
                    'modified_time': file_stat.st_mtime
                })
        
        # 按修改时间排序（最新的在前）
        files.sort(key=lambda x: x['modified_time'], reverse=True)
        
        return jsonify({
            'success': True,
            'files': files
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'列出文件失败: {str(e)}'
        }), 500


@app.route('/api/list_configs', methods=['GET'])
def list_configs():
    """列出所有可用的配置文件（从 model_config 文件夹）"""
    try:
        configs = []
        
        # 确保 model_config 目录存在
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # 查找 model_config 文件夹下的所有 config 文件
        if os.path.exists(config_dir):
            for filename in os.listdir(config_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(config_dir, filename)
                    if os.path.isfile(file_path):
                        file_stat = os.stat(file_path)
                        configs.append({
                            'filename': filename,
                            'file_path': file_path,
                            'modified_time': file_stat.st_mtime
                        })
        
        # 按文件名排序
        configs.sort(key=lambda x: x['filename'])
        
        return jsonify({
            'success': True,
            'configs': configs
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'列出配置文件失败: {str(e)}'
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """处理用户输入并返回咨询师回复"""
    global current_manager
    
    if current_manager is None:
        return jsonify({
            'success': False,
            'message': '请先初始化或加载咨询会话'
        }), 400
    
    try:
        data = request.json or {}
        patient_input = data.get('patient_input', '').strip()
        
        if not patient_input:
            return jsonify({
                'success': False,
                'message': '输入不能为空'
            }), 400
        
        # 可选参数
        temperature = data.get('temperature')
        max_tokens = data.get('max_tokens')
        top_p = data.get('top_p')
        frequency_penalty = data.get('frequency_penalty')
        presence_penalty = data.get('presence_penalty')
        stop = data.get('stop')
        
        # 构建参数
        kwargs = {}
        if temperature is not None:
            kwargs['temperature'] = temperature
        if max_tokens is not None:
            kwargs['max_tokens'] = max_tokens
        if top_p is not None:
            kwargs['top_p'] = top_p
        if frequency_penalty is not None:
            kwargs['frequency_penalty'] = frequency_penalty
        if presence_penalty is not None:
            kwargs['presence_penalty'] = presence_penalty
        if stop is not None:
            kwargs['stop'] = stop
        
        # 处理用户输入
        result = current_manager.process(patient_input=patient_input, **kwargs)
        
        # 获取当前所有对话记录
        all_dialogs = current_manager.get_all_dialogs()
        
        return jsonify({
            'success': True,
            'result': result,
            'all_dialogs': all_dialogs,
            'current_therapy': current_manager.get_current_therapy(),
            'file_path': current_manager.get_all_dialogs_file()
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'处理失败: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """获取当前状态"""
    global current_manager
    
    if current_manager is None:
        return jsonify({
            'success': True,
            'initialized': False
        })
    
    all_dialogs = current_manager.get_all_dialogs()
    
    return jsonify({
        'success': True,
        'initialized': True,
        'file_path': current_manager.get_all_dialogs_file(),
        'current_therapy': current_manager.get_current_therapy(),
        'session_count': len(all_dialogs),
        'all_dialogs': all_dialogs
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

