#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
语音播报模块
实现TTS语音合成和播放功能
"""

import os
import threading
import time
from queue import Queue

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("警告: pyttsx3未安装，将使用系统say命令")

class VoicePlayer:
    """语音播报类"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.tts_engine = None
        self.voice_queue = Queue()
        self.voice_thread = None
        self.running = False
        
        # 初始化TTS引擎
        self._init_tts_engine()
        
        # 启动语音播报线程
        self.start_voice_thread()
        
    def _init_tts_engine(self):
        """初始化TTS引擎"""
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                
                # 设置语音参数
                self.tts_engine.setProperty('rate', 150)  # 语速
                self.tts_engine.setProperty('volume', 0.8)  # 音量
                
                # 尝试设置中文语音
                voices = self.tts_engine.getProperty('voices')
                for voice in voices:
                    if 'chinese' in voice.name.lower() or 'zh' in voice.id.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                        
                print("TTS引擎初始化成功")
                
            except Exception as e:
                print(f"TTS引擎初始化失败: {str(e)}")
                self.tts_engine = None
        else:
            print("使用系统say命令进行语音播报")
            
    def start_voice_thread(self):
        """启动语音播报线程"""
        self.running = True
        self.voice_thread = threading.Thread(target=self._voice_loop)
        self.voice_thread.daemon = True
        self.voice_thread.start()
        
    def start(self):
        """启动语音播报系统（兼容性方法）"""
        if not self.running:
            self.start_voice_thread()
        
    def _voice_loop(self):
        """语音播报循环"""
        while self.running:
            try:
                if not self.voice_queue.empty():
                    text = self.voice_queue.get()
                    self._speak_text(text)
                    
                time.sleep(0.1)
                
            except Exception as e:
                print(f"语音播报异常: {str(e)}")
                
    def _speak_text(self, text):
        """播报文字"""
        try:
            if self.tts_engine:
                # 使用pyttsx3播报
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            else:
                # 使用系统say命令（macOS）
                os.system(f'say "{text}"')
                
            print(f"语音播报: {text}")
            
            # 记录语音播报日志
            if self.logger:
                self.logger.log_voice(text)
            
        except Exception as e:
            print(f"语音播报失败: {str(e)}")
            
    def speak(self, text, priority=False):
        """添加语音播报任务
        
        Args:
            text: 要播报的文字
            priority: 是否优先播报
        """
        if priority:
            # 清空队列，优先播报
            while not self.voice_queue.empty():
                self.voice_queue.get()
                
        self.voice_queue.put(text)
        
    def speak_system_start(self):
        """播报系统启动"""
        self.speak("系统开始运行", priority=True)
        
    def speak_system_end(self):
        """播报系统结束"""
        self.speak("本轮运行结束", priority=True)
        
    def speak_sample_received(self, sample_types):
        """播报收到样本
        
        Args:
            sample_types: 样本类型列表
        """
        if not sample_types:
            return
            
        if len(sample_types) == 1:
            text = f"收到{sample_types[0]}样本"
        else:
            text = "收到" + "和".join(sample_types) + "样本"
            
        self.speak(text)
        
    def speak_window_busy(self, window_name):
        """播报窗口无空闲
        
        Args:
            window_name: 窗口名称
        """
        text = f"{window_name}无空闲正在等待"
        self.speak(text)
        
    def speak_delivery_arrival(self, window_name, sample_count):
        """播报到达配送窗口
        
        Args:
            window_name: 窗口名称
            sample_count: 样本数量
        """
        text = f"到达{window_name}，样本数为{sample_count}"
        self.speak(text)
        
    def speak_custom(self, text):
        """播报自定义文字
        
        Args:
            text: 自定义文字
        """
        self.speak(text)
        
    def clear_queue(self):
        """清空播报队列"""
        while not self.voice_queue.empty():
            self.voice_queue.get()
            
    def stop(self):
        """停止语音播报"""
        self.running = False
        self.clear_queue()
        
        if self.voice_thread and self.voice_thread.is_alive():
            self.voice_thread.join(timeout=1)
            
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
                
        print("语音播报已停止")
        
    def is_speaking(self):
        """检查是否正在播报"""
        return not self.voice_queue.empty()
        
    def wait_for_completion(self, timeout=10):
        """等待播报完成
        
        Args:
            timeout: 超时时间（秒）
        """
        start_time = time.time()
        while self.is_speaking() and (time.time() - start_time) < timeout:
            time.sleep(0.1)