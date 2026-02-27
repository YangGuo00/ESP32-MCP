# 插件开发指南

## 插件架构

所有插件必须继承 `PluginInterface` 基类并实现以下方法：

- `initialize(config)`: 初始化插件
- `get_tools()`: 返回插件提供的工具列表
- `execute_tool(tool_name, arguments)`: 执行工具
- `shutdown()`: 关闭插件（可选）

## 创建插件

### 1. 创建插件目录

在 `src/plugins/` 下创建新目录：

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
        self.description = "插件描述"
        self.logger = get_logger(__name__)

    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        # 从配置中读取参数
        self.some_param = config.get("some_param", "default_value")
        self.logger.info("插件初始化成功")
        return True

    def get_tools(self) -> List[Dict[str, Any]]:
        """返回工具列表"""
        return [
            {
                "name": "my_plugin.tool_name",
                "description": "工具描述",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "参数1描述"
                        },
                        "param2": {
                            "type": "integer",
                            "description": "参数2描述"
                        }
                    },
                    "required": ["param1"]
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        try:
            if tool_name == "my_plugin.tool_name":
                param1 = arguments.get("param1")
                param2 = arguments.get("param2", 0)

                # 执行工具逻辑
                result = self._do_something(param1, param2)

                return {
                    "success": True,
                    "message": "执行成功",
                    "result": result
                }
            else:
                return {
                    "success": False,
                    "error": f"未知工具: {tool_name}"
                }
        except Exception as e:
            self.logger.error(f"执行工具时出错: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _do_something(self, param1: str, param2: int) -> Any:
        """工具的具体实现"""
        # 实现你的逻辑
        return f"处理结果: {param1}, {param2}"

    def shutdown(self):
        """关闭插件"""
        self.logger.info("插件已关闭")
```

### 3. 配置插件

在 `config/config.yaml` 中添加：

```yaml
plugins:
  my_plugin:
    enabled: true
    some_param: "value"
```

## 工具定义

每个工具需要定义以下属性：

- `name`: 工具名称（格式：`plugin_name.tool_name`）
- `description`: 工具描述
- `inputSchema`: 输入参数的 JSON Schema

### JSON Schema 示例

```json
{
  "type": "object",
  "properties": {
    "param1": {
      "type": "string",
      "description": "参数描述"
    },
    "param2": {
      "type": "integer",
      "description": "参数描述",
      "default": 0
    }
  },
  "required": ["param1"]
}
```

## 返回值格式

工具执行成功时：

```python
{
    "success": True,
    "message": "执行成功",
    "result": any_data
}
```

工具执行失败时：

```python
{
    "success": False,
    "error": "错误信息"
}
```

## 最佳实践

1. **错误处理**: 始终使用 try-except 捕获异常
2. **日志记录**: 使用 `self.logger` 记录重要信息
3. **参数验证**: 验证输入参数的有效性
4. **资源清理**: 在 `shutdown()` 中清理资源
5. **文档**: 为工具提供清晰的描述和参数说明

## 示例插件

参考以下插件的实现：

- [IDF 插件](../../src/plugins/idf/plugin.py)
- [串口插件](../../src/plugins/serial/plugin.py)
- [监控插件](../../src/plugins/monitor/plugin.py)
