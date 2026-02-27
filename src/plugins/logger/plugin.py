from typing import Dict, Any, List
from datetime import datetime
import os

from ...core.plugin_interface import PluginInterface
from ...utils.logger import get_logger


class LoggerPlugin(PluginInterface):
    """日志插件，提供日志记录和管理功能"""

    def __init__(self):
        super().__init__()
        self.name = "logger"
        self.version = "1.0.0"
        self.description = "日志记录和管理插件"
        self.log_file = None
        self.logger = get_logger(__name__)

    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        try:
            log_dir = config.get("log_dir", "logs")
            self.log_file = os.path.join(log_dir, "esp32_mcp.log")

            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            self.logger.info(f"日志插件初始化成功，日志文件: {self.log_file}")
            return True
        except Exception as e:
            self.logger.error(f"初始化日志插件时出错: {str(e)}")
            return False

    def get_tools(self) -> List[Dict[str, Any]]:
        """获取插件提供的工具列表"""
        return [
            {
                "name": "logger.log",
                "description": "记录日志",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "level": {
                            "type": "string",
                            "description": "日志级别（debug, info, warning, error）"
                        },
                        "message": {
                            "type": "string",
                            "description": "日志消息"
                        }
                    },
                    "required": ["message"]
                }
            },
            {
                "name": "logger.get_logs",
                "description": "获取日志",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "level": {
                            "type": "string",
                            "description": "日志级别过滤"
                        },
                        "count": {
                            "type": "integer",
                            "description": "获取的日志条数"
                        }
                    }
                }
            },
            {
                "name": "logger.clear_logs",
                "description": "清空日志",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "logger.export_logs",
                "description": "导出日志",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "description": "导出格式（json, txt）"
                        },
                        "output_file": {
                            "type": "string",
                            "description": "输出文件路径"
                        }
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        try:
            if tool_name == "logger.log":
                return self._log(arguments)
            elif tool_name == "logger.get_logs":
                return self._get_logs(arguments)
            elif tool_name == "logger.clear_logs":
                return self._clear_logs(arguments)
            elif tool_name == "logger.export_logs":
                return self._export_logs(arguments)
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

    def _log(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """记录日志"""
        level = arguments.get("level", "info").lower()
        message = arguments.get("message", "")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }

        try:
            if self.log_file:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(f"{timestamp} - {level.upper()} - {message}\n")

            return {
                "success": True,
                "message": "日志已记录",
                "log_entry": log_entry
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"记录日志失败: {str(e)}"
            }

    def _get_logs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """获取日志"""
        level_filter = arguments.get("level")
        count = arguments.get("count", 50)

        try:
            if not self.log_file or not os.path.exists(self.log_file):
                return {
                    "success": True,
                    "message": "暂无日志",
                    "logs": []
                }

            logs = []
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if level_filter:
                        if level_filter.lower() in line.lower():
                            logs.append(line.strip())
                    else:
                        logs.append(line.strip())

            if count > 0:
                logs = logs[-count:]

            return {
                "success": True,
                "message": f"获取了 {len(logs)} 条日志",
                "logs": logs
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"获取日志失败: {str(e)}"
            }

    def _clear_logs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """清空日志"""
        try:
            if self.log_file and os.path.exists(self.log_file):
                os.remove(self.log_file)

            return {
                "success": True,
                "message": "日志已清空"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"清空日志失败: {str(e)}"
            }

    def _export_logs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """导出日志"""
        format_type = arguments.get("format", "txt").lower()
        output_file = arguments.get("output_file", f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}")

        try:
            if not self.log_file or not os.path.exists(self.log_file):
                return {
                    "success": False,
                    "error": "没有日志可导出"
                }

            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = f.readlines()

            if format_type == "json":
                import json
                log_entries = []
                for line in logs:
                    parts = line.strip().split(" - ", 2)
                    if len(parts) >= 3:
                        log_entries.append({
                            "timestamp": parts[0],
                            "level": parts[1],
                            "message": parts[2]
                        })

                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(log_entries, f, indent=2, ensure_ascii=False)
            else:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.writelines(logs)

            return {
                "success": True,
                "message": f"日志已导出到 {output_file}",
                "output_file": output_file
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"导出日志失败: {str(e)}"
            }
