from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class PluginInterface(ABC):
    """插件基类，所有插件必须继承此类"""

    def __init__(self):
        self.name: str = ""
        self.version: str = "1.0.0"
        self.description: str = ""
        self.enabled: bool = True

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        pass

    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """获取插件提供的工具列表"""
        pass

    @abstractmethod
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        pass

    def shutdown(self):
        """关闭插件"""
        pass

    def get_info(self) -> Dict[str, Any]:
        """获取插件信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "enabled": self.enabled
        }
