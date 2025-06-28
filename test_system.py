#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智慧药房机器人系统测试脚本
用于测试各个模块的基本功能
"""

import os
import sys
import time

# 添加模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# 导入模块
from logger import SystemLogger
from voice_player import VoicePlayer
from image_recognition import ImageRecognition

def test_logger():
    """测试日志系统"""
    print("\n=== 测试日志系统 ===")
    
    logger = SystemLogger()
    logger.start()
    
    # 测试各种日志类型
    logger.log_system("测试系统日志")
    logger.log_uart_receive("test command")
    logger.log_uart_send("ok")
    logger.log_qr_recognition("左上区域", "AB")
    logger.log_ocr_recognition(1, "血常规窗口空闲中", True)
    logger.log_voice("测试语音播报")
    logger.log_error("测试错误日志")
    
    print(f"日志文件路径: {logger.get_log_file_path()}")
    
    # 读取最近的日志
    recent_logs = logger.get_recent_logs(5)
    print("最近的日志:")
    for log in recent_logs:
        print(f"  {log}")
    
    logger.stop()
    print("日志系统测试完成")
    
def test_voice_player():
    """测试语音播报系统"""
    print("\n=== 测试语音播报系统 ===")
    
    logger = SystemLogger()
    logger.start()
    
    voice_player = VoicePlayer(logger)
    voice_player.start()
    
    # 测试各种语音播报
    print("播报系统启动...")
    voice_player.speak_system_start()
    time.sleep(2)
    
    print("播报样本接收...")
    voice_player.speak_sample_received(["静脉血样本", "唾液样本"])
    time.sleep(3)
    
    print("播报窗口忙碌...")
    voice_player.speak_window_busy("血常规窗口")
    time.sleep(2)
    
    print("播报到达配送窗口...")
    voice_player.speak_delivery_arrival("血常规窗口", 2)
    time.sleep(3)
    
    print("播报系统结束...")
    voice_player.speak_system_end()
    time.sleep(2)
    
    voice_player.stop()
    logger.stop()
    print("语音播报系统测试完成")
    
def test_image_recognition():
    """测试图像识别系统"""
    print("\n=== 测试图像识别系统 ===")
    
    logger = SystemLogger()
    logger.start()
    
    image_recognition = ImageRecognition(logger)
    
    # 测试二维码识别（模拟数据）
    print("测试二维码识别...")
    qr_results = image_recognition.recognize_qr_codes_board1()
    print(f"二维码识别结果: {qr_results}")
    
    # 测试样本信息解析
    if qr_results:
        for position, content in qr_results.items():
            sample_info = image_recognition.get_sample_info(position, content)
            print(f"位置 {position}, 内容 {content} -> 样本信息: {sample_info}")
            
            # 测试二维码内容解析
            windows = image_recognition.parse_qr_content(content)
            print(f"  解析窗口: {windows}")
    
    # 测试OCR识别（模拟数据）
    print("\n测试OCR识别...")
    ocr_results = image_recognition.recognize_ocr_board2()
    print(f"OCR识别结果: {ocr_results}")
    
    logger.stop()
    print("图像识别系统测试完成")
    
def test_mappings():
    """测试映射关系"""
    print("\n=== 测试映射关系 ===")
    
    logger = SystemLogger()
    logger.start()
    
    image_recognition = ImageRecognition(logger)
    
    # 显示位置映射
    print("位置映射关系:")
    for position, window_num in image_recognition.position_mapping.items():
        window_name = image_recognition.window_names.get(window_num, f"{window_num}号窗口")
        sample_type = image_recognition.sample_types.get(window_num, "未知样本")
        print(f"  {position} -> {window_num}号窗口 ({window_name}) -> {sample_type}")
    
    # 测试二维码内容解析
    print("\n二维码内容解析测试:")
    test_contents = ["A", "AB", "ABC", "BC", "AC", "B", "C"]
    for content in test_contents:
        windows = image_recognition.parse_qr_content(content)
        print(f"  '{content}' -> 窗口: {windows}, 数量: {len(windows)}")
    
    logger.stop()
    print("映射关系测试完成")
    
def test_integration():
    """集成测试"""
    print("\n=== 集成测试 ===")
    
    logger = SystemLogger()
    logger.start()
    
    voice_player = VoicePlayer(logger)
    voice_player.start()
    
    image_recognition = ImageRecognition(logger)
    
    # 模拟完整的任务流程
    print("模拟任务流程...")
    
    # 1. 系统启动
    print("1. 系统启动")
    voice_player.speak_system_start()
    time.sleep(1)
    
    # 2. 识别板1
    print("2. 识别板1二维码")
    qr_results = image_recognition.recognize_qr_codes_board1()
    print(f"   识别结果: {qr_results}")
    
    # 3. 体检区采样
    print("3. 体检区采样")
    for window in ['A', 'B', 'C']:
        sample_types = []
        for position, content in qr_results.items():
            windows = image_recognition.parse_qr_content(content)
            if window in windows:
                sample_info = image_recognition.get_sample_info(position, content)
                if sample_info:
                    sample_types.append(sample_info['sample_type'])
        
        if sample_types:
            print(f"   {window}窗口采集样本: {sample_types}")
            voice_player.speak_sample_received(sample_types)
            time.sleep(1)
    
    # 4. 识别板2
    print("4. 识别板2 OCR")
    ocr_results = image_recognition.recognize_ocr_board2()
    print(f"   识别结果: {ocr_results}")
    
    # 5. 化验区配送
    print("5. 化验区配送")
    for window_num in [1, 2, 3, 4]:
        sample_count = 0
        for position, content in qr_results.items():
            sample_info = image_recognition.get_sample_info(position, content)
            if sample_info and sample_info['window_number'] == window_num:
                sample_count += sample_info['sample_count']
        
        window_name = image_recognition.window_names.get(window_num, f"{window_num}号窗口")
        if sample_count > 0:
            print(f"   到达{window_name}，样本数: {sample_count}")
            voice_player.speak_delivery_arrival(window_name, sample_count)
            time.sleep(1)
        else:
            print(f"   通过{window_name}")
    
    # 6. 任务结束
    print("6. 任务结束")
    voice_player.speak_system_end()
    time.sleep(1)
    
    voice_player.stop()
    logger.stop()
    print("集成测试完成")
    
def main():
    """主测试函数"""
    print("智慧药房机器人系统测试")
    print("=" * 50)
    
    try:
        # 运行各项测试
        test_logger()
        test_voice_player()
        test_image_recognition()
        test_mappings()
        test_integration()
        
        print("\n" + "=" * 50)
        print("所有测试完成！")
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        
if __name__ == "__main__":
    main()