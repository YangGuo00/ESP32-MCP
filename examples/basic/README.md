# 基础示例

## 快速开始

### 1. 编译 ESP32 项目

```python
# 通过 MCP 客户端调用
idf.build(target="esp32")
```

### 2. 烧录固件

```python
# 烧录到 COM3 端口
idf.flash(port="COM3", baud=460800)
```

### 3. 监控串口输出

```python
# 列出可用串口
serial.list_ports()

# 启动监控
serial.start_monitor(port="COM3", baudrate=115200)

# 获取监控数据
serial.get_monitor_data(count=10)
```

### 4. 擦除 Flash

```python
idf.erase_flash(port="COM3")
```

## 完整工作流程

```python
# 1. 设置目标芯片
idf.set_target(target="esp32")

# 2. 编译项目
idf.build()

# 3. 烧录固件
idf.flash(port="COM3")

# 4. 启动监控
serial.start_monitor(port="COM3")

# 5. 查看输出
serial.get_monitor_data(count=20)
```
