#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
串口自动验证程序
用于测试串口通信，支持快捷指令发送和接收验证
"""

import serial
import threading
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable
import argparse
import sys
import os

# 添加模块路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import Config

class SerialTester:
    """串口测试器"""
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn: Optional[serial.Serial] = None
        self.is_connected = False
        self.is_listening = False
        self.listen_thread: Optional[threading.Thread] = None
        self.received_data: List[str] = []
        self.test_results: List[Dict] = []
        
        # 预定义快捷指令
        self.quick_commands = {
            '1': {'cmd': 'STATUS', 'desc': '查询状态'},
            '2': {'cmd': 'RESET', 'desc': '重置系统'},
            '3': {'cmd': 'START', 'desc': '开始任务'},
            '4': {'cmd': 'STOP', 'desc': '停止任务'},
            '5': {'cmd': 'GET_INFO', 'desc': '获取信息'},
            '6': {'cmd': 'TEST_LED', 'desc': '测试LED'},
            '7': {'cmd': 'TEST_MOTOR', 'desc': '测试电机'},
            '8': {'cmd': 'GET_SENSOR', 'desc': '读取传感器'},
            '9': {'cmd': 'CALIBRATE', 'desc': '校准系统'},
            '0': {'cmd': 'PING', 'desc': 'Ping测试'}
        }
        
    def connect(self) -> bool:
        """连接串口"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self.is_connected = True
            print(f"✓ 串口连接成功: {self.port} @ {self.baudrate}")
            return True
        except Exception as e:
            print(f"✗ 串口连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开串口连接"""
        self.stop_listening()
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.is_connected = False
        print("串口已断开")
    
    def start_listening(self):
        """开始监听串口数据"""
        if not self.is_connected:
            print("请先连接串口")
            return
        
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        print("开始监听串口数据...")
    
    def stop_listening(self):
        """停止监听"""
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=1.0)
    
    def _listen_loop(self):
        """监听循环"""
        while self.is_listening and self.serial_conn and self.serial_conn.is_open:
            try:
                if self.serial_conn.in_waiting > 0:
                    data = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                    if data:
                        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                        formatted_data = f"[{timestamp}] RX: {data}"
                        print(formatted_data)
                        self.received_data.append(formatted_data)
                time.sleep(0.01)
            except Exception as e:
                print(f"监听错误: {e}")
                break
    
    def send_command(self, command: str, expect_response: bool = True, timeout: float = 2.0) -> Dict:
        """发送指令并记录结果"""
        if not self.is_connected:
            return {'success': False, 'error': '串口未连接'}
        
        try:
            # 清空接收缓冲区
            self.serial_conn.reset_input_buffer()
            
            # 发送指令
            send_data = command + '\r\n'
            self.serial_conn.write(send_data.encode('utf-8'))
            
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            print(f"[{timestamp}] TX: {command}")
            
            result = {
                'timestamp': timestamp,
                'command': command,
                'success': True,
                'response': None,
                'response_time': None
            }
            
            if expect_response:
                start_time = time.time()
                response_received = False
                
                while time.time() - start_time < timeout:
                    if self.serial_conn.in_waiting > 0:
                        response = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                        if response:
                            response_time = time.time() - start_time
                            result['response'] = response
                            result['response_time'] = f"{response_time:.3f}s"
                            
                            resp_timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                            print(f"[{resp_timestamp}] RX: {response} (耗时: {response_time:.3f}s)")
                            response_received = True
                            break
                    time.sleep(0.01)
                
                if not response_received:
                    result['error'] = f'超时未收到响应 (>{timeout}s)'
                    print(f"⚠ 超时未收到响应 (>{timeout}s)")
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            error_result = {
                'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3],
                'command': command,
                'success': False,
                'error': str(e)
            }
            self.test_results.append(error_result)
            print(f"✗ 发送失败: {e}")
            return error_result
    
    def run_quick_test(self, commands: List[str], delay: float = 0.5) -> List[Dict]:
        """运行快速测试序列"""
        print(f"\n开始快速测试，共 {len(commands)} 个指令...")
        results = []
        
        for i, cmd in enumerate(commands, 1):
            print(f"\n[{i}/{len(commands)}] 执行指令: {cmd}")
            result = self.send_command(cmd)
            results.append(result)
            
            if i < len(commands):
                time.sleep(delay)
        
        print(f"\n快速测试完成，成功: {sum(1 for r in results if r['success'])}/{len(results)}")
        return results
    
    def show_quick_commands(self):
        """显示快捷指令列表"""
        print("\n=== 快捷指令列表 ===")
        for key, info in self.quick_commands.items():
            print(f"{key}: {info['cmd']} - {info['desc']}")
        print("q: 退出程序")
        print("h: 显示帮助")
        print("s: 显示统计信息")
        print("c: 清空历史记录")
        print("t: 运行快速测试")
        print("===================\n")
    
    def show_statistics(self):
        """显示统计信息"""
        if not self.test_results:
            print("暂无测试记录")
            return
        
        total = len(self.test_results)
        success = sum(1 for r in self.test_results if r['success'])
        failed = total - success
        
        print(f"\n=== 测试统计 ===")
        print(f"总计: {total}")
        print(f"成功: {success} ({success/total*100:.1f}%)")
        print(f"失败: {failed} ({failed/total*100:.1f}%)")
        
        # 显示最近的响应时间
        recent_times = []
        for r in self.test_results[-10:]:
            if r.get('response_time'):
                try:
                    time_val = float(r['response_time'].replace('s', ''))
                    recent_times.append(time_val)
                except:
                    pass
        
        if recent_times:
            avg_time = sum(recent_times) / len(recent_times)
            print(f"平均响应时间: {avg_time:.3f}s (最近{len(recent_times)}次)")
        
        print("================\n")
    
    def save_results(self, filename: str = None):
        """保存测试结果"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"serial_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'test_info': {
                        'port': self.port,
                        'baudrate': self.baudrate,
                        'total_tests': len(self.test_results),
                        'export_time': datetime.now().isoformat()
                    },
                    'results': self.test_results
                }, f, ensure_ascii=False, indent=2)
            print(f"测试结果已保存到: {filename}")
        except Exception as e:
            print(f"保存失败: {e}")
    
    def interactive_mode(self):
        """交互模式"""
        print("\n=== 串口测试器 - 交互模式 ===")
        print(f"连接到: {self.port} @ {self.baudrate}")
        
        if not self.connect():
            return
        
        self.start_listening()
        self.show_quick_commands()
        
        try:
            while True:
                user_input = input("请输入指令 (h=帮助): ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'q':
                    break
                elif user_input.lower() == 'h':
                    self.show_quick_commands()
                elif user_input.lower() == 's':
                    self.show_statistics()
                elif user_input.lower() == 'c':
                    self.test_results.clear()
                    self.received_data.clear()
                    print("历史记录已清空")
                elif user_input.lower() == 't':
                    # 运行快速测试
                    test_commands = [info['cmd'] for info in self.quick_commands.values()]
                    self.run_quick_test(test_commands[:5])  # 测试前5个指令
                elif user_input in self.quick_commands:
                    # 快捷指令
                    cmd_info = self.quick_commands[user_input]
                    print(f"执行: {cmd_info['desc']}")
                    self.send_command(cmd_info['cmd'])
                else:
                    # 自定义指令
                    self.send_command(user_input)
                    
        except KeyboardInterrupt:
            print("\n用户中断")
        finally:
            # 询问是否保存结果
            if self.test_results:
                save = input("\n是否保存测试结果? (y/n): ").strip().lower()
                if save == 'y':
                    self.save_results()
            
            self.disconnect()
            print("程序退出")

def main():
    parser = argparse.ArgumentParser(description='串口自动验证程序')
    parser.add_argument('--port', '-p', help='串口设备路径')
    parser.add_argument('--baudrate', '-b', type=int, default=9600, help='波特率 (默认: 9600)')
    parser.add_argument('--timeout', '-t', type=float, default=1.0, help='超时时间 (默认: 1.0s)')
    parser.add_argument('--config', action='store_true', help='显示当前配置')
    parser.add_argument('--test', help='运行指定的测试指令 (逗号分隔)')
    
    args = parser.parse_args()
    
    # 加载配置
    config = Config()
    
    if args.config:
        print("=== 当前配置 ===")
        print(f"串口设备: {config.SERIAL_PORT}")
        print(f"波特率: {config.SERIAL_BAUDRATE}")
        print(f"超时时间: {config.SERIAL_TIMEOUT}")
        print(f"最大重试: {config.SERIAL_MAX_RETRIES}")
        return
    
    # 确定串口参数
    port = args.port or config.SERIAL_PORT
    baudrate = args.baudrate or config.SERIAL_BAUDRATE
    timeout = args.timeout or config.SERIAL_TIMEOUT
    
    if not port:
        print("错误: 请指定串口设备 (--port 或在配置文件中设置)")
        return
    
    # 创建测试器
    tester = SerialTester(port, baudrate, timeout)
    
    if args.test:
        # 批量测试模式
        commands = [cmd.strip() for cmd in args.test.split(',')]
        print(f"批量测试模式，指令: {commands}")
        
        if tester.connect():
            tester.start_listening()
            results = tester.run_quick_test(commands)
            tester.show_statistics()
            tester.save_results()
            tester.disconnect()
    else:
        # 交互模式
        tester.interactive_mode()

if __name__ == '__main__':
    main()