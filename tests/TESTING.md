# ESP32-MCP 本地测试指南

## 测试文件

项目根目录下有以下测试文件：

- **test_features.py** - 重点功能测试脚本
- **test_server_backup.py** - 服务器初始化测试（备份）
- **test_plugins_backup.py** - 插件导入测试（备份）
- **test_plugin_manager_backup.py** - 插件管理器测试（备份）

## 快速测试

### 运行重点功能测试

```bash
python test_features.py
```

这个脚本会测试：
- ✓ IDF 编译功能
- ✓ 串口列表功能
- ✓ 日志功能
- ✓ 监控功能
- ✓ 构建功能
- ✓ MCP 协议
- ✓ 工具列表

### 测试服务器启动

```bash
python main.py
```

## 改进说明

### 1. ESP-IDF 路径自动检测

系统现在会自动检测 ESP-IDF 安装路径，按以下优先级：

1. 环境变量 `ESP_IDF_PATH`
2. 环境变量 `IDF_PATH`
3. 配置文件 `config.yaml` 中的 `esp_idf_path`
4. 常见安装路径：
   - `C:/Espressif/esp-idf`
   - `C:/Users/<用户名>/.espressif/esp-idf`
   - `~/.espressif/esp-idf`

### 2. 串口日志读取功能

新增了 `serial.read_log_file` 工具，可以读取串口日志文件：

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "serial.read_log_file",
    "arguments": {
      "file_path": "logs/serial.log",
      "lines": 100,
      "filter": "error"
    }
  }
}
```

### 3. 配置改进

在 `config.yaml` 中添加了 `plugin_dir` 配置项，可以自定义插件目录：

```yaml
plugin_dir: "src/plugins"
```

## AI 自主编程工作流

### 1. 编译和下载

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "idf.build",
    "arguments": {
      "target": "esp32"
    }
  }
}
```

### 2. 烧录固件

```json
{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "tools/call",
  "params": {
    "name": "idf.flash",
    "arguments": {
      "port": "COM3",
      "baud": 460800
    }
  }
}
```

### 3. 监控串口输出

```json
{
  "jsonrpc": "2.0",
  "id": "3",
  "method": "tools/call",
  "params": {
    "name": "serial.start_monitor",
    "arguments": {
      "port": "COM3",
      "baudrate": 115200
    }
  }
}
```

### 4. 读取日志分析错误

```json
{
  "jsonrpc": "2.0",
  "id": "4",
  "method": "tools/call",
  "params": {
    "name": "serial.read_log_file",
    "arguments": {
      "file_path": "logs/serial.log",
      "lines": 50,
      "filter": "error"
    }
  }
}
```

### 5. 根据日志修改代码

AI 可以根据日志输出：
- 识别错误类型
- 定位错误位置
- 分析错误原因
- 生成修复方案
- 调用 `idf.build` 重新编译
- 调用 `idf.flash` 重新烧录

## 故障排除

### 插件未加载

如果插件未加载，检查：
1. `config.yaml` 中的 `plugin_dir` 配置
2. 插件目录是否存在
3. 插件目录下是否有 `plugin.py` 文件

### ESP-IDF 路径问题

如果 ESP-IDF 功能不可用：
1. 检查 ESP-IDF 是否已安装
2. 设置环境变量 `ESP_IDF_PATH`
3. 或在 `config.yaml` 中配置 `esp_idf_path`

### 工具未找到

如果工具未找到：
1. 检查插件是否正确加载
2. 查看服务器日志输出
3. 运行 `python test_features.py` 查看工具列表

## 下一步

1. 运行 `python test_features.py` 测试所有功能
2. 运行 `python main.py` 启动 MCP 服务器
3. 在 MCP 客户端中测试各个工具
4. 根据测试结果调整配置
