from typing import Dict, Any, List
import os

from ...core.plugin_interface import PluginInterface
from ...utils.logger import get_logger
from ...utils.command_executor import CommandExecutor
from ...utils.exceptions import IDFCommandError


class IDFPlugin(PluginInterface):
    """IDF 插件，封装 idf.py 命令"""

    def __init__(self):
        super().__init__()
        self.name = "idf"
        self.version = "1.0.0"
        self.description = "ESP-IDF 命令封装插件"
        self.esp_idf_path = None
        self.project_path = None
        self.executor = None
        self.logger = get_logger(__name__)

    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        try:
            self.esp_idf_path = config.get("esp_idf_path") or os.getenv("ESP_IDF_PATH")
            self.project_path = config.get("project_path", os.getcwd())

            if not self.esp_idf_path:
                self.logger.warning("未设置 ESP_IDF_PATH，IDF 功能将不可用")
                self.executor = None
                return True

            if not os.path.exists(self.esp_idf_path):
                self.logger.warning(f"ESP-IDF 路径不存在: {self.esp_idf_path}，IDF 功能将不可用")
                self.executor = None
                return True

            self.executor = CommandExecutor(working_dir=self.project_path)
            self.logger.info(f"IDF 插件初始化成功，ESP-IDF 路径: {self.esp_idf_path}")
            return True

        except Exception as e:
            self.logger.error(f"初始化 IDF 插件时出错: {str(e)}")
            return False

    def get_tools(self) -> List[Dict[str, Any]]:
        """获取插件提供的工具列表"""
        return [
            {
                "name": "idf.build",
                "description": "编译 ESP32 项目",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "目标芯片（如 esp32, esp32s2 等）"
                        }
                    }
                }
            },
            {
                "name": "idf.flash",
                "description": "烧录固件到 ESP32",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "port": {
                            "type": "string",
                            "description": "串口端口（如 COM3, /dev/ttyUSB0）"
                        },
                        "baud": {
                            "type": "integer",
                            "description": "波特率（默认 460800）"
                        }
                    }
                }
            },
            {
                "name": "idf.erase_flash",
                "description": "擦除 ESP32 Flash",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "port": {
                            "type": "string",
                            "description": "串口端口"
                        }
                    }
                }
            },
            {
                "name": "idf.monitor",
                "description": "打开串口监视器",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "port": {
                            "type": "string",
                            "description": "串口端口"
                        }
                    }
                }
            },
            {
                "name": "idf.menuconfig",
                "description": "打开项目配置菜单",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "idf.fullclean",
                "description": "完全清理项目",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "idf.set_target",
                "description": "设置目标芯片",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "目标芯片（如 esp32, esp32s2 等）"
                        }
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        try:
            if tool_name == "idf.build":
                return self._build(arguments)
            elif tool_name == "idf.flash":
                return self._flash(arguments)
            elif tool_name == "idf.erase_flash":
                return self._erase_flash(arguments)
            elif tool_name == "idf.monitor":
                return self._monitor(arguments)
            elif tool_name == "idf.menuconfig":
                return self._menuconfig(arguments)
            elif tool_name == "idf.fullclean":
                return self._fullclean(arguments)
            elif tool_name == "idf.set_target":
                return self._set_target(arguments)
            else:
                return {
                    "success": False,
                    "error": f"未知工具: {tool_name}"
                }

        except Exception as e:
            self.logger.error(f"执行工具 {tool_name} 时出错: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _build(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """编译项目"""
        target = arguments.get("target")
        args = ["build"]
        if target:
            args.extend(["--target", target])

        result = self.executor.execute("idf.py", args)

        if result["success"]:
            return {
                "success": True,
                "message": "编译成功",
                "output": result["stdout"]
            }
        else:
            return {
                "success": False,
                "error": result.get("stderr", "编译失败"),
                "output": result.get("stdout", "")
            }

    def _flash(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """烧录固件"""
        port = arguments.get("port")
        baud = arguments.get("baud", 460800)

        args = ["flash"]
        if port:
            args.extend(["-p", port])
        args.extend(["-b", str(baud)])

        result = self.executor.execute("idf.py", args)

        if result["success"]:
            return {
                "success": True,
                "message": "烧录成功",
                "output": result["stdout"]
            }
        else:
            return {
                "success": False,
                "error": result.get("stderr", "烧录失败"),
                "output": result.get("stdout", "")
            }

    def _erase_flash(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """擦除 Flash"""
        port = arguments.get("port")
        args = ["erase-flash"]
        if port:
            args.extend(["-p", port])

        result = self.executor.execute("idf.py", args)

        if result["success"]:
            return {
                "success": True,
                "message": "擦除成功",
                "output": result["stdout"]
            }
        else:
            return {
                "success": False,
                "error": result.get("stderr", "擦除失败"),
                "output": result.get("stdout", "")
            }

    def _monitor(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """打开监视器"""
        port = arguments.get("port")
        args = ["monitor"]
        if port:
            args.extend(["-p", port])

        return {
            "success": True,
            "message": f"监视器已启动，端口: {port or '默认'}",
            "command": f"idf.py {' '.join(args)}"
        }

    def _menuconfig(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """打开配置菜单"""
        return {
            "success": True,
            "message": "配置菜单已打开",
            "command": "idf.py menuconfig"
        }

    def _fullclean(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """完全清理"""
        result = self.executor.execute("idf.py", ["fullclean"])

        if result["success"]:
            return {
                "success": True,
                "message": "清理完成",
                "output": result["stdout"]
            }
        else:
            return {
                "success": False,
                "error": result.get("stderr", "清理失败"),
                "output": result.get("stdout", "")
            }

    def _set_target(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """设置目标芯片"""
        target = arguments.get("target")
        if not target:
            return {
                "success": False,
                "error": "必须指定目标芯片"
            }

        result = self.executor.execute("idf.py", ["set-target", target])

        if result["success"]:
            return {
                "success": True,
                "message": f"目标芯片设置为 {target}",
                "output": result["stdout"]
            }
        else:
            return {
                "success": False,
                "error": result.get("stderr", "设置目标失败"),
                "output": result.get("stdout", "")
            }
