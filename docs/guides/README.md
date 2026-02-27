# 使用指南

## 安装

### 环境要求

- Python 3.8+
- ESP-IDF 开发环境
- MCP 客户端（Claude Desktop、Cursor 等）

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/yourusername/ESP32-MCP.git
cd ESP32-MCP
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置 ESP-IDF
```bash
cp config/config.yaml.example config/config.yaml
# 编辑 config.yaml，设置 ESP_IDF_PATH
```

## 配置 MCP 客户端

### Claude Desktop

在 Claude Desktop 配置文件中添加：

```json
{
  "mcpServers": {
    "esp32": {
      "command": "python",
      "args": ["E:\\Desktop\\ESP32-MCP\\main.py"],
      "env": {
        "ESP_IDF_PATH": "C:\\Espressif\\esp-idf"
      }
    }
  }
}
```

### Cursor

在 Cursor 设置中添加 MCP 服务器配置。

## 使用

### 基本操作

1. 启动服务器
```bash
python main.py
```

2. 在 MCP 客户端中调用工具

### 常见任务

#### 编译项目
```
请帮我编译 ESP32 项目
```

#### 烧录固件
```
请将固件烧录到 COM3 端口
```

#### 监控串口
```
请启动串口监控，端口是 COM3
```

## 故障排除

### ESP-IDF 路径错误

确保 `config.yaml` 中的 `esp_idf_path` 正确。

### 串口连接失败

检查串口端口是否正确，是否有权限访问。

### 编译失败

检查 ESP-IDF 环境是否正确设置，项目路径是否正确。
