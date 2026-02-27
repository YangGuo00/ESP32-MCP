# API 文档

## MCP 协议

### 初始化

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "initialize",
  "params": {}
}
```

### 列出工具

```json
{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "tools/list",
  "params": {}
}
```

### 调用工具

```json
{
  "jsonrpc": "2.0",
  "id": "3",
  "method": "tools/call",
  "params": {
    "name": "idf.build",
    "arguments": {
      "target": "esp32"
    }
  }
}
```

## 可用工具

### IDF 工具

- `idf.build`: 编译项目
- `idf.flash`: 烧录固件
- `idf.erase_flash`: 擦除 Flash
- `idf.monitor`: 打开监视器
- `idf.menuconfig`: 配置菜单
- `idf.fullclean`: 完全清理
- `idf.set_target`: 设置目标芯片

### 串口工具

- `serial.list_ports`: 列出串口
- `serial.connect`: 连接串口
- `serial.disconnect`: 断开连接
- `serial.write`: 写入数据
- `serial.read`: 读取数据
- `serial.start_monitor`: 启动监控
- `serial.stop_monitor`: 停止监控
- `serial.get_monitor_data`: 获取监控数据

### 构建工具

- `build.clean`: 清理构建
- `build.rebuild`: 重新构建
- `build.check_config`: 检查配置
- `build.get_size`: 获取固件大小

### 监控工具

- `monitor.add_data`: 添加数据
- `monitor.get_data`: 获取数据
- `monitor.clear_data`: 清空数据
- `monitor.analyze`: 分析数据
- `monitor.get_stats`: 获取统计

### 日志工具

- `logger.log`: 记录日志
- `logger.get_logs`: 获取日志
- `logger.clear_logs`: 清空日志
- `logger.export_logs`: 导出日志
