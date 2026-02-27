# ESP32-MCP

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)](https://modelcontextprotocol.io/)

一个基于 MCP (Model Context Protocol) 的 ESP32 开发服务器，通过插件化架构实现对 ESP32 的完全控制，支持 AI 自主编程。

## 特性

- **完整的 IDF.py 控制**: 支持所有 idf.py 命令（编译、烧录、擦除、配置等）
- **实时串口监控**: 监控 ESP32 串口输出，支持数据解析和过滤
- **插件化架构**: 高度模块化，易于扩展和自定义
- **AI 自主编程**: 通过 MCP 协议让 AI 能够自主完成 ESP32 开发流程
- **开源友好**: 清晰的代码结构，完善的文档，适合社区贡献

## 架构

```
┌─────────────────────────────────────┐
│   MCP Server Core (核心服务器)      │
├─────────────────────────────────────┤
│   Plugin Manager (插件管理器)        │
├─────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  │ IDF插件  │ │串口插件 │ │编译插件│ │
│  └─────────┘ └─────────┘ └────────┘ │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  │监控插件  │ │日志插件 │ │其他... │ │
│  └─────────┘ └─────────┘ └────────┘ │
└─────────────────────────────────────┘
```

## 快速开始

### 环境要求

- Python 3.8 或更高版本
- ESP-IDF 开发环境
- MCP 客户端（如 Claude Desktop、Cursor、Trae 等）

### 安装

```bash
# 克隆仓库
git clone https://github.com/YangGuo00/ESP32-MCP.git
cd ESP32-MCP

# 安装依赖
pip install -r requirements.txt

# 配置 ESP-IDF 路径
cp config/config.yaml.example config/config.yaml
# 编辑 config.yaml，设置你的 ESP-IDF 路径
```

### 配置 MCP 客户端

在 MCP 客户端配置文件中添加：

```json
{
  "mcpServers": {
    "esp32": {
      "command": "python",
      "args": ["E:\\Desktop\\ESP32-MCP\\src\\main.py"],
      "env": {
        "ESP_IDF_PATH": "你的ESP-IDF路径"
      }
    }
  }
}
```

### 使用示例

```python
# 通过 MCP 客户端调用
# 编译项目
idf.build()

# 烧录到设备
idf.flash()

# 监控串口输出
serial.monitor()

# 擦除 Flash
idf.erase_flash()
```

## 核心插件

### IDF 插件
封装所有 idf.py 命令，包括：
- `build`: 编译项目
- `flash`: 烧录固件
- `erase_flash`: 擦除 Flash
- `monitor`: 打开串口监视器
- `menuconfig`: 配置项目
- `fullclean`: 完全清理

### 串口插件
- 实时串口数据监控
- 数据解析和过滤
- 双向通信支持

### 构建插件
- 自动化构建流程
- 多目标编译
- 增量编译支持

### 监控插件
- 实时数据收集
- 错误检测和报告
- 性能监控

### 日志插件
- 结构化日志记录
- 日志过滤和搜索
- 多级别日志输出

## 开发

### 项目结构

```
ESP32-MCP/
├── config/              # 配置文件
├── docs/               # 文档
├── examples/           # 示例代码
├── src/                # 源代码
│   ├── core/          # 核心模块
│   ├── plugins/       # 插件
│   ├── protocol/      # MCP 协议
│   └── utils/         # 工具函数
└── tests/             # 测试
```

### 开发自定义插件

1. 在 `src/plugins/` 创建新插件目录
2. 实现插件接口
3. 在 `config/plugins/` 添加配置
4. 重启服务器加载插件

详细文档请参考 [插件开发指南](docs/plugins/README.md)

## 测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/
```

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 致谢

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [ESP-IDF](https://github.com/espressif/esp-idf)

## 联系方式

- Issues: [GitHub Issues](https://github.com/yourusername/ESP32-MCP/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/ESP32-MCP/discussions)

## 路线图

- [ ] 支持更多 ESP32 芯片系列
- [ ] Web UI 界面
- [ ] 远程调试支持
- [ ] AI 代码生成优化
- [ ] 更多社区插件
