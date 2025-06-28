#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
串口通信模块
实现UART串口通信功能
波特率：115200
数据格式：ASCII文本
"""

import serial
import time
import threading
from queue import Queue

class SerialCommunication:
    """串口通信类"""
    
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.connected = False
        
        # 接收数据队列
        self.receive_queue = Queue()
        self.receive_thread = None
        self.running = False
        
        # 重试机制
        self.max_retries = 3
        
        # 数据回调函数
        self.data_callback = None
        
    def connect(self):
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
            
            if self.serial_conn.is_open:
                self.connected = True
                self.running = True
                
                # 启动接收线程
                self.receive_thread = threading.Thread(target=self._receive_loop)
                self.receive_thread.daemon = True
                self.receive_thread.start()
                
                print(f"串口连接成功: {self.port}")
                return True
            else:
                print(f"串口连接失败: {self.port}")
                return False
                
        except Exception as e:
            print(f"串口连接异常: {str(e)}")
            return False
            
    def disconnect(self):
        """断开串口连接"""
        self.running = False
        self.connected = False
        
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1)
            
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("串口连接已断开")
            
    def _receive_loop(self):
        """接收数据循环"""
        while self.running and self.connected:
            try:
                if self.serial_conn.in_waiting > 0:
                    data = self.serial_conn.readline().decode('utf-8').strip()
                    if data:
                        self.receive_queue.put(data)
                        # 如果设置了回调函数，调用它
                        if self.data_callback:
                            try:
                                self.data_callback(data)
                            except Exception as e:
                                print(f"数据回调异常: {str(e)}")
                        
                time.sleep(0.01)  # 避免CPU占用过高
                
            except Exception as e:
                print(f"接收数据异常: {str(e)}")
                break
                
    def send_command(self, command):
        """发送指令"""
        if not self.connected or not self.serial_conn:
            return False
            
        for retry in range(self.max_retries):
            try:
                # 发送指令（添加换行符）
                self.serial_conn.write((command + '\n').encode('utf-8'))
                self.serial_conn.flush()
                return True
                
            except Exception as e:
                print(f"发送指令失败 (重试 {retry + 1}/{self.max_retries}): {str(e)}")
                if retry < self.max_retries - 1:
                    time.sleep(0.1)
                    
        return False
        
    def read_command(self):
        """读取接收到的指令"""
        if not self.receive_queue.empty():
            return self.receive_queue.get()
        return None
        
    def has_data(self):
        """检查是否有数据"""
        return not self.receive_queue.empty()
        
    def clear_buffer(self):
        """清空接收缓冲区"""
        while not self.receive_queue.empty():
            self.receive_queue.get()
            
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()
            
    def is_connected(self):
        """检查连接状态"""
        return self.connected and self.serial_conn and self.serial_conn.is_open
        
    def set_data_callback(self, callback):
        """设置数据回调函数
        
        Args:
            callback: 回调函数，接收一个参数（接收到的数据）
        """
        self.data_callback = callback