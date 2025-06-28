#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图像识别模块
实现二维码识别和OCR文字识别功能
"""

import cv2
import numpy as np
from pyzbar import pyzbar
import pytesseract
from PIL import Image
import re

class ImageRecognition:
    """图像识别类"""
    
    def __init__(self, logger=None):
        self.logger = logger
        
        # 二维码位置映射
        self.qr_position_mapping = {
            'top_left': {'window': 1, 'name': '血常规窗口', 'sample': '静脉血样本'},
            'top_right': {'window': 2, 'name': '体液窗口', 'sample': '唾液样本'},
            'bottom_left': {'window': 3, 'name': '免疫检测窗口', 'sample': '组织样本'},
            'bottom_right': {'window': 4, 'name': '激素检验窗口', 'sample': '血浆样本'}
        }
        
        # 位置映射（简化版本）
        self.position_mapping = {
            'top_left': 1,
            'top_right': 2,
            'bottom_left': 3,
            'bottom_right': 4
        }
        
        # 窗口名称映射
        self.window_names = {
            1: '血常规窗口',
            2: '体液窗口', 
            3: '免疫检测窗口',
            4: '激素检验窗口'
        }
        
        # 样本类型映射
        self.sample_types = {
            1: '静脉血样本',
            2: '唾液样本',
            3: '组织样本', 
            4: '血浆样本'
        }
        
    def start(self):
        """启动图像识别系统"""
        if self.logger:
            self.logger.log_recognition("图像识别系统已启动")
        print("图像识别系统已启动")
        
    def recognize_qr_codes_board1(self, image_path=None, image_data=None):
        """识别板1的二维码
        
        Args:
            image_path: 图像文件路径
            image_data: 图像数据（numpy数组）
            
        Returns:
            dict: 识别结果 {'position': 'content', ...}
        """
        try:
            # 加载图像
            if image_path:
                image = cv2.imread(image_path)
            elif image_data is not None:
                image = image_data
            else:
                # 模拟摄像头捕获
                image = self._capture_camera_image()
                
            if image is None:
                return {'error': '无法获取图像'}
                
            # 将图像分为四个区域
            height, width = image.shape[:2]
            regions = {
                'top_left': image[0:height//2, 0:width//2],
                'top_right': image[0:height//2, width//2:width],
                'bottom_left': image[height//2:height, 0:width//2],
                'bottom_right': image[height//2:height, width//2:width]
            }
            
            results = {}
            
            # 识别每个区域的二维码
            for position, region in regions.items():
                qr_content = self._decode_qr_code(region)
                if qr_content:
                    results[position] = qr_content
                    
            return results
            
        except Exception as e:
            return {'error': f'二维码识别失败: {str(e)}'}
            
    def _decode_qr_code(self, image_region):
        """解码二维码"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image_region, cv2.COLOR_BGR2GRAY)
            
            # 使用pyzbar解码二维码
            decoded_objects = pyzbar.decode(gray)
            
            if decoded_objects:
                # 返回第一个二维码的内容
                return decoded_objects[0].data.decode('utf-8')
            else:
                return None
                
        except Exception as e:
            print(f"二维码解码异常: {str(e)}")
            return None
            
    def recognize_ocr_board2(self, image_path=None, image_data=None):
        """识别板2的OCR内容
        
        Args:
            image_path: 图像文件路径
            image_data: 图像数据（numpy数组）
            
        Returns:
            dict: 识别结果 {'window_status': {...}, 'available': bool}
        """
        try:
            # 加载图像
            if image_path:
                image = cv2.imread(image_path)
            elif image_data is not None:
                image = image_data
            else:
                # 模拟摄像头捕获
                image = self._capture_camera_image()
                
            if image is None:
                return {'error': '无法获取图像'}
                
            # 将图像分为四个区域
            height, width = image.shape[:2]
            regions = [
                image[0:height//2, 0:width//2],      # 区域1
                image[0:height//2, width//2:width],   # 区域2
                image[height//2:height, 0:width//2],  # 区域3
                image[height//2:height, width//2:width] # 区域4
            ]
            
            window_status = {}
            
            # 识别每个区域的OCR内容
            for i, region in enumerate(regions, 1):
                ocr_text = self._extract_text_ocr(region)
                status = self._parse_window_status(ocr_text)
                window_status[i] = {
                    'text': ocr_text,
                    'available': status
                }
                
            return {
                'window_status': window_status,
                'available': all(status['available'] for status in window_status.values())
            }
            
        except Exception as e:
            return {'error': f'OCR识别失败: {str(e)}'}
            
    def _extract_text_ocr(self, image_region):
        """提取图像区域的文字"""
        try:
            # 转换为PIL图像
            pil_image = Image.fromarray(cv2.cvtColor(image_region, cv2.COLOR_BGR2RGB))
            
            # 使用tesseract进行OCR识别
            text = pytesseract.image_to_string(pil_image, lang='chi_sim')
            
            return text.strip()
            
        except Exception as e:
            print(f"OCR文字提取异常: {str(e)}")
            return ""
            
    def _parse_window_status(self, ocr_text):
        """解析窗口状态"""
        # 检查是否包含"无空闲"关键词
        if '无空闲' in ocr_text or '忙碌' in ocr_text or '占用' in ocr_text:
            return False
        elif '空闲' in ocr_text or '可用' in ocr_text:
            return True
        else:
            # 默认返回空闲状态
            return True
            
    def _capture_camera_image(self):
        """捕获摄像头图像（模拟）"""
        try:
            # 尝试打开摄像头
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret:
                    return frame
            
            # 如果摄像头不可用，返回模拟图像
            return self._create_mock_image()
            
        except Exception as e:
            print(f"摄像头捕获异常: {str(e)}")
            return self._create_mock_image()
            
    def _create_mock_image(self):
        """创建模拟图像用于测试"""
        # 创建640x480的白色图像
        image = np.ones((480, 640, 3), dtype=np.uint8) * 255
        
        # 添加一些文字用于测试
        cv2.putText(image, 'Mock Image for Testing', (50, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                   
        return image
        
    def parse_qr_content(self, qr_content):
        """解析二维码内容
        
        Args:
            qr_content: 二维码内容（如"AB", "BC", "ABC"等）
            
        Returns:
            list: 包含样本的窗口列表（如['A', 'B']）
        """
        if not qr_content:
            return []
            
        # 提取字母
        windows = []
        for char in qr_content.upper():
            if char in ['A', 'B', 'C']:
                windows.append(char)
                
        return windows
        
    def get_sample_info(self, position, qr_content):
        """获取样本信息
        
        Args:
            position: 二维码位置（如'top_left'）
            qr_content: 二维码内容
            
        Returns:
            dict: 样本信息
        """
        if position not in self.qr_position_mapping:
            return None
            
        mapping = self.qr_position_mapping[position]
        windows = self.parse_qr_content(qr_content)
        
        return {
            'window_number': mapping['window'],
            'window_name': mapping['name'],
            'sample_type': mapping['sample'],
            'target_windows': windows,
            'sample_count': len(windows)
        }