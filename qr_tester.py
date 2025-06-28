#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QR码识别测试程序
用于测试和调试QR码识别功能
"""

import cv2
import numpy as np
from pyzbar import pyzbar
import argparse
import sys
import os
from datetime import datetime
import json
from typing import Dict, List, Optional, Tuple

# 添加模块路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules.image_recognition import ImageRecognition
from config import Config

class QRTester:
    """QR码测试器"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.image_recognition = ImageRecognition()
        self.test_results = []
        
    def test_camera_capture(self) -> bool:
        """测试摄像头捕获功能"""
        print("\n=== 测试摄像头捕获 ===")
        
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("❌ 摄像头无法打开")
                return False
            
            print("✅ 摄像头已打开")
            
            # 读取一帧
            ret, frame = cap.read()
            if not ret:
                print("❌ 无法读取摄像头数据")
                cap.release()
                return False
            
            print(f"✅ 成功捕获图像，尺寸: {frame.shape}")
            
            # 保存测试图像
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"camera_test_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"✅ 测试图像已保存: {filename}")
            
            cap.release()
            return True
            
        except Exception as e:
            print(f"❌ 摄像头测试失败: {e}")
            return False
    
    def test_qr_decode_basic(self) -> bool:
        """测试基本QR码解码功能"""
        print("\n=== 测试基本QR码解码 ===")
        
        try:
            # 创建测试QR码图像
            test_image = self._create_test_qr_image("TEST_QR_123")
            
            # 使用pyzbar解码
            gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
            decoded_objects = pyzbar.decode(gray)
            
            if decoded_objects:
                content = decoded_objects[0].data.decode('utf-8')
                print(f"✅ QR码解码成功: {content}")
                return True
            else:
                print("❌ QR码解码失败")
                return False
                
        except Exception as e:
            print(f"❌ QR码解码测试失败: {e}")
            return False
    
    def test_image_recognition_module(self) -> bool:
        """测试图像识别模块"""
        print("\n=== 测试图像识别模块 ===")
        
        try:
            # 创建包含多个QR码的测试图像
            test_image = self._create_multi_qr_test_image()
            
            # 使用图像识别模块识别
            results = self.image_recognition.recognize_qr_codes_board1(image_data=test_image)
            
            if 'error' in results:
                print(f"❌ 图像识别模块测试失败: {results['error']}")
                return False
            
            print(f"✅ 图像识别模块测试成功，识别到 {len(results)} 个QR码:")
            for position, content in results.items():
                print(f"  - {position}: {content}")
            
            return True
            
        except Exception as e:
            print(f"❌ 图像识别模块测试失败: {e}")
            return False
    
    def test_real_camera_qr(self, duration=10) -> Dict:
        """测试实时摄像头QR码识别"""
        print(f"\n=== 测试实时摄像头QR码识别 (持续{duration}秒) ===")
        
        results = {'detected_qrs': [], 'total_frames': 0, 'qr_frames': 0}
        
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("❌ 摄像头无法打开")
                return results
            
            print("📷 开始实时检测，请将QR码放在摄像头前...")
            print("按 'q' 键提前退出")
            
            start_time = datetime.now()
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                results['total_frames'] += 1
                
                # QR码检测
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                decoded_objects = pyzbar.decode(gray)
                
                if decoded_objects:
                    results['qr_frames'] += 1
                    for obj in decoded_objects:
                        content = obj.data.decode('utf-8')
                        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                        
                        # 避免重复记录相同内容
                        if not results['detected_qrs'] or results['detected_qrs'][-1]['content'] != content:
                            results['detected_qrs'].append({
                                'content': content,
                                'timestamp': timestamp,
                                'rect': obj.rect._asdict()
                            })
                            print(f"[{timestamp}] 检测到QR码: {content}")
                        
                        # 在图像上绘制检测框
                        points = obj.polygon
                        if len(points) == 4:
                            pts = np.array([[p.x, p.y] for p in points], dtype=np.int32)
                            cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
                            cv2.putText(frame, content, (obj.rect.left, obj.rect.top - 10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # 显示图像
                cv2.imshow('QR Code Detection Test', frame)
                
                # 检查退出条件
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                # 检查时间
                if (datetime.now() - start_time).seconds >= duration:
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            # 统计结果
            detection_rate = (results['qr_frames'] / results['total_frames'] * 100) if results['total_frames'] > 0 else 0
            print(f"\n📊 检测统计:")
            print(f"  总帧数: {results['total_frames']}")
            print(f"  检测到QR码的帧数: {results['qr_frames']}")
            print(f"  检测率: {detection_rate:.1f}%")
            print(f"  唯一QR码数量: {len(results['detected_qrs'])}")
            
            return results
            
        except Exception as e:
            print(f"❌ 实时QR码检测失败: {e}")
            return results
    
    def test_image_file_qr(self, image_path: str) -> Dict:
        """测试图像文件QR码识别"""
        print(f"\n=== 测试图像文件QR码识别: {image_path} ===")
        
        if not os.path.exists(image_path):
            print(f"❌ 图像文件不存在: {image_path}")
            return {'error': '文件不存在'}
        
        try:
            # 使用图像识别模块
            results = self.image_recognition.recognize_qr_codes_board1(image_path=image_path)
            
            if 'error' in results:
                print(f"❌ 图像文件QR码识别失败: {results['error']}")
                return results
            
            print(f"✅ 图像文件QR码识别成功，识别到 {len(results)} 个QR码:")
            for position, content in results.items():
                print(f"  - {position}: {content}")
                
                # 解析QR码内容
                sample_info = self.image_recognition.get_sample_info(position, content)
                if sample_info:
                    print(f"    窗口: {sample_info['window_number']} ({sample_info['window_name']})")
                    print(f"    样本: {sample_info['sample_type']}")
                    print(f"    目标窗口: {sample_info['target_windows']}")
            
            return results
            
        except Exception as e:
            print(f"❌ 图像文件QR码识别失败: {e}")
            return {'error': str(e)}
    
    def _create_test_qr_image(self, content: str) -> np.ndarray:
        """创建测试QR码图像"""
        try:
            import qrcode
            
            # 生成QR码
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(content)
            qr.make(fit=True)
            
            # 转换为PIL图像
            pil_img = qr.make_image(fill_color="black", back_color="white")
            
            # 转换为OpenCV格式
            opencv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            
            return opencv_img
            
        except ImportError:
            print("⚠️ qrcode库未安装，使用模拟图像")
            # 创建简单的模拟图像
            img = np.ones((200, 200, 3), dtype=np.uint8) * 255
            cv2.putText(img, content, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            return img
    
    def _create_multi_qr_test_image(self) -> np.ndarray:
        """创建包含多个QR码的测试图像"""
        # 创建640x480的白色图像
        image = np.ones((480, 640, 3), dtype=np.uint8) * 255
        
        # 在四个角落添加QR码内容标识
        positions = [
            (50, 50, "AB"),      # top_left
            (350, 50, "BC"),     # top_right  
            (50, 300, "AC"),     # bottom_left
            (350, 300, "ABC")    # bottom_right
        ]
        
        for x, y, content in positions:
            # 绘制矩形框模拟QR码
            cv2.rectangle(image, (x, y), (x+100, y+100), (0, 0, 0), 2)
            cv2.putText(image, content, (x+20, y+60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        return image
    
    def run_comprehensive_test(self) -> Dict:
        """运行综合测试"""
        print("\n🔍 开始QR码识别综合测试...")
        
        test_results = {
            'camera_capture': False,
            'qr_decode_basic': False,
            'image_recognition_module': False,
            'real_camera_qr': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # 1. 测试摄像头捕获
        test_results['camera_capture'] = self.test_camera_capture()
        
        # 2. 测试基本QR码解码
        test_results['qr_decode_basic'] = self.test_qr_decode_basic()
        
        # 3. 测试图像识别模块
        test_results['image_recognition_module'] = self.test_image_recognition_module()
        
        # 4. 测试实时摄像头QR码识别（可选）
        if input("\n是否进行实时摄像头测试? (y/n): ").strip().lower() == 'y':
            duration = int(input("测试持续时间(秒，默认10): ") or "10")
            test_results['real_camera_qr'] = self.test_real_camera_qr(duration)
        
        # 总结
        print("\n📋 测试总结:")
        passed = sum(1 for k, v in test_results.items() 
                    if k != 'timestamp' and k != 'real_camera_qr' and v)
        total = 3  # 基础测试数量
        
        print(f"基础测试通过: {passed}/{total}")
        
        if test_results['real_camera_qr']:
            qr_count = len(test_results['real_camera_qr'].get('detected_qrs', []))
            print(f"实时测试检测到QR码: {qr_count}个")
        
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"qr_test_results_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 测试结果已保存: {filename}")
        
        return test_results
    
    def interactive_mode(self):
        """交互模式"""
        print("\n🔍 QR码识别测试器 - 交互模式")
        print("选择测试项目:")
        print("1. 摄像头捕获测试")
        print("2. 基本QR码解码测试")
        print("3. 图像识别模块测试")
        print("4. 实时摄像头QR码识别")
        print("5. 图像文件QR码识别")
        print("6. 综合测试")
        print("q. 退出")
        
        while True:
            choice = input("\n请选择 (1-6, q): ").strip()
            
            if choice == 'q':
                break
            elif choice == '1':
                self.test_camera_capture()
            elif choice == '2':
                self.test_qr_decode_basic()
            elif choice == '3':
                self.test_image_recognition_module()
            elif choice == '4':
                duration = int(input("测试持续时间(秒，默认10): ") or "10")
                self.test_real_camera_qr(duration)
            elif choice == '5':
                image_path = input("请输入图像文件路径: ").strip()
                self.test_image_file_qr(image_path)
            elif choice == '6':
                self.run_comprehensive_test()
            else:
                print("无效选择，请重试")

def main():
    parser = argparse.ArgumentParser(description='QR码识别测试程序')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--test', choices=['camera', 'decode', 'module', 'realtime', 'comprehensive'], 
                       help='运行指定测试')
    parser.add_argument('--image', help='测试指定图像文件')
    parser.add_argument('--duration', type=int, default=10, help='实时测试持续时间(秒)')
    
    args = parser.parse_args()
    
    tester = QRTester(debug=args.debug)
    
    if args.image:
        tester.test_image_file_qr(args.image)
    elif args.test:
        if args.test == 'camera':
            tester.test_camera_capture()
        elif args.test == 'decode':
            tester.test_qr_decode_basic()
        elif args.test == 'module':
            tester.test_image_recognition_module()
        elif args.test == 'realtime':
            tester.test_real_camera_qr(args.duration)
        elif args.test == 'comprehensive':
            tester.run_comprehensive_test()
    else:
        tester.interactive_mode()

if __name__ == '__main__':
    main()