#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
任务控制器模块
实现系统任务流程控制和指令处理
"""

import time
import threading
from datetime import datetime

class TaskController:
    """任务控制器类"""
    
    def __init__(self, logger, serial_comm, image_recognition, voice_player):
        self.logger = logger
        self.serial_comm = serial_comm
        self.image_recognition = image_recognition
        self.voice_player = voice_player
        
        # 任务状态
        self.running = False
        self.current_task_data = {}
        
        # 二维码识别结果存储
        self.qr_results = {}
        
        # 窗口状态存储
        self.window_status = {}
        
        # 指令处理映射
        self.command_handlers = {
            'start': self._handle_start,
            'check board 1': self._handle_check_board1,
            'check A': self._handle_check_window_A,
            'check B': self._handle_check_window_B,
            'check C': self._handle_check_window_C,
            'check board 2': self._handle_check_board2,
            'check 1': self._handle_check_lab_1,
            'check 2': self._handle_check_lab_2,
            'check 3': self._handle_check_lab_3,
            'check 4': self._handle_check_lab_4,
            'over': self._handle_over
        }
        
    def start(self):
        """启动任务控制器"""
        self.running = True
        self.logger.log_system("任务控制器启动")
        
    def stop(self):
        """停止任务控制器"""
        self.running = False
        self.logger.log_system("任务控制器停止")
        
    def handle_command(self, command):
        """处理接收到的指令
        
        Args:
            command: 接收到的指令字符串
        """
        if not self.running:
            return
            
        # 记录接收到的指令
        self.logger.log_uart_receive(command)
        
        # 查找对应的处理函数
        handler = self.command_handlers.get(command.strip())
        
        if handler:
            try:
                response = handler()
                if response:
                    self._send_response(response)
            except Exception as e:
                error_msg = f"处理指令'{command}'时发生异常: {str(e)}"
                self.logger.log_error(error_msg)
                self._send_response("error")
        else:
            self.logger.log_error(f"未知指令: {command}")
            self._send_response("error")
            
    def _send_response(self, response):
        """发送响应
        
        Args:
            response: 响应内容
        """
        if self.serial_comm.send_command(response):
            self.logger.log_uart_send(response)
        else:
            self.logger.log_error(f"发送响应失败: {response}")
            
    def _handle_start(self):
        """处理start指令"""
        self.logger.log_task_start()
        
        # 清除之前的任务数据
        self.current_task_data.clear()
        self.qr_results.clear()
        self.window_status.clear()
        
        # 语音播报
        self.voice_player.speak_system_start()
        
        return "ok"
        
    def _handle_check_board1(self):
        """处理check board 1指令"""
        try:
            # 进行二维码识别
            results = self.image_recognition.recognize_qr_codes_board1()
            
            if 'error' in results:
                self.logger.log_recognition_error("二维码", results['error'])
                return "error"
                
            # 存储识别结果
            self.qr_results = results
            
            # 记录识别结果
            position_names = {
                'top_left': '左上区域',
                'top_right': '右上区域', 
                'bottom_left': '左下区域',
                'bottom_right': '右下区域'
            }
            
            for position, content in results.items():
                chinese_position = position_names.get(position, position)
                self.logger.log_qr_recognition(chinese_position, content)
                
            # 构建响应数据
            response_data = self._format_qr_results(results)
            return response_data
            
        except Exception as e:
            self.logger.log_recognition_error("二维码", str(e))
            return "error"
            
    def _format_qr_results(self, results):
        """格式化二维码识别结果
        
        Args:
            results: 识别结果字典
            
        Returns:
            str: 格式化的结果字符串
        """
        if not results:
            return "no_qr_found"
            
        # 简单格式：position1:content1,position2:content2
        formatted_parts = []
        for position, content in results.items():
            formatted_parts.append(f"{position}:{content}")
            
        return ",".join(formatted_parts)
        
    def _handle_check_window_A(self):
        """处理check A指令"""
        return self._handle_check_window('A')
        
    def _handle_check_window_B(self):
        """处理check B指令"""
        return self._handle_check_window('B')
        
    def _handle_check_window_C(self):
        """处理check C指令"""
        return self._handle_check_window('C')
        
    def _handle_check_window(self, window):
        """处理体检区窗口检查
        
        Args:
            window: 窗口标识（A/B/C）
        """
        try:
            # 根据二维码识别结果确定样本类型
            sample_types = self._get_sample_types_for_window(window)
            
            if sample_types:
                # 语音播报收到样本
                self.voice_player.speak_sample_received(sample_types)
                
                # 记录样本采集
                for sample_type in sample_types:
                    self.logger.log_sample_collection(window, sample_type, 1)
                    
                # 构建响应
                response = f"collected:{','.join(sample_types)}"
                return response
            else:
                self.logger.log("采样", f"{window}窗口无样本")
                return "no_sample"
                
        except Exception as e:
            self.logger.log_error(f"处理{window}窗口检查异常: {str(e)}")
            return "error"
            
    def _get_sample_types_for_window(self, window):
        """获取指定窗口的样本类型
        
        Args:
            window: 窗口标识（A/B/C）
            
        Returns:
            list: 样本类型列表
        """
        sample_types = []
        
        # 遍历二维码识别结果
        for position, content in self.qr_results.items():
            # 解析二维码内容，检查是否包含当前窗口
            windows = self.image_recognition.parse_qr_content(content)
            if window in windows:
                # 获取样本信息
                sample_info = self.image_recognition.get_sample_info(position, content)
                if sample_info:
                    sample_types.append(sample_info['sample_type'])
                    
        return sample_types
        
    def _handle_check_board2(self):
        """处理check board 2指令"""
        try:
            # 进行OCR识别
            results = self.image_recognition.recognize_ocr_board2()
            
            if 'error' in results:
                self.logger.log_recognition_error("OCR", results['error'])
                return "error"
                
            # 存储窗口状态
            self.window_status = results['window_status']
            
            # 记录OCR识别结果
            for window_num, status_info in results['window_status'].items():
                self.logger.log_ocr_recognition(
                    window_num, 
                    status_info['text'], 
                    status_info['available']
                )
                
            # 检查需要前往的窗口是否可用
            needed_windows = self._get_needed_windows()
            unavailable_windows = []
            
            for window_num in needed_windows:
                if window_num in self.window_status:
                    if not self.window_status[window_num]['available']:
                        window_name = self.image_recognition.window_names.get(window_num, f"{window_num}号窗口")
                        unavailable_windows.append(window_name)
                        
            if unavailable_windows:
                # 有窗口不可用，语音播报并返回wait
                for window_name in unavailable_windows:
                    self.voice_player.speak_window_busy(window_name)
                return "wait"
            else:
                # 所有需要的窗口都可用
                return "ok"
                
        except Exception as e:
            self.logger.log_recognition_error("OCR", str(e))
            return "error"
            
    def _get_needed_windows(self):
        """获取需要前往的窗口列表
        
        Returns:
            list: 窗口编号列表
        """
        needed_windows = set()
        
        # 根据二维码识别结果确定需要的窗口
        for position, content in self.qr_results.items():
            sample_info = self.image_recognition.get_sample_info(position, content)
            if sample_info:
                needed_windows.add(sample_info['window_number'])
                
        return list(needed_windows)
        
    def _handle_check_lab_1(self):
        """处理check 1指令"""
        return self._handle_check_lab_window(1)
        
    def _handle_check_lab_2(self):
        """处理check 2指令"""
        return self._handle_check_lab_window(2)
        
    def _handle_check_lab_3(self):
        """处理check 3指令"""
        return self._handle_check_lab_window(3)
        
    def _handle_check_lab_4(self):
        """处理check 4指令"""
        return self._handle_check_lab_window(4)
        
    def _handle_check_lab_window(self, window_num):
        """处理化验区窗口检查
        
        Args:
            window_num: 窗口编号（1-4）
        """
        try:
            # 检查当前窗口是否需要停留
            should_stop, sample_count = self._should_stop_at_window(window_num)
            
            window_name = self.image_recognition.window_names.get(window_num, f"{window_num}号窗口")
            
            if should_stop:
                # 需要停留
                self.voice_player.speak_delivery_arrival(window_name, sample_count)
                self.logger.log_delivery(window_num, window_name, f"停留，样本数: {sample_count}")
                return "wait"
            else:
                # 不需要停留
                self.logger.log_delivery(window_num, window_name, "通过")
                return "ok"
                
        except Exception as e:
            self.logger.log_error(f"处理{window_num}号窗口检查异常: {str(e)}")
            return "error"
            
    def _should_stop_at_window(self, window_num):
        """判断是否应该在指定窗口停留
        
        Args:
            window_num: 窗口编号
            
        Returns:
            tuple: (是否停留, 样本数量)
        """
        sample_count = 0
        
        # 检查二维码识别结果中是否有对应此窗口的样本
        for position, content in self.qr_results.items():
            sample_info = self.image_recognition.get_sample_info(position, content)
            if sample_info and sample_info['window_number'] == window_num:
                sample_count += sample_info['sample_count']
                
        return sample_count > 0, sample_count
        
    def _handle_over(self):
        """处理over指令"""
        # 语音播报任务结束
        self.voice_player.speak_system_end()
        
        # 清除任务数据
        self.current_task_data.clear()
        self.qr_results.clear()
        self.window_status.clear()
        
        # 记录任务结束
        self.logger.log_task_end()
        
        return "ok"
        
    def get_current_status(self):
        """获取当前状态
        
        Returns:
            dict: 当前状态信息
        """
        return {
            'running': self.running,
            'qr_results': self.qr_results,
            'window_status': self.window_status,
            'task_data': self.current_task_data
        }
        
    def reset_task_data(self):
        """重置任务数据"""
        self.current_task_data.clear()
        self.qr_results.clear()
        self.window_status.clear()
        self.logger.log_system("任务数据已重置")