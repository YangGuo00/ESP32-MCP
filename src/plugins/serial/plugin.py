from typing import Dict, Any, List
import serial
import serial.tools.list_ports
from threading import Thread, Event
import queue

from ...core.plugin_interface import PluginInterface
from ...utils.logger import get_logger
from ...utils.exceptions import SerialConnectionError, SerialReadError


class SerialPlugin(PluginInterface):
    """串口插件，提供串口通信和监控功能"""

    def __init__(self):
        super().__init__()
        self.name = "serial"
        self.version = "1.0.0"
        self.description = "串口通信和监控插件"
        self.serial_connection = None
        self.monitor_thread = None
        self.monitor_stop_event = Event()
        self.data_queue = queue.Queue()
        self.logger = get_logger(__name__)

    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        try:
            self.logger.info("串口插件初始化成功")
            return True
        except Exception as e:
            self.logger.error(f"初始化串口插件时出错: {str(e)}")
            return False

    def get_tools(self) -> List[Dict[str, Any]]:
        """获取插件提供的工具列表"""
        return [
            {
                "name": "serial.list_ports",
                "description": "列出所有可用的串口",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "serial.connect",
                "description": "连接到串口",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "port": {
                            "type": "string",
                            "description": "串口端口（如 COM3, /dev/ttyUSB0）"
                        },
                        "baudrate": {
                            "type": "integer",
                            "description": "波特率（默认 115200）"
                        }
                    },
                    "required": ["port"]
                }
            },
            {
                "name": "serial.disconnect",
                "description": "断开串口连接",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "serial.write",
                "description": "向串口写入数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "string",
                            "description": "要写入的数据"
                        }
                    },
                    "required": ["data"]
                }
            },
            {
                "name": "serial.read",
                "description": "从串口读取数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "size": {
                            "type": "integer",
                            "description": "读取的字节数（默认 1024）"
                        }
                    }
                }
            },
            {
                "name": "serial.start_monitor",
                "description": "启动串口监控",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "port": {
                            "type": "string",
                            "description": "串口端口"
                        },
                        "baudrate": {
                            "type": "integer",
                            "description": "波特率"
                        }
                    },
                    "required": ["port"]
                }
            },
            {
                "name": "serial.stop_monitor",
                "description": "停止串口监控",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "serial.get_monitor_data",
                "description": "获取监控数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "count": {
                            "type": "integer",
                            "description": "获取的数据条数（默认 10）"
                        }
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        try:
            if tool_name == "serial.list_ports":
                return self._list_ports(arguments)
            elif tool_name == "serial.connect":
                return self._connect(arguments)
            elif tool_name == "serial.disconnect":
                return self._disconnect(arguments)
            elif tool_name == "serial.write":
                return self._write(arguments)
            elif tool_name == "serial.read":
                return self._read(arguments)
            elif tool_name == "serial.start_monitor":
                return self._start_monitor(arguments)
            elif tool_name == "serial.stop_monitor":
                return self._stop_monitor(arguments)
            elif tool_name == "serial.get_monitor_data":
                return self._get_monitor_data(arguments)
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

    def _list_ports(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """列出所有可用串口"""
        try:
            ports = serial.tools.list_ports.comports()
            port_list = []

            for port in ports:
                port_list.append({
                    "device": port.device,
                    "description": port.description,
                    "hwid": port.hwid,
                    "vid": port.vid,
                    "pid": port.pid,
                    "serial_number": port.serial_number
                })

            return {
                "success": True,
                "message": f"找到 {len(port_list)} 个串口",
                "ports": port_list
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"列出串口时出错: {str(e)}"
            }

    def _connect(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """连接到串口"""
        try:
            port = arguments.get("port")
            baudrate = arguments.get("baudrate", 115200)

            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()

            self.serial_connection = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=1
            )

            return {
                "success": True,
                "message": f"已连接到串口 {port}，波特率 {baudrate}"
            }

        except Exception as e:
            raise SerialConnectionError(f"连接串口失败: {str(e)}")

    def _disconnect(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """断开串口连接"""
        try:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
                return {
                    "success": True,
                    "message": "已断开串口连接"
                }
            else:
                return {
                    "success": True,
                    "message": "串口未连接"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"断开连接时出错: {str(e)}"
            }

    def _write(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """写入数据到串口"""
        try:
            if not self.serial_connection or not self.serial_connection.is_open:
                return {
                    "success": False,
                    "error": "串口未连接"
                }

            data = arguments.get("data", "")
            self.serial_connection.write(data.encode('utf-8'))
            self.serial_connection.flush()

            return {
                "success": True,
                "message": f"已写入 {len(data)} 字节"
            }

        except Exception as e:
            raise SerialReadError(f"写入数据失败: {str(e)}")

    def _read(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """从串口读取数据"""
        try:
            if not self.serial_connection or not self.serial_connection.is_open:
                return {
                    "success": False,
                    "error": "串口未连接"
                }

            size = arguments.get("size", 1024)
            data = self.serial_connection.read(size)

            return {
                "success": True,
                "message": f"读取了 {len(data)} 字节",
                "data": data.decode('utf-8', errors='ignore')
            }

        except Exception as e:
            raise SerialReadError(f"读取数据失败: {str(e)}")

    def _start_monitor(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """启动串口监控"""
        try:
            port = arguments.get("port")
            baudrate = arguments.get("baudrate", 115200)

            if self.monitor_thread and self.monitor_thread.is_alive():
                return {
                    "success": False,
                    "error": "监控已在运行"
                }

            self.serial_connection = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=1
            )

            self.monitor_stop_event.clear()
            self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()

            return {
                "success": True,
                "message": f"串口监控已启动，端口: {port}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"启动监控失败: {str(e)}"
            }

    def _stop_monitor(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """停止串口监控"""
        try:
            self.monitor_stop_event.set()

            if self.monitor_thread:
                self.monitor_thread.join(timeout=2)

            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()

            return {
                "success": True,
                "message": "串口监控已停止"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"停止监控失败: {str(e)}"
            }

    def _get_monitor_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """获取监控数据"""
        try:
            count = arguments.get("count", 10)
            data_list = []

            for _ in range(count):
                try:
                    data = self.data_queue.get_nowait()
                    data_list.append(data)
                except queue.Empty:
                    break

            return {
                "success": True,
                "message": f"获取了 {len(data_list)} 条数据",
                "data": data_list
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"获取监控数据失败: {str(e)}"
            }

    def _monitor_loop(self):
        """监控循环"""
        while not self.monitor_stop_event.is_set():
            try:
                if self.serial_connection and self.serial_connection.is_open:
                    data = self.serial_connection.readline()
                    if data:
                        decoded_data = data.decode('utf-8', errors='ignore').strip()
                        if decoded_data:
                            self.data_queue.put({
                                "timestamp": self._get_timestamp(),
                                "data": decoded_data
                            })
            except Exception as e:
                self.logger.error(f"监控循环出错: {str(e)}")

    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def shutdown(self):
        """关闭插件"""
        self._stop_monitor({})
        super().shutdown()
