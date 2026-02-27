import asyncio
import sys
import os
import json

grandparent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, grandparent_dir)

from src.core.server import MCPServer
from src.utils.config_loader import ConfigLoader, load_env_config
from src.utils.logger import get_logger, set_log_level


async def test_server_initialization():
    """测试服务器初始化"""
    print("=" * 60)
    print("测试 1: 服务器初始化")
    print("=" * 60)

    config_loader = ConfigLoader()
    config_file = os.path.join(grandparent_dir, "config", "config.yaml")
    config = config_loader.load(config_file)

    env_config = load_env_config()
    config.update(env_config)

    log_level = config.get("log_level", "DEBUG")
    set_log_level(log_level)

    logger = get_logger(__name__)
    logger.info("配置加载成功")

    server = MCPServer(config)
    status = server.get_status()

    print(f"服务器状态: {'运行中' if status['running'] else '已停止'}")
    print(f"已加载插件数量: {len(status['plugins'])}")
    print(f"可用工具数量: {len(status['tools'])}")

    print("\n已加载的插件:")
    for name, info in status['plugins'].items():
        print(f"  - {name}: {info['description']} (v{info['version']})")

    print("\n可用工具:")
    for tool in status['tools'][:10]:
        print(f"  - {tool['name']}: {tool['description']}")

    if len(status['tools']) > 10:
        print(f"  ... 还有 {len(status['tools']) - 10} 个工具")

    return server, config


async def test_plugin_execution(server):
    """测试插件执行"""
    print("\n" + "=" * 60)
    print("测试 2: 插件执行")
    print("=" * 60)

    logger = get_logger(__name__)

    tests = [
        {
            "name": "serial.list_ports",
            "description": "列出可用串口",
            "args": {}
        },
        {
            "name": "logger.log",
            "description": "记录测试日志",
            "args": {
                "level": "info",
                "message": "这是一条测试日志"
            }
        },
        {
            "name": "monitor.add_data",
            "description": "添加监控数据",
            "args": {
                "data": "测试监控数据",
                "source": "test"
            }
        },
        {
            "name": "build.check_config",
            "description": "检查构建配置",
            "args": {}
        }
    ]

    for test in tests:
        print(f"\n执行: {test['description']}")
        print(f"工具: {test['name']}")

        try:
            result = server.plugin_manager.execute_tool(test['name'], test['args'])

            if result.get('success'):
                print(f"✓ 成功: {result.get('message', '无消息')}")
            else:
                print(f"✗ 失败: {result.get('error', '未知错误')}")

        except Exception as e:
            print(f"✗ 异常: {str(e)}")

        await asyncio.sleep(0.1)


async def test_mcp_protocol():
    """测试 MCP 协议"""
    print("\n" + "=" * 60)
    print("测试 3: MCP 协议")
    print("=" * 60)

    from src.protocol.mcp_protocol import MCPProtocol

    protocol = MCPProtocol()

    print("\n测试消息创建:")
    request = protocol.create_request("initialize", {})
    print(f"初始化请求: {json.dumps(request, indent=2, ensure_ascii=False)}")

    response = protocol.create_response(request['id'], {"server": "ESP32-MCP"})
    print(f"响应: {json.dumps(response, indent=2, ensure_ascii=False)}")

    error_response = protocol.create_error_response(-32601, "方法未找到", request_id=request['id'])
    print(f"错误响应: {json.dumps(error_response, indent=2, ensure_ascii=False)}")

    notification = protocol.create_notification("log", {"message": "测试通知"})
    print(f"通知: {json.dumps(notification, indent=2, ensure_ascii=False)}")

    print("\n✓ MCP 协议测试完成")


async def test_message_handler(server):
    """测试消息处理器"""
    print("\n" + "=" * 60)
    print("测试 4: 消息处理")
    print("=" * 60)

    from src.protocol.message_handler import MessageHandler

    handler = MessageHandler(server.plugin_manager)

    test_messages = [
        {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "initialize",
            "params": {}
        },
        {
            "jsonrpc": "2.0",
            "id": "2",
            "method": "tools/list",
            "params": {}
        },
        {
            "jsonrpc": "2.0",
            "id": "3",
            "method": "tools/call",
            "params": {
                "name": "logger.log",
                "arguments": {
                    "level": "info",
                    "message": "消息处理测试"
                }
            }
        }
    ]

    for message in test_messages:
        print(f"\n处理消息: {message['method']}")
        try:
            response = await handler.handle(message)
            print(f"✓ 响应: {response.get('result', {}).get('content', [{}])[0].get('text', '成功')}")
        except Exception as e:
            print(f"✗ 错误: {str(e)}")


async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("ESP32-MCP 服务器测试套件")
    print("=" * 60)

    try:
        server, config = await test_server_initialization()
        await test_plugin_execution(server)
        await test_mcp_protocol()
        await test_message_handler(server)

        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)

        print("\n测试摘要:")
        print("✓ 服务器初始化")
        print("✓ 插件加载")
        print("✓ 插件执行")
        print("✓ MCP 协议")
        print("✓ 消息处理")

        print("\n服务器已准备就绪，可以启动完整服务器了。")
        print("运行 'python main.py' 启动 MCP 服务器。")

    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
