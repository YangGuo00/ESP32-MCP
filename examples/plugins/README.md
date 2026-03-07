# 插件开发示例

## MCP 客户端示例

本目录包含 MCP 客户端示例代码，演示如何通过 MCP 协议调用 ESP32-MCP 服务器的工具。

### 运行 MCP 客户端示例

```bash
cd examples/plugins
python mcp_client_example.py
```

### 示例功能

客户端示例演示了以下功能：

1. **连接到 MCP 服务器** - 通过 stdio 协议连接到 `main.py`
2. **列出可用工具** - 获取所有可用的 MCP 工具列表及其参数
3. **调用工具** - 演示如何调用 `idf_version` 和 `idf_build` 等工具
4. **错误处理** - 当缺少必需参数时，服务器会返回清晰的错误信息

### AI 如何使用 MCP 协议

当 AI 通过 MCP 客户端调用工具时：

1. **初始化连接**: AI 客户端连接到 MCP 服务器
2. **获取工具列表**: AI 调用 `list_tools()` 获取所有可用工具及其参数信息
3. **参数验证**: AI 根据工具的参数信息决定需要哪些参数
   - 例如：`idf_build` 工具显示 `project_path: Path to the ESP32 project directory (required)`
   - AI 知道需要用户提供项目路径
4. **调用工具**: AI 收集所有必需参数后调用工具
5. **错误反馈**: 如果缺少参数或路径无效，服务器返回清晰的错误信息
   - 例如：`"缺少必需参数: project_path。请提供 ESP32 项目目录路径"`
   - 或：`"项目路径不存在: D:/example/project"`

### 错误处理示例

当 AI 调用工具时，可能会遇到以下错误：

1. **缺少必需参数**:
   ```json
   {
     "success": false,
     "error": "缺少必需参数: project_path。请提供 ESP32 项目目录路径"
   }
   ```

2. **项目路径不存在**:
   ```json
   {
     "success": false,
     "error": "项目路径不存在: D:/example/project"
   }
   ```

3. **编译失败**:
   ```json
   {
     "success": false,
     "error": "编译失败的具体错误信息",
     "output": "命令输出内容"
   }
   ```

AI 应该根据这些错误信息：
- 提示用户提供正确的参数
- 验证路径是否存在
- 显示详细的错误信息给用户

### 工具列表

#### IDF 工具

所有 IDF 工具都需要提供 `project_path` 参数（必需）：

- `idf_build(project_path, target)` - 编译 ESP32 项目
  - `project_path`: ESP32 项目目录路径（**必需**）
  - `target`: 目标芯片（可选，如 esp32, esp32s3, esp32c3）
  - **错误处理**: 如果缺少 `project_path` 或路径不存在，会返回清晰的错误信息

- `idf_flash(project_path, port, baud)` - 烧录固件到 ESP32 设备
  - `project_path`: ESP32 项目目录路径（**必需**）
  - `port`: 串口号（可选）
  - `baud`: 波特率（可选，默认 460800）
  - **错误处理**: 如果缺少 `project_path` 或路径不存在，会返回清晰的错误信息

- `idf_erase_flash(project_path, port)` - 擦除 ESP32 Flash
  - `project_path`: ESP32 项目目录路径（**必需**）
  - `port`: 串口号（可选）
  - **错误处理**: 如果缺少 `project_path` 或路径不存在，会返回清晰的错误信息

- `idf_monitor(project_path, port)` - 打开 ESP32 串口监视器
  - `project_path`: ESP32 项目目录路径（**必需**）
  - `port`: 串口号（可选）
  - **错误处理**: 如果缺少 `project_path` 或路径不存在，会返回清晰的错误信息

- `idf_menuconfig(project_path)` - 打开项目配置菜单
  - `project_path`: ESP32 项目目录路径（**必需**）
  - **错误处理**: 如果缺少 `project_path` 或路径不存在，会返回清晰的错误信息

- `idf_fullclean(project_path)` - 清理项目构建文件
  - `project_path`: ESP32 项目目录路径（**必需**）
  - **错误处理**: 如果缺少 `project_path` 或路径不存在，会返回清晰的错误信息

