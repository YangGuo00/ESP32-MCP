from typing import Dict, Any, List


class ToolsRegistry:
    """工具注册表"""

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, tool: Dict[str, Any]) -> bool:
        """注册工具"""
        tool_name = tool.get("name")
        if not tool_name:
            return False

        if tool_name in self.tools:
            return False

        self.tools[tool_name] = tool
        return True

    def unregister_tool(self, tool_name: str) -> bool:
        """注销工具"""
        if tool_name in self.tools:
            del self.tools[tool_name]
            return True
        return False

    def get_tool(self, tool_name: str) -> Dict[str, Any]:
        """获取工具"""
        return self.tools.get(tool_name)

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """获取所有工具"""
        return list(self.tools.values())

    def clear(self):
        """清空注册表"""
        self.tools.clear()

    def count(self) -> int:
        """获取工具数量"""
        return len(self.tools)
