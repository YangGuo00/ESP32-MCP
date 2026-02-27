# 插件开发示例

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

### 4. 使用插件

```python
# 通过 MCP 客户端调用
my_plugin.hello(name="ESP32")
```

## 更多示例

查看其他插件的实现：
- [IDF 插件](../../src/plugins/idf/plugin.py)
- [串口插件](../../src/plugins/serial/plugin.py)
- [监控插件](../../src/plugins/monitor/plugin.py)
