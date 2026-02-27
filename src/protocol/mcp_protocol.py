import json
import uuid
from typing import Dict, Any, Optional, List


class MCPProtocol:
    """MCP 协议实现"""

    def __init__(self):
        self.protocol_version = "2024-11-05"

    def create_request(self, method: str, params: Dict[str, Any] = None, request_id: str = None) -> Dict[str, Any]:
        """创建请求消息"""
        return {
            "jsonrpc": "2.0",
            "id": request_id or str(uuid.uuid4()),
            "method": method,
            "params": params or {}
        }

    def create_response(self, request_id: str, result: Any = None) -> Dict[str, Any]:
        """创建成功响应"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }

    def create_error_response(self, code: int, message: str, data: Any = None, request_id: str = None) -> Dict[str, Any]:
        """创建错误响应"""
        error = {
            "code": code,
            "message": message
        }
        if data is not None:
            error["data"] = data

        response = {
            "jsonrpc": "2.0",
            "error": error
        }
        if request_id:
            response["id"] = request_id

        return response

    def create_notification(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """创建通知消息"""
        return {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }

    def validate_message(self, message: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """验证消息格式"""
        if not isinstance(message, dict):
            return False, "消息必须是字典类型"

        if "jsonrpc" not in message or message["jsonrpc"] != "2.0":
            return False, "缺少或无效的 jsonrpc 版本"

        if "method" not in message:
            return False, "缺少 method 字段"

        return True, None

    def parse_message(self, message_str: str) -> Optional[Dict[str, Any]]:
        """解析消息字符串"""
        try:
            return json.loads(message_str)
        except json.JSONDecodeError:
            return None

    def serialize_message(self, message: Dict[str, Any]) -> str:
        """序列化消息为字符串"""
        return json.dumps(message, ensure_ascii=False)

    def is_request(self, message: Dict[str, Any]) -> bool:
        """判断是否为请求消息"""
        return "id" in message and "method" in message

    def is_response(self, message: Dict[str, Any]) -> bool:
        """判断是否为响应消息"""
        return "id" in message and ("result" in message or "error" in message)

    def is_notification(self, message: Dict[str, Any]) -> bool:
        """判断是否为通知消息"""
        return "id" not in message and "method" in message
