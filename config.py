#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
系统配置文件
包含串口通信、图像识别、语音播报等模块的配置参数
"""

import os

class Config:
    """系统配置类"""
    
    # ==================== 串口通信配置 ====================
    # 串口设备路径
    SERIAL_PORT = '/dev/ttys019'  # macOS默认
    # SERIAL_PORT = '/dev/ttyUSB0'  # Linux默认
    # SERIAL_PORT = 'COM3'  # Windows默认
    
    # 串口波特率
    SERIAL_BAUDRATE = 115200
    
    # 串口超时时间（秒）
    SERIAL_TIMEOUT = 1
    
    # 串口重试次数
    SERIAL_MAX_RETRIES = 3
    
    # ==================== 图像识别配置 ====================
    # 摄像头设备ID
    CAMERA_DEVICE_ID = 0
    
    # 图像分辨率
    IMAGE_WIDTH = 640
    IMAGE_HEIGHT = 480
    
    # OCR语言设置
    OCR_LANGUAGE = 'chi_sim'  # 简体中文
    
    # 二维码识别超时时间（秒）
    QR_RECOGNITION_TIMEOUT = 5
    
    # ==================== 语音播报配置 ====================
    # TTS引擎类型 ('pyttsx3' 或 'system')
    TTS_ENGINE = 'pyttsx3'
    
    # 语音播报速度（仅pyttsx3）
    TTS_RATE = 150
    
    # 语音播报音量（仅pyttsx3，0.0-1.0）
    TTS_VOLUME = 0.8
    
    # 语音播报语言（仅pyttsx3）
    TTS_VOICE_ID = None  # None为默认语音
    
    # 系统命令语音播报（仅macOS）
    SYSTEM_SAY_COMMAND = 'say'
    
    # ==================== 日志配置 ====================
    # 日志目录
    LOG_DIR = 'logs'
    
    # 日志文件名格式
    LOG_FILENAME_FORMAT = 'pharmacy_robot_%Y%m%d_%H%M%S.log'
    
    # 日志级别
    LOG_LEVEL = 'INFO'
    
    # 日志保留天数
    LOG_RETENTION_DAYS = 30
    
    # ==================== 任务控制配置 ====================
    # 任务超时时间（秒）
    TASK_TIMEOUT = 30
    
    # 二维码识别重试次数
    QR_RETRY_COUNT = 3
    
    # OCR识别重试次数
    OCR_RETRY_COUNT = 3
    
    # ==================== 系统配置 ====================
    # 调试模式
    DEBUG_MODE = False
    
    # 模拟模式（不连接真实硬件）
    SIMULATION_MODE = False
    
    # 系统启动延迟（秒）
    STARTUP_DELAY = 2
    
    # ==================== 窗口映射配置 ====================
    # 体检区窗口映射
    MEDICAL_EXAM_WINDOWS = {
        'A': {'name': '血常规窗口', 'sample': '静脉血样本'},
        'B': {'name': '体液窗口', 'sample': '唾液样本'},
        'C': {'name': '免疫检测窗口', 'sample': '组织样本'}
    }
    
    # 化验区窗口映射
    LAB_WINDOWS = {
        1: {'name': '血常规窗口', 'sample': '静脉血样本'},
        2: {'name': '体液窗口', 'sample': '唾液样本'},
        3: {'name': '免疫检测窗口', 'sample': '组织样本'},
        4: {'name': '激素检验窗口', 'sample': '血浆样本'}
    }
    
    @classmethod
    def get_serial_config(cls):
        """获取串口配置"""
        return {
            'port': cls.SERIAL_PORT,
            'baudrate': cls.SERIAL_BAUDRATE,
            'timeout': cls.SERIAL_TIMEOUT,
            'max_retries': cls.SERIAL_MAX_RETRIES
        }
    
    @classmethod
    def get_camera_config(cls):
        """获取摄像头配置"""
        return {
            'device_id': cls.CAMERA_DEVICE_ID,
            'width': cls.IMAGE_WIDTH,
            'height': cls.IMAGE_HEIGHT
        }
    
    @classmethod
    def get_tts_config(cls):
        """获取TTS配置"""
        return {
            'engine': cls.TTS_ENGINE,
            'rate': cls.TTS_RATE,
            'volume': cls.TTS_VOLUME,
            'voice_id': cls.TTS_VOICE_ID,
            'system_command': cls.SYSTEM_SAY_COMMAND
        }
    
    @classmethod
    def get_log_config(cls):
        """获取日志配置"""
        return {
            'log_dir': cls.LOG_DIR,
            'filename_format': cls.LOG_FILENAME_FORMAT,
            'level': cls.LOG_LEVEL,
            'retention_days': cls.LOG_RETENTION_DAYS
        }
    
    @classmethod
    def load_from_env(cls):
        """从环境变量加载配置（仅覆盖已设置的环境变量）"""
        env_loaded = False
        
        # 串口配置
        if 'SERIAL_PORT' in os.environ:
            cls.SERIAL_PORT = os.getenv('SERIAL_PORT')
            env_loaded = True
        if 'SERIAL_BAUDRATE' in os.environ:
            cls.SERIAL_BAUDRATE = int(os.getenv('SERIAL_BAUDRATE'))
            env_loaded = True
        if 'SERIAL_TIMEOUT' in os.environ:
            cls.SERIAL_TIMEOUT = float(os.getenv('SERIAL_TIMEOUT'))
            env_loaded = True
        
        # 摄像头配置
        if 'CAMERA_DEVICE_ID' in os.environ:
            cls.CAMERA_DEVICE_ID = int(os.getenv('CAMERA_DEVICE_ID'))
            env_loaded = True
        if 'IMAGE_WIDTH' in os.environ:
            cls.IMAGE_WIDTH = int(os.getenv('IMAGE_WIDTH'))
            env_loaded = True
        if 'IMAGE_HEIGHT' in os.environ:
            cls.IMAGE_HEIGHT = int(os.getenv('IMAGE_HEIGHT'))
            env_loaded = True
        
        # TTS配置
        if 'TTS_ENGINE' in os.environ:
            cls.TTS_ENGINE = os.getenv('TTS_ENGINE')
            env_loaded = True
        if 'TTS_RATE' in os.environ:
            cls.TTS_RATE = int(os.getenv('TTS_RATE'))
            env_loaded = True
        if 'TTS_VOLUME' in os.environ:
            cls.TTS_VOLUME = float(os.getenv('TTS_VOLUME'))
            env_loaded = True
        
        # 系统配置
        if 'DEBUG_MODE' in os.environ:
            cls.DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
            env_loaded = True
        if 'SIMULATION_MODE' in os.environ:
            cls.SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'False').lower() == 'true'
            env_loaded = True
        
        if env_loaded:
            print("已从环境变量加载部分配置")
        else:
            print("未检测到环境变量配置")
    
    @classmethod
    def print_config(cls):
        """打印当前配置"""
        print("\n=== 系统配置 ===")
        print(f"串口设备: {cls.SERIAL_PORT}")
        print(f"串口波特率: {cls.SERIAL_BAUDRATE}")
        print(f"摄像头设备ID: {cls.CAMERA_DEVICE_ID}")
        print(f"图像分辨率: {cls.IMAGE_WIDTH}x{cls.IMAGE_HEIGHT}")
        print(f"TTS引擎: {cls.TTS_ENGINE}")
        print(f"日志目录: {cls.LOG_DIR}")
        print(f"调试模式: {cls.DEBUG_MODE}")
        print(f"模拟模式: {cls.SIMULATION_MODE}")
        print("================\n")

    @classmethod
    def load_local_config(cls):
        """加载本地配置文件（如果存在）"""
        try:
            import config_local
            
            # 从本地配置文件加载配置
            for attr_name in dir(config_local):
                if not attr_name.startswith('_') and hasattr(cls, attr_name):
                    setattr(cls, attr_name, getattr(config_local, attr_name))
            
            print("已加载本地配置文件: config_local.py")
            return True
            
        except ImportError:
            print("未找到本地配置文件 config_local.py，使用默认配置")
            return False
        except Exception as e:
            print(f"加载本地配置文件失败: {str(e)}")
            return False

# 在模块加载时自动加载配置
# 1. 首先尝试加载本地配置文件
Config.load_local_config()

# 2. 然后从环境变量加载配置（会覆盖本地配置）
Config.load_from_env()