import asyncio
from typing import Dict, Any, Optional

from .mcp_protocol import MCPProtocol
from ..core.plugin_manager import PluginManager
from ..utils.logger import get_logger


class MessageHandler:
    """消息处理器"""

    def __init__(self, plugin_manager: PluginManager):
        self.plugin_manager = plugin_manager
        self.protocol = MCPProtocol()
        self.logger = get_logger(__name__)

    async def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理接收到的消息"""
        is_valid, error = self.protocol.validate_message(message)
        if not is_valid:
            return self.protocol.create_error_response(-32600, error)

        method = message.get("method")
        params = message.get("params", {})
        request_id = message.get("id")

        try:
            if method == "initialize":
                return await self._handle_initialize(request_id, params)
            elif method == "tools/list":
                return await self._handle_tools_list(request_id, params)
            elif method == "tools/call":
                return await self._handle_tools_call(request_id, params)
            elif method == "shutdown":
                return await self._handle_shutdown(request_id, params)
            else:
                return self.protocol.create_error_response(
                    -32601,
                    f"未知方法: {method}",
                    request_id=request_id
                )

        except Exception as e:
            self.logger.error(f"处理方法 {method} 时出错: {str(e)}")
            return self.protocol.create_error_response(
                -32603,
                str(e),
                request_id=request_id
            )

    async def _handle_initialize(self, request_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理初始化请求"""
        capabilities = {
            "tools": {}
        }

        server_info = {
            "name": "esp32-mcp",
            "version": "1.0.0"
        }

        return self.protocol.create_response(request_id, {
            "protocolVersion": self.protocol.protocol_version,
            "capabilities": capabilities,
            "serverInfo": server_info
        })

    async def _handle_tools_list(self, request_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具列表请求"""
        tools = self.plugin_manager.get_all_tools()
        return self.protocol.create_response(request_id, {
            "tools": tools
        })

    async def _handle_tools_call(self, request_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具调用请求"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not tool_name:
            return self.protocol.create_error_response(
                -32602,
                "缺少工具名称",
                request_id=request_id
            )

        result = self.plugin_manager.execute_tool(tool_name, arguments)

        if result.get("success"):
            return self.protocol.create_response(request_id, {
                "content": [
                    {
                        "type": "text",
                        "text": result.get("message", "执行成功")
                    }
                ]
            })
        else:
            return self.protocol.create_error_response(
                -32603,
                result.get("error", "执行失败"),
                request_id=request_id
            )

    async def _handle_shutdown(self, request_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理关闭请求"""
        self.plugin_manager.shutdown_all()
        return self.protocol.create_response(request_id, {})
