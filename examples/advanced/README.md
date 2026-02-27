# 高级示例

## 自动化构建和部署

```python
# 完整的自动化流程
build.rebuild(target="esp32")
idf.flash(port="COM3")
serial.start_monitor(port="COM3")

# 等待一段时间后检查输出
import time
time.sleep(5)
data = serial.get_monitor_data(count=50)
```

## 数据分析和监控

```python
# 启动监控
serial.start_monitor(port="COM3", baudrate=115200)

# 添加监控数据
monitor.add_data(data="System started", source="system")

# 分析监控数据
analysis = monitor.analyze(pattern="error")

# 获取统计信息
stats = monitor.get_stats()
```

## 日志管理

```python
# 记录日志
logger.log(level="info", message="Build started")
logger.log(level="warning", message="Low memory")

# 获取日志
logs = logger.get_logs(level="error", count=10)

# 导出日志
logger.export_logs(format="json", output_file="logs_export.json")
```

## 错误处理

```python
# 检查配置
build.check_config()

# 清理构建
build.clean()

# 完全清理
idf.fullclean()
```