- `idf_set_target(project_path, target)` - 设置目标芯片
  - `project_path`: ESP32 项目目录路径（**必需**）
  - `target`: 目标芯片（必需，如 esp32, esp32s3, esp32c3）
  - **错误处理**: 如果缺少 `project_path`、`target` 或路径不存在，会返回清晰的错误信息

- `idf_version()` - 获取 ESP-IDF 版本号（不需要项目路径）

#### 串口工具

- `serial_list_ports()` - 列出可用的串口
- `serial_open(port, baud)` - 打开串口
- `serial_close(port)` - 关闭串口
- `serial_read(port, bytes)` - 从串口读取数据
- `serial_write(port, data)` - 向串口写入数据

#### 监控工具

- `monitor_start()` - 开始监控 ESP32 数据
- `monitor_stop()` - 停止监控
- `monitor_get_data()` - 获取监控数据

#### 日志工具

- `logger_get_logs(lines)` - 获取系统日志
- `logger_clear_logs()` - 清除系统日志

### 使用示例

#### 获取 ESP-IDF 版本

```python
result = await session.call_tool("idf_version", {})
```

#### 编译 ESP32 项目

```python
result = await session.call_tool("idf_build", {
    "project_path": "D:/path/to/your/project",
    "target": "esp32"
})
```

#### 烧录固件

```python
result = await session.call_tool("idf_flash", {
    "project_path": "D:/path/to/your/project",
    "port": "COM3",
    "baud": 460800
})
```

#### 列出串口

```python
result = await session.call_tool("serial_list_ports", {})
```

### 完整示例代码

```python
import asyncio
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession

async def main():
    # 配置服务器参数
    server_params = StdioServerParameters(
        command="python",
        args=["E:/Desktop/ESP32-MCP/main.py"]
    )
    
    # 连接到服务器
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 初始化会话
            await session.initialize()
            
            # 调用工具
            result = await session.call_tool("idf_version", {})
            print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## 创建自定义插件

### 1. 创建插件目录

```
src/plugins/my_plugin/
├── __init__.py
└── plugin.py
```

### 2. 实现插件类

```python
from typing import Dict, Any, List
from ...core.plugin_interface import PluginInterface
from ...utils.logger import get_logger

class MyPlugin(PluginInterface):
    def __init__(self):
        super().__init__()
        self.name = "my_plugin"
        self.version = "1.0.0"
        self.description = "我的自定义插件"
        self.logger = get_logger(__name__)

    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        self.logger.info("插件初始化成功")
        return True

    def get_tools(self) -> List[Dict[str, Any]]:
        """返回插件提供的工具列表"""
        return [
            {
                "name": "my_plugin.hello",
                "description": "打招呼",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "名字"
                        }
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        if tool_name == "my_plugin.hello":
            name = arguments.get("name", "World")
            return {
                "success": True,
                "message": f"Hello, {name}!"
            }
        else:
            return {
                "success": False,
                "error": f"未知工具: {tool_name}"
            }
```

### 3. 配置插件

在 `config/config.yaml` 中添加：

```yaml
plugins:
  my_plugin:
    enabled: true
```

### 4. 在 main.py 中注册工具

```python
from src.plugins.my_plugin.plugin import MyPlugin

# 初始化插件
my_plugin = MyPlugin()
my_plugin.initialize(config.get("plugins", {}).get("my_plugin", {}))

# 注册 MCP 工具
@mcp.tool()
def my_plugin_hello(name: str = "World"):
    """打招呼"""
    return my_plugin.execute_tool("my_plugin.hello", {"name": name})
```

### 5. 使用插件

```python
# 通过 MCP 客户端调用
result = await session.call_tool("my_plugin_hello", {"name": "ESP32"})
```

## 更多示例

查看其他插件的实现：
- [IDF 插件](../../src/plugins/idf/plugin.py)
- [串口插件](../../src/plugins/serial/plugin.py)
- [监控插件](../../src/plugins/monitor/plugin.py)
- [日志插件](../../src/plugins/logger/plugin.py)
