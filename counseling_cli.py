#!/usr/bin/env python3
"""
咨询管理命令行界面
用于通过命令行与咨询管理系统交互
"""

import argparse
import sys
from counseling_manager import CounselingManager


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="咨询管理命令行界面 - 与咨询管理系统交互",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认配置创建新咨询
  python counseling_cli.py
  
  # 指定配置文件
  python counseling_cli.py --config_path my_config.json
  
  # 从文件加载继续咨询
  python counseling_cli.py --all_dialogs_file counseling_records/counseling_20240101_120000.json
  
  # 同时指定配置文件和咨询记录文件
  python counseling_cli.py --config_path my_config.json --all_dialogs_file counseling_records/counseling_20240101_120000.json
        """
    )
    
    parser.add_argument(
        "--config_path",
        type=str,
        default="model_config/default_config_zh.json",
        help="配置文件路径（默认: model_config/default_config_zh.json）"
    )
    
    parser.add_argument(
        "--all_dialogs_file",
        type=str,
        default=None,
        help="咨询记录文件路径（默认: None，创建新咨询）"
    )
    
    parser.add_argument(
        "--storage_dir",
        type=str,
        default="counseling_records",
        help="存储目录（默认: counseling_records）"
    )
    
    parser.add_argument(
        "--initial_therapy",
        type=str,
        default=None,
        help="首次咨询的治疗方案（仅在新咨询时使用，默认: 认知行为疗法（CBT））"
    )
    
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="启用调试模式，显示详细的中间处理结果"
    )
    
    args = parser.parse_args()
    
    # 初始化咨询管理器
    try:
        print("正在初始化咨询管理系统...")
        manager = CounselingManager(
            config_path=args.config_path,
            all_dialogs_file=args.all_dialogs_file,
            storage_dir=args.storage_dir,
            initial_therapy=args.initial_therapy
        )
        
        if args.all_dialogs_file:
            print(f"✓ 已从文件加载咨询记录: {args.all_dialogs_file}")
        else:
            print(f"✓ 已创建新的咨询记录: {manager.get_all_dialogs_file()}")
        
        print(f"✓ 当前治疗方案: {manager.get_current_therapy()}")
        print(f"✓ 历史 session 数量: {len(manager.get_all_dialogs())}")
        print("\n" + "="*60)
        print("咨询系统已就绪，请输入来访者的对话（输入 'quit' 或 'exit' 退出）")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"错误: 初始化咨询管理系统失败")
        print(f"详细信息: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 交互式循环
    try:
        while True:
            # 获取用户输入
            try:
                patient_input = input("来访者: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\n程序已退出")
                break
            
            # 检查退出命令
            if patient_input.lower() in ['quit', 'exit', 'q']:
                print("\n程序已退出")
                break
            
            # 检查空输入
            if not patient_input:
                print("请输入有效的对话内容")
                continue
            
            # 处理用户输入
            try:
                print("\n正在处理...")
                result = manager.process(
                    patient_input=patient_input,
                    temperature=0.7,
                    max_tokens=500
                )
                
                # 显示咨询师回复
                counselor_response = result.get("counselor_response", "")
                print(f"\n咨询师: {counselor_response}\n")
                
                # 显示额外信息（可选）
                end_session = result.get("end_session", False)
                if end_session:
                    print("⚠ 本次会话已结束")
                    
                    # 显示 cross_session 结果
                    if "cross_session" in result:
                        cross_result = result["cross_session"]
                        new_therapy = cross_result.get("new_therapy", "")
                        reason = cross_result.get("reason", "")
                        if new_therapy:
                            print(f"✓ 新的治疗方案: {new_therapy}")
                            if reason:
                                print(f"  原因: {reason}")
                    
                    print(f"✓ 已开始新的 session\n")
                
                # 显示中间结果（调试用，可选）
                if args.debug:
                    print("\n[调试信息]")
                    print(f"  主要情感: {result.get('reaction_classification', {}).get('primary_emotion', 'N/A')}")
                    print(f"  情感强度: {result.get('reaction_classification', {}).get('emotional_intensity', 'N/A')}")
                    print(f"  是否抵抗: {result.get('resistance', 'N/A')}")
                    print(f"  选择策略: {result.get('strategy_selection', {}).get('strategy', 'N/A')}")
                    print(f"  当前阶段: {result.get('phase_analysis', 'N/A')}")
                    memory_result = result.get('memory_result', 'N/A')
                    if memory_result and memory_result != 'N/A':
                        print(f"  召回记忆: {memory_result}")
                    else:
                        print(f"  召回记忆: 无")
                    print()
                
            except Exception as e:
                print(f"\n错误: 处理用户输入时发生错误")
                print(f"详细信息: {e}")
                import traceback
                traceback.print_exc()
                print()
                continue
    
    except KeyboardInterrupt:
        print("\n\n程序已中断")
    finally:
        # 保存状态
        try:
            manager.save()
            print(f"\n✓ 咨询记录已保存到: {manager.get_all_dialogs_file()}")
        except Exception as e:
            print(f"\n警告: 保存咨询记录时发生错误: {e}")


if __name__ == "__main__":
    main()

