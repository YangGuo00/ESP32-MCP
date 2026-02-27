import os
import importlib
import inspect
from typing import Dict, List, Any, Optional
from pathlib import Path

from .plugin_interface import PluginInterface
from ..utils.logger import get_logger


class PluginManager:
    """插件管理器，负责插件的加载、卸载和生命周期管理"""

    def __init__(self, plugin_dir: str = None):
        self.plugin_dir = plugin_dir or os.path.join(os.path.dirname(__file__), "plugins")
        self.plugins: Dict[str, PluginInterface] = {}
        self.logger = get_logger(__name__)

    def load_plugins(self, config: Dict[str, Any] = None) -> int:
        """加载所有插件"""
        config = config or {}
        loaded_count = 0

        if not os.path.exists(self.plugin_dir):
            self.logger.warning(f"插件目录不存在: {self.plugin_dir}")
            return 0

        for plugin_name in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, plugin_name)

            if not os.path.isdir(plugin_path):
                continue

            plugin_file = os.path.join(plugin_path, "plugin.py")
            if not os.path.exists(plugin_file):
                self.logger.warning(f"插件 {plugin_name} 缺少 plugin.py 文件")
                continue

            if self._load_plugin(plugin_name, plugin_path, config):
                loaded_count += 1

        self.logger.info(f"成功加载 {loaded_count} 个插件")
        return loaded_count

    def _load_plugin(self, plugin_name: str, plugin_path: str, config: Dict[str, Any]) -> bool:
        """加载单个插件"""
        try:
            plugin_module_name = f"src.plugins.{plugin_name}.plugin"
            plugin_module = importlib.import_module(plugin_module_name)

            plugin_class = None
            for name, obj in inspect.getmembers(plugin_module, inspect.isclass):
                if issubclass(obj, PluginInterface) and obj != PluginInterface:
                    plugin_class = obj
                    break

            if not plugin_class:
                self.logger.warning(f"插件 {plugin_name} 未找到有效的插件类")
                return False

            plugin_instance = plugin_class()
            plugin_config = config.get("plugins", {}).get(plugin_name, {})

            if plugin_instance.initialize(plugin_config):
                self.plugins[plugin_name] = plugin_instance
                self.logger.info(f"插件 {plugin_name} 加载成功")
                return True
            else:
                self.logger.error(f"插件 {plugin_name} 初始化失败")
                return False

        except Exception as e:
            self.logger.error(f"加载插件 {plugin_name} 时出错: {str(e)}")
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """卸载插件"""
        if plugin_name in self.plugins:
            try:
                self.plugins[plugin_name].shutdown()
                del self.plugins[plugin_name]
                self.logger.info(f"插件 {plugin_name} 已卸载")
                return True
            except Exception as e:
                self.logger.error(f"卸载插件 {plugin_name} 时出错: {str(e)}")
                return False
        return False

    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """获取插件实例"""
        return self.plugins.get(plugin_name)

    def get_all_plugins(self) -> Dict[str, PluginInterface]:
        """获取所有插件"""
        return self.plugins.copy()

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """获取所有插件提供的工具"""
        all_tools = []
        for plugin_name, plugin in self.plugins.items():
            if plugin.enabled:
                try:
                    tools = plugin.get_tools()
                    for tool in tools:
                        tool["plugin"] = plugin_name
                    all_tools.extend(tools)
                except Exception as e:
                    self.logger.error(f"获取插件 {plugin_name} 的工具时出错: {str(e)}")
        return all_tools

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        for plugin_name, plugin in self.plugins.items():
            if not plugin.enabled:
                continue

            try:
                tools = plugin.get_tools()
                for tool in tools:
                    if tool.get("name") == tool_name:
                        return plugin.execute_tool(tool_name, arguments)
            except Exception as e:
                self.logger.error(f"执行工具 {tool_name} 时出错: {str(e)}")
                return {
                    "success": False,
                    "error": str(e)
                }

        return {
            "success": False,
            "error": f"工具 {tool_name} 未找到"
        }

    def shutdown_all(self):
        """关闭所有插件"""
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.shutdown()
                self.logger.info(f"插件 {plugin_name} 已关闭")
            except Exception as e:
                self.logger.error(f"关闭插件 {plugin_name} 时出错: {str(e)}")
        self.plugins.clear()
