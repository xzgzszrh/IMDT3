#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置文件示例
复制此文件为 config_local.py 并根据需要修改配置
"""

# ==================== 串口通信配置 ====================
# 串口设备路径（根据操作系统选择）
SERIAL_PORT = '/dev/tty.usbserial-0001'  # macOS
# SERIAL_PORT = '/dev/ttyUSB0'  # Linux
# SERIAL_PORT = 'COM3'  # Windows

# 串口波特率
SERIAL_BAUDRATE = 115200

# 串口超时时间（秒）
SERIAL_TIMEOUT = 1

# ==================== 图像识别配置 ====================
# 摄像头设备ID
CAMERA_DEVICE_ID = 0

# 图像分辨率
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

# ==================== 语音播报配置 ====================
# TTS引擎类型 ('pyttsx3' 或 'system')
TTS_ENGINE = 'pyttsx3'

# 语音播报速度（仅pyttsx3）
TTS_RATE = 150

# 语音播报音量（仅pyttsx3，0.0-1.0）
TTS_VOLUME = 0.8

# ==================== 系统配置 ====================
# 调试模式
DEBUG_MODE = False

# 模拟模式（不连接真实硬件）
SIMULATION_MODE = False

# ==================== 使用说明 ====================
"""
1. 复制此文件为 config_local.py
2. 根据你的硬件配置修改相应参数
3. 运行程序时会自动加载 config_local.py 中的配置
4. 如果 config_local.py 不存在，将使用 config.py 中的默认配置

常用命令行参数：
  --port /dev/ttyUSB0    指定串口设备
  --debug               启用调试模式
  --simulation          启用模拟模式
  --config              显示当前配置
  --interactive         启动交互模式

环境变量配置（可选）：
  export SERIAL_PORT=/dev/ttyUSB0
  export SERIAL_BAUDRATE=115200
  export DEBUG_MODE=true
  export SIMULATION_MODE=true
"""