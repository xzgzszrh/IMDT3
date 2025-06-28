# 串口自动验证程序使用说明

## 功能概述

这是一个用于测试串口通信的自动验证程序，支持：
- 交互式串口通信测试
- 预定义快捷指令
- 批量测试模式
- 实时数据监听
- 测试结果统计和保存
- 响应时间测量

## 安装依赖

```bash
pip install pyserial
```

## 基本使用

### 1. 交互模式（推荐）

```bash
# 使用默认配置
python serial_tester.py

# 指定串口和波特率
python serial_tester.py --port /dev/ttyUSB0 --baudrate 115200

# 在macOS上使用USB串口
python serial_tester.py --port /dev/cu.usbserial-1410
```

### 2. 查看当前配置

```bash
python serial_tester.py --config
```

### 3. 批量测试模式

```bash
# 运行指定的测试指令
python serial_tester.py --test "STATUS,RESET,START,STOP"
```

## 交互模式操作

启动交互模式后，你可以使用以下操作：

### 快捷指令
- `1`: STATUS - 查询状态
- `2`: RESET - 重置系统
- `3`: START - 开始任务
- `4`: STOP - 停止任务
- `5`: GET_INFO - 获取信息
- `6`: TEST_LED - 测试LED
- `7`: TEST_MOTOR - 测试电机
- `8`: GET_SENSOR - 读取传感器
- `9`: CALIBRATE - 校准系统
- `0`: PING - Ping测试

### 控制指令
- `h`: 显示帮助信息
- `s`: 显示统计信息
- `c`: 清空历史记录
- `t`: 运行快速测试（测试前5个快捷指令）
- `q`: 退出程序

### 自定义指令
直接输入任何文本作为自定义指令发送到串口。

## 功能特性

### 1. 实时监听
程序会自动监听串口接收的数据，并实时显示：
```
[14:30:25.123] TX: STATUS
[14:30:25.156] RX: OK:READY (耗时: 0.033s)
```

### 2. 响应时间测量
自动测量每个指令的响应时间，帮助评估系统性能。

### 3. 统计信息
显示测试统计，包括：
- 总测试次数
- 成功/失败率
- 平均响应时间

### 4. 结果保存
退出时可选择保存测试结果为JSON格式，包含：
- 测试配置信息
- 每次测试的详细记录
- 时间戳和响应时间

## 配置说明

程序会自动读取项目的配置文件 `config.py`，你也可以：

1. 创建 `config_local.py` 覆盖默认配置
2. 使用环境变量设置参数
3. 通过命令行参数指定

配置优先级：命令行参数 > 环境变量 > 本地配置 > 默认配置

## 常见串口设备

### Linux/macOS
- USB串口：`/dev/ttyUSB0`, `/dev/ttyUSB1`
- macOS USB串口：`/dev/cu.usbserial-*`
- 蓝牙串口：`/dev/cu.Bluetooth-*`

### Windows
- COM端口：`COM1`, `COM2`, `COM3` 等

## 使用示例

### 示例1：测试Arduino
```bash
# 连接Arduino (通常使用115200波特率)
python serial_tester.py --port /dev/cu.usbmodem14101 --baudrate 115200
```

### 示例2：测试自定义设备
```bash
# 使用9600波特率测试
python serial_tester.py --port /dev/ttyUSB0 --baudrate 9600

# 在交互模式中：
# 输入 "1" 发送 STATUS 指令
# 输入 "HELLO" 发送自定义指令
# 输入 "s" 查看统计
# 输入 "q" 退出
```

### 示例3：批量测试
```bash
# 运行一系列测试指令
python serial_tester.py --port /dev/ttyUSB0 --test "PING,STATUS,GET_INFO,RESET"
```

## 故障排除

### 1. 串口连接失败
- 检查串口设备路径是否正确
- 确认设备已连接且未被其他程序占用
- 检查权限（Linux/macOS可能需要sudo或加入dialout组）

### 2. 无响应
- 检查波特率设置是否正确
- 确认目标设备的通信协议
- 尝试不同的超时时间设置

### 3. 乱码
- 检查波特率、数据位、停止位、校验位设置
- 确认字符编码（程序默认使用UTF-8）

## 扩展功能

你可以修改 `serial_tester.py` 中的 `quick_commands` 字典来自定义快捷指令：

```python
self.quick_commands = {
    '1': {'cmd': 'YOUR_COMMAND', 'desc': '你的指令描述'},
    # 添加更多指令...
}
```

## 注意事项

1. 确保串口设备未被其他程序占用
2. 某些系统可能需要管理员权限访问串口
3. 程序会自动添加 `\r\n` 作为指令结束符
4. 响应超时默认为2秒，可通过 `--timeout` 参数调整
5. 退出时记得保存重要的测试结果