#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智慧药房机器人上位机程序
负责串口通信、图像识别、语音播报和日志记录
"""

import os
import sys
import time
import threading
from datetime import datetime

# 添加模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# 导入自定义模块
from serial_comm import SerialCommunication
from image_recognition import ImageRecognition
from voice_player import VoicePlayer
from logger import SystemLogger
from task_controller import TaskController

class PharmacyRobotSystem:
    """智慧药房机器人系统主类"""
    
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        """初始化系统
        
        Args:
            port: 串口端口
            baudrate: 波特率
        """
        self.running = False
        
        # 初始化日志系统
        self.logger = SystemLogger()
        
        # 初始化串口通信
        self.serial_comm = SerialCommunication(port, baudrate, self.logger)
        
        # 初始化图像识别
        self.image_recognition = ImageRecognition(self.logger)
        
        # 初始化语音播报
        self.voice_player = VoicePlayer(self.logger)
        
        # 初始化任务控制器
        self.task_controller = TaskController(
            self.logger,
            self.serial_comm,
            self.image_recognition,
            self.voice_player
        )
        
        # 设置串口数据接收回调
        self.serial_comm.set_data_callback(self._handle_serial_data)
        
        print("智慧药房机器人系统初始化完成")
        
    def start(self):
        """启动系统"""
        try:
            self.running = True
            
            # 启动日志系统
            self.logger.start()
            self.logger.log_system("系统启动")
            
            # 启动串口通信
            if not self.serial_comm.connect():
                raise Exception("串口连接失败")
                
            # 启动语音播报
            self.voice_player.start()
            
            # 启动任务控制器
            self.task_controller.start()
            
            print("智慧药房机器人系统启动成功")
            self.logger.log_system("系统启动成功")
            
        except Exception as e:
            error_msg = f"系统启动失败: {str(e)}"
            print(error_msg)
            if hasattr(self, 'logger'):
                self.logger.log_error(error_msg)
            self.stop()
            raise
            
    def stop(self):
        """停止系统"""
        self.running = False
        
        print("正在停止智慧药房机器人系统...")
        
        # 停止任务控制器
        if hasattr(self, 'task_controller'):
            self.task_controller.stop()
            
        # 停止语音播报
        if hasattr(self, 'voice_player'):
            self.voice_player.stop()
            
        # 停止串口通信
        if hasattr(self, 'serial_comm'):
            self.serial_comm.disconnect()
            
        # 停止日志系统
        if hasattr(self, 'logger'):
            self.logger.log_system("系统停止")
            self.logger.stop()
            
        print("智慧药房机器人系统已停止")
        
    def _handle_serial_data(self, data):
        """处理串口接收到的数据
        
        Args:
            data: 接收到的数据
        """
        if not self.running:
            return
            
        try:
            # 清理数据（去除换行符等）
            command = data.strip()
            
            if command:
                # 交给任务控制器处理
                self.task_controller.handle_command(command)
                
        except Exception as e:
            error_msg = f"处理串口数据异常: {str(e)}"
            print(error_msg)
            self.logger.log_error(error_msg)
            
    def get_system_status(self):
        """获取系统状态
        
        Returns:
            dict: 系统状态信息
        """
        return {
            'running': self.running,
            'serial_connected': self.serial_comm.is_connected() if hasattr(self, 'serial_comm') else False,
            'task_status': self.task_controller.get_current_status() if hasattr(self, 'task_controller') else {},
            'log_file': self.logger.get_log_file_path() if hasattr(self, 'logger') else None
        }
        
    def run_interactive_mode(self):
        """运行交互模式（用于测试）"""
        print("\n进入交互模式，输入指令进行测试:")
        print("可用指令: start, check board 1, check A/B/C, check board 2, check 1/2/3/4, over")
        print("输入 'quit' 退出交互模式\n")
        
        while self.running:
            try:
                command = input("请输入指令: ").strip()
                
                if command.lower() == 'quit':
                    break
                elif command.lower() == 'status':
                    status = self.get_system_status()
                    print(f"系统状态: {status}")
                elif command:
                    self.task_controller.handle_command(command)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"处理指令异常: {str(e)}")
                
def main():
    """主函数"""
    # 检查命令行参数
    port = '/dev/ttyUSB0'  # 默认串口
    interactive = False
    
    if len(sys.argv) > 1:
        if '--interactive' in sys.argv or '-i' in sys.argv:
            interactive = True
        if '--port' in sys.argv:
            port_index = sys.argv.index('--port') + 1
            if port_index < len(sys.argv):
                port = sys.argv[port_index]
                
    # macOS系统可能使用不同的串口名称
    if sys.platform == 'darwin':  # macOS
        port = '/dev/tty.usbserial-0001'  # 根据实际情况调整
        
    print(f"使用串口: {port}")
    
    system = PharmacyRobotSystem(port=port)
    
    try:
        system.start()
        
        if interactive:
            # 交互模式
            system.run_interactive_mode()
        else:
            # 正常运行模式
            print("系统正在运行，按 Ctrl+C 停止...")
            while system.running:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n接收到中断信号，正在停止系统...")
    except Exception as e:
        print(f"系统运行异常: {str(e)}")
    finally:
        system.stop()

if __name__ == "__main__":
    main()