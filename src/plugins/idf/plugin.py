from typing import Dict, Any, List
import os
import subprocess
import re

from ...core.plugin_interface import PluginInterface
from ...utils.logger import get_logger
from ...utils.command_executor import CommandExecutor
from ...utils.exceptions import IDFCommandError
from ...utils.idf_controller import IDFController


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
        self.idf_env = None
        self.idf_controller = None  # IDF 控制器
        self.logger = get_logger(__name__)

    def _load_idf_environment(self):
        """加载 ESP-IDF 环境变量"""
        try:
            # 运行 export.bat 来获取所有环境变量
            export_bat = os.path.join(self.esp_idf_path, "export.bat")
            
            # 使用 cmd /c 来运行 export.bat 并捕获环境变量
            result = subprocess.run(
                f'cmd /c "{export_bat} && set"',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # 解析环境变量
                env_vars = {}
                for line in result.stdout.split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value
                
                self.idf_env = env_vars
                return env_vars
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"加载 ESP-IDF 环境变量时出错: {str(e)}")
            return None

    def _get_idf_env(self):
        """获取 ESP-IDF 环境变量"""
        env = os.environ.copy()
        if self.idf_env:
            env.update(self.idf_env)
        return env

    def _build_error_response(self, operation: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """构建统一的错误响应"""
        stderr = result.get("stderr", "")
        stdout = result.get("stdout", "")
        returncode = result.get("returncode", -1)
        
        # 构建详细的错误信息
        error_parts = []
        if returncode != 0:
            error_parts.append(f"返回码: {returncode}")
        if stderr:
            error_parts.append(f"错误: {stderr}")
        if stdout:
            error_parts.append(f"输出: {stdout[:200] if len(stdout) > 200 else stdout}")
        
        error_message = f"{operation}失败"
        if error_parts:
            error_message += " - " + "; ".join(error_parts)
        
        self.logger.error(f"{operation}失败: {error_message}")
        return {
            "success": False,
            "error": error_message,
            "output": stdout,
            "stderr": stderr,
            "returncode": returncode
        }

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

            # 创建 IDF 控制器
            self.idf_controller = IDFController(self.esp_idf_path)
            self.idf_controller.start()  # 启动控制器

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
            },
            {
                "name": "idf.version",
                "description": "获取 ESP-IDF 版本号",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
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
            elif tool_name == "idf.version":
                return self._version(arguments)
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
        project_path = arguments.get("project_path")
        target = arguments.get("target")
        
        self.logger.info(f"编译参数: {arguments}")
        self.logger.info(f"project_path: {project_path}, target: {target}")
        
        if not project_path:
            self.logger.warning("缺少 project_path 参数")
            return {
                "success": False,
                "error": "缺少必需参数: project_path。请提供 ESP32 项目目录路径"
            }
        
        if not os.path.exists(project_path):
            self.logger.warning(f"项目路径不存在: {project_path}")
            return {
                "success": False,
                "error": f"项目路径不存在: {project_path}"
            }
        
        # 使用 IDF 控制器执行命令
        if not self.idf_controller:
            return {
                "success": False,
                "error": "IDF 控制器未启动"
            }
        
        # 设置目标芯片
        if target:
            result = self.idf_controller.execute("set-target", args=[target], cwd=project_path)
            if not result.get("success"):
                return result
        
        # 执行编译
        result = self.idf_controller.execute("build", cwd=project_path)
        
        return result

    def _flash(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """烧录固件"""
        project_path = arguments.get("project_path")
        port = arguments.get("port")
        baud = arguments.get("baud", 460800)
        
        if not project_path:
            return {
                "success": False,
                "error": "缺少必需参数: project_path。请提供 ESP32 项目目录路径"
            }
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"项目路径不存在: {project_path}"
            }
        
        # 使用 IDF 控制器执行命令
        if not self.idf_controller:
            return {
                "success": False,
                "error": "IDF 控制器未启动"
            }
        
        # 构建命令参数
        args = ["flash"]
        if port:
            args.extend(["-p", port])
        args.extend(["-b", str(baud)])
        
        # 执行烧录
        result = self.idf_controller.execute("flash", args, cwd=project_path)
        
        return result.to_dict()

    def _erase_flash(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """擦除 Flash"""
        project_path = arguments.get("project_path")
        port = arguments.get("port")
        
        if not project_path:
            return {
                "success": False,
                "error": "缺少必需参数: project_path。请提供 ESP32 项目目录路径"
            }
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"项目路径不存在: {project_path}"
            }
        
        # 使用 IDF 控制器执行命令
        if not self.idf_controller:
            return {
                "success": False,
                "error": "IDF 控制器未启动"
            }
        
        # 构建命令参数
        args = ["erase-flash"]
        if port:
            args.extend(["-p", port])
        
        # 执行擦除
        result = self.idf_controller.execute("erase-flash", args, cwd=project_path)
        
        return result.to_dict()

    def _monitor(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """打开监视器"""
        project_path = arguments.get("project_path")
        port = arguments.get("port")
        
        if not project_path:
            return {
                "success": False,
                "error": "缺少必需参数: project_path。请提供 ESP32 项目目录路径"
            }
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"项目路径不存在: {project_path}"
            }
        
        # 使用 IDF 控制器执行命令
        if not self.idf_controller:
            return {
                "success": False,
                "error": "IDF 控制器未启动"
            }
        
        # 构建命令参数
        args = ["monitor"]
        if port:
            args.extend(["-p", port])
        
        # 执行监视器
        result = self.idf_controller.execute("monitor", args, cwd=project_path)
        
        return result

    def _menuconfig(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """打开配置菜单"""
        project_path = arguments.get("project_path")
        
        if not project_path:
            return {
                "success": False,
                "error": "缺少必需参数: project_path。请提供 ESP32 项目目录路径"
            }
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"项目路径不存在: {project_path}"
            }
        
        # 使用 IDF 控制器执行命令
        if not self.idf_controller:
            return {
                "success": False,
                "error": "IDF 控制器未启动"
            }
        
        # 构建命令参数
        args = ["menuconfig"]
        
        # 执行配置菜单
        result = self.idf_controller.execute("menuconfig", cwd=project_path)
        
        return result

    def _fullclean(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """完全清理"""
        project_path = arguments.get("project_path")
        
        if not project_path:
            return {
                "success": False,
                "error": "缺少必需参数: project_path。请提供 ESP32 项目目录路径"
            }
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"项目路径不存在: {project_path}"
            }
        
        # 使用 IDF 控制器执行命令
        
        if not self.idf_controller:
            return {
                "success": False,
                "error": "IDF 控制器未启动"
            }

        # 构建命令参数

        args = ["fullclean"]
        
        # 执行清理
        result = self.idf_controller.execute("fullclean", cwd=project_path)
        
        return result

    def _set_target(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """设置目标芯片"""
        project_path = arguments.get("project_path")
        target = arguments.get("target")
        
        if not project_path:
            return {
                "success": False,
                "error": "缺少必需参数: project_path。请提供 ESP32 项目目录路径"
            }
        
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": f"项目路径不存在: {project_path}"
            }
        
        if not target:
            return {
                "success": False,
                "error": "必须指定目标芯片"
            }
        
        # 使用 IDF 控制器执行命令
        if not self.idf_controller:
            return {
                "success": False,
                "error": "IDF 控制器未启动"
            }
        
        # 设置目标芯片
        result = self.idf_controller.execute("set-target", args=[target], cwd=project_path)
        
        return result

    def _version(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """获取 ESP-IDF 版本号"""
        try:
            if not self.esp_idf_path:
                return {
                    "success": False,
                    "error": "未设置 ESP_IDF_PATH"
                }

            if not os.path.exists(self.esp_idf_path):
                return {
                    "success": False,
                    "error": f"IDF路径不存在: {self.esp_idf_path}"
                }

            cmake_file = os.path.join(self.esp_idf_path, "tools", "cmake", "version.cmake")
            if os.path.exists(cmake_file):
                with open(cmake_file, 'r') as f:
                    content = f.read()
                    import re
                    match = re.search(r'set\(IDF_VERSION_MAJOR (\d+)\)', content)
                    if match:
                        major = match.group(1)
                        match = re.search(r'set\(IDF_VERSION_MINOR (\d+)\)', content)
                        if match:
                            minor = match.group(1)
                            match = re.search(r'set\(IDF_VERSION_PATCH (\d+)\)', content)
                            if match:
                                patch = match.group(1)
                                version = f"ESP-IDF v{major}.{minor}.{patch}"
                                return {
                                    "success": True,
                                    "message": f"获取到 ESP-IDF 版本号: {version}",
                                    "version": version,
                                    "output": version
                                }

            return {
                "success": False,
                "error": "无法获取 ESP-IDF 版本号，请确保 ESP-IDF 已正确安装"
            }
                
        except Exception as e:
            self.logger.error(f"获取 ESP-IDF 版本号时出错: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
