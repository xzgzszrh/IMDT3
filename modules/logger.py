#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志记录模块
实现系统日志记录功能
"""

import os
import threading
from datetime import datetime
from queue import Queue

class SystemLogger:
    """系统日志记录类"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.log_file = None
        self.log_queue = Queue()
        self.log_thread = None
        self.running = False
        
        # 创建日志目录
        self._create_log_dir()
        
        # 创建日志文件
        self._create_log_file()
        
        # 启动日志写入线程
        self.start_logging_thread()
        
    def _create_log_dir(self):
        """创建日志目录"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
    def _create_log_file(self):
        """创建日志文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"pharmacy_robot_{timestamp}.log")
        
        # 写入日志文件头
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"智慧药房机器人系统日志\n")
            f.write(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*50}\n")
            
    def start_logging_thread(self):
        """启动日志写入线程"""
        self.running = True
        self.log_thread = threading.Thread(target=self._logging_loop)
        self.log_thread.daemon = True
        self.log_thread.start()
        
    def start(self):
        """启动日志系统（兼容性方法）"""
        if not self.running:
            self.start_logging_thread()
        
    def _logging_loop(self):
        """日志写入循环"""
        while self.running:
            try:
                if not self.log_queue.empty():
                    log_entry = self.log_queue.get()
                    self._write_log_entry(log_entry)
                    
                # 避免CPU占用过高
                import time
                time.sleep(0.01)
                
            except Exception as e:
                print(f"日志写入异常: {str(e)}")
                
    def _write_log_entry(self, log_entry):
        """写入日志条目"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
                f.flush()
                
            # 同时输出到控制台
            print(log_entry)
            
        except Exception as e:
            print(f"写入日志文件失败: {str(e)}")
            
    def log(self, event_type, message):
        """记录日志
        
        Args:
            event_type: 事件类型（如"系统", "UART接收", "UART发送", "识别", "语音", "错误"等）
            message: 日志消息
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{event_type}] {message}"
        
        # 添加到日志队列
        self.log_queue.put(log_entry)
        
    def log_system(self, message):
        """记录系统日志"""
        self.log("系统", message)
        
    def log_uart_receive(self, command):
        """记录UART接收日志"""
        self.log("UART接收", command)
        
    def log_uart_send(self, response):
        """记录UART发送日志"""
        self.log("UART发送", response)
        
    def log_recognition(self, result):
        """记录识别结果日志"""
        self.log("识别", result)
        
    def log_voice(self, text):
        """记录语音播报日志"""
        self.log("语音", text)
        
    def log_error(self, error_message):
        """记录错误日志"""
        self.log("错误", error_message)
        
    def log_qr_recognition(self, position, content):
        """记录二维码识别日志
        
        Args:
            position: 位置（如"左上区域"）
            content: 二维码内容
        """
        message = f"{position}: {content}"
        self.log("识别", message)
        
    def log_ocr_recognition(self, window_num, text, status):
        """记录OCR识别日志
        
        Args:
            window_num: 窗口编号
            text: 识别文字
            status: 窗口状态
        """
        status_text = "空闲" if status else "无空闲"
        message = f"窗口{window_num}: {text} -> {status_text}"
        self.log("识别", message)
        
    def log_sample_collection(self, window, sample_type, count):
        """记录样本采集日志
        
        Args:
            window: 窗口标识（A/B/C）
            sample_type: 样本类型
            count: 样本数量
        """
        message = f"{window}窗口采集{sample_type}，数量: {count}"
        self.log("采样", message)
        
    def log_delivery(self, window_num, window_name, action):
        """记录配送日志
        
        Args:
            window_num: 窗口编号
            window_name: 窗口名称
            action: 动作（停留/通过）
        """
        message = f"{window_num}号{window_name}: {action}"
        self.log("配送", message)
        
    def log_task_start(self):
        """记录任务开始日志"""
        self.log_system("新任务开始")
        
    def log_task_end(self):
        """记录任务结束日志"""
        self.log_system("任务结束")
        
    def log_communication_error(self, error_type, details):
        """记录通信错误日志
        
        Args:
            error_type: 错误类型
            details: 错误详情
        """
        message = f"通信错误 - {error_type}: {details}"
        self.log_error(message)
        
    def log_recognition_error(self, recognition_type, details):
        """记录识别错误日志
        
        Args:
            recognition_type: 识别类型（二维码/OCR）
            details: 错误详情
        """
        message = f"{recognition_type}识别失败: {details}"
        self.log_error(message)
        
    def flush_logs(self):
        """强制刷新日志"""
        # 等待队列中的日志写入完成
        import time
        while not self.log_queue.empty():
            time.sleep(0.01)
            
    def stop(self):
        """停止日志记录"""
        # 记录系统停止日志
        self.log_system("系统停止")
        
        # 等待日志写入完成
        self.flush_logs()
        
        # 停止日志线程
        self.running = False
        if self.log_thread and self.log_thread.is_alive():
            self.log_thread.join(timeout=1)
            
        print(f"日志已保存到: {self.log_file}")
        
    def get_log_file_path(self):
        """获取日志文件路径"""
        return self.log_file
        
    def get_recent_logs(self, lines=50):
        """获取最近的日志
        
        Args:
            lines: 返回的行数
            
        Returns:
            list: 最近的日志行
        """
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
                
        except Exception as e:
            print(f"读取日志文件失败: {str(e)}")
            return []