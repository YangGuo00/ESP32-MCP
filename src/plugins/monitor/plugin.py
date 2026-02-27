from typing import Dict, Any, List
from datetime import datetime
import re

from ...core.plugin_interface import PluginInterface
from ...utils.logger import get_logger


class MonitorPlugin(PluginInterface):
    """监控插件，提供数据监控和分析功能"""

    def __init__(self):
        super().__init__()
        self.name = "monitor"
        self.version = "1.0.0"
        self.description = "数据监控和分析插件"
        self.monitor_data = []
        self.logger = get_logger(__name__)

    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        try:
            max_data_size = config.get("max_data_size", 1000)
            self.max_data_size = max_data_size
            self.logger.info(f"监控插件初始化成功，最大数据量: {max_data_size}")
            return True
        except Exception as e:
            self.logger.error(f"初始化监控插件时出错: {str(e)}")
            return False

    def get_tools(self) -> List[Dict[str, Any]]:
        """获取插件提供的工具列表"""
        return [
            {
                "name": "monitor.add_data",
                "description": "添加监控数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "string",
                            "description": "监控数据"
                        },
                        "source": {
                            "type": "string",
                            "description": "数据来源"
                        }
                    },
                    "required": ["data"]
                }
            },
            {
                "name": "monitor.get_data",
                "description": "获取监控数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "count": {
                            "type": "integer",
                            "description": "获取的数据条数"
                        },
                        "filter": {
                            "type": "string",
                            "description": "过滤条件（正则表达式）"
                        }
                    }
                }
            },
            {
                "name": "monitor.clear_data",
                "description": "清空监控数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "monitor.analyze",
                "description": "分析监控数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "分析模式（error, warning, info）"
                        }
                    }
                }
            },
            {
                "name": "monitor.get_stats",
                "description": "获取监控统计信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        try:
            if tool_name == "monitor.add_data":
                return self._add_data(arguments)
            elif tool_name == "monitor.get_data":
                return self._get_data(arguments)
            elif tool_name == "monitor.clear_data":
                return self._clear_data(arguments)
            elif tool_name == "monitor.analyze":
                return self._analyze(arguments)
            elif tool_name == "monitor.get_stats":
                return self._get_stats(arguments)
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

    def _add_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """添加监控数据"""
        data = arguments.get("data", "")
        source = arguments.get("source", "unknown")

        data_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "data": data,
            "source": source
        }

        self.monitor_data.append(data_entry)

        if len(self.monitor_data) > self.max_data_size:
            self.monitor_data = self.monitor_data[-self.max_data_size:]

        return {
            "success": True,
            "message": "数据已添加",
            "total_count": len(self.monitor_data)
        }

    def _get_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """获取监控数据"""
        count = arguments.get("count", 10)
        filter_pattern = arguments.get("filter")

        data_to_return = self.monitor_data

        if filter_pattern:
            try:
                regex = re.compile(filter_pattern, re.IGNORECASE)
                data_to_return = [
                    d for d in self.monitor_data
                    if regex.search(d["data"])
                ]
            except re.error:
                return {
                    "success": False,
                    "error": "无效的正则表达式"
                }

        if count > 0:
            data_to_return = data_to_return[-count:]

        return {
            "success": True,
            "message": f"获取了 {len(data_to_return)} 条数据",
            "data": data_to_return
        }

    def _clear_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """清空监控数据"""
        cleared_count = len(self.monitor_data)
        self.monitor_data.clear()

        return {
            "success": True,
            "message": f"已清空 {cleared_count} 条数据"
        }

    def _analyze(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """分析监控数据"""
        pattern = arguments.get("pattern", "all")

        analysis_result = {
            "total": len(self.monitor_data),
            "errors": 0,
            "warnings": 0,
            "info": 0
        }

        for entry in self.monitor_data:
            data = entry["data"].lower()

            if "error" in data or "err" in data:
                analysis_result["errors"] += 1
            elif "warning" in data or "warn" in data:
                analysis_result["warnings"] += 1
            else:
                analysis_result["info"] += 1

        if pattern == "error":
            result = [d for d in self.monitor_data if "error" in d["data"].lower()]
        elif pattern == "warning":
            result = [d for d in self.monitor_data if "warning" in d["data"].lower()]
        elif pattern == "info":
            result = [d for d in self.monitor_data if "error" not in d["data"].lower() and "warning" not in d["data"].lower()]
        else:
            result = self.monitor_data

        return {
            "success": True,
            "message": "分析完成",
            "analysis": analysis_result,
            "matched_data": result[:10]
        }

    def _get_stats(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """获取监控统计信息"""
        if not self.monitor_data:
            return {
                "success": True,
                "message": "暂无监控数据",
                "stats": {
                    "total": 0,
                    "sources": {},
                    "time_range": None
                }
            }

        sources = {}
        for entry in self.monitor_data:
            source = entry["source"]
            sources[source] = sources.get(source, 0) + 1

        first_time = self.monitor_data[0]["timestamp"]
        last_time = self.monitor_data[-1]["timestamp"]

        return {
            "success": True,
            "message": "统计信息",
            "stats": {
                "total": len(self.monitor_data),
                "sources": sources,
                "time_range": {
                    "first": first_time,
                    "last": last_time
                }
            }
        }
