import asyncio
import json
import sys
from typing import Dict, Any, Optional

from .plugin_manager import PluginManager
from ..protocol.mcp_protocol import MCPProtocol
from ..protocol.message_handler import MessageHandler
from ..utils.logger import get_logger


class MCPServer:
    """MCP 服务器核心"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = get_logger(__name__)
        self.plugin_manager = PluginManager()
        self.protocol = MCPProtocol()
        self.message_handler = MessageHandler(self.plugin_manager)
        self.running = False

    async def start(self):
        """启动服务器"""
        self.logger.info("启动 ESP32-MCP 服务器...")

        try:
            plugin_dir = self.config.get("plugin_dir")
            if plugin_dir:
                self.plugin_manager.plugin_dir = plugin_dir

            loaded_count = self.plugin_manager.load_plugins(self.config)
            self.logger.info(f"已加载 {loaded_count} 个插件")

            self.running = True
            await self._run()

        except Exception as e:
            self.logger.error(f"启动服务器时出错: {str(e)}")
            sys.exit(1)

    async def _run(self):
        """运行服务器主循环"""
        self.logger.info("服务器已启动，等待连接...")

        try:
            while self.running:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )

                if not line:
                    break

                try:
                    message = json.loads(line.strip())
                    response = await self._handle_message(message)
                    print(json.dumps(response), flush=True)

                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON 解析错误: {str(e)}")
                    error_response = self.protocol.create_error_response(
                        -32700,
                        "Parse error"
                    )
                    print(json.dumps(error_response), flush=True)

                except Exception as e:
                    self.logger.error(f"处理消息时出错: {str(e)}")
                    error_response = self.protocol.create_error_response(
                        -32603,
                        str(e)
                    )
                    print(json.dumps(error_response), flush=True)

        except KeyboardInterrupt:
            self.logger.info("接收到中断信号，正在关闭服务器...")
        finally:
            await self.stop()

    async def _handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理接收到的消息"""
        try:
            return await self.message_handler.handle(message)
        except Exception as e:
            self.logger.error(f"处理消息时出错: {str(e)}")
            return self.protocol.create_error_response(-32603, str(e))

    async def stop(self):
        """停止服务器"""
        self.logger.info("正在停止服务器...")
        self.running = False
        self.plugin_manager.shutdown_all()
        self.logger.info("服务器已停止")

    def get_status(self) -> Dict[str, Any]:
        """获取服务器状态"""
        plugins = self.plugin_manager.get_all_plugins()
        return {
            "running": self.running,
            "plugins": {
                name: plugin.get_info()
                for name, plugin in plugins.items()
            },
            "tools": self.plugin_manager.get_all_tools()
        }
