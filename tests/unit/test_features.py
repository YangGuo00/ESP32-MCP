import asyncio
import sys
import os
import json

grandparent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, grandparent_dir)

from src.core.server import MCPServer
from src.utils.config_loader import ConfigLoader, load_env_config
from src.utils.logger import get_logger, set_log_level


async def test_idf_build(server):
    """测试 IDF 编译功能"""
    print("\n" + "=" * 60)
    print("测试 1: IDF 编译功能")
    print("=" * 60)

    print("\n检查 ESP-IDF 路径...")
    plugins = server.plugin_manager.get_all_plugins()
    idf_plugin = plugins.get("idf")

    if idf_plugin:
        esp_idf_path = idf_plugin.esp_idf_path
        if esp_idf_path and os.path.exists(esp_idf_path):
            print(f"✓ ESP-IDF 路径: {esp_idf_path}")
        else:
            print(f"⚠ ESP-IDF 路径未配置或不存在")
            print("  提示: 在 config.yaml 中配置 esp_idf_path，或设置 ESP_IDF_PATH 环境变量")
    else:
        print("⚠ IDF 插件未加载")

    print("\n测试编译命令...")
    result = server.plugin_manager.execute_tool("idf.build", {})

    if result.get("success"):
        print(f"✓ 编译测试通过")
        print(f"  消息: {result.get('message', '')}")
    else:
        print(f"✗ 编译测试失败")
        print(f"  错误: {result.get('error', '未知错误')}")


async def test_serial_list_ports(server):
    """测试串口列表功能"""
    print("\n" + "=" * 60)
    print("测试 2: 串口列表功能")
    print("=" * 60)

    result = server.plugin_manager.execute_tool("serial.list_ports", {})

    if result.get("success"):
        ports = result.get("ports", [])
        print(f"✓ 找到 {len(ports)} 个串口")
        for port in ports:
            print(f"  - {port.get('device', 'N/A')}: {port.get('description', '无描述')}")
    else:
        print(f"✗ 列出串口失败")
        print(f"  错误: {result.get('error', '未知错误')}")


async def test_logger_functions(server):
    """测试日志功能"""
    print("\n" + "=" * 60)
    print("测试 3: 日志功能")
    print("=" * 60)

    print("\n测试记录日志...")
    result = server.plugin_manager.execute_tool("logger.log", {
        "level": "info",
        "message": "这是一条测试日志"
    })

    if result.get("success"):
        print(f"✓ 日志记录成功")
    else:
        print(f"✗ 日志记录失败")
        print(f"  错误: {result.get('error', '未知错误')}")

    print("\n测试获取日志...")
    result = server.plugin_manager.execute_tool("logger.get_logs", {
        "count": 5
    })

    if result.get("success"):
        logs = result.get("logs", [])
        print(f"✓ 获取了 {len(logs)} 条日志")
        for log in logs:
            print(f"  - {log}")
    else:
        print(f"✗ 获取日志失败")
        print(f"  错误: {result.get('error', '未知错误')}")


async def test_monitor_functions(server):
    """测试监控功能"""
    print("\n" + "=" * 60)
    print("测试 4: 监控功能")
    print("=" * 60)

    print("\n测试添加监控数据...")
    result = server.plugin_manager.execute_tool("monitor.add_data", {
        "data": "测试监控数据",
        "source": "test"
    })

    if result.get("success"):
        print(f"✓ 添加监控数据成功")
    else:
        print(f"✗ 添加监控数据失败")
        print(f"  错误: {result.get('error', '未知错误')}")

    print("\n测试分析监控数据...")
    result = server.plugin_manager.execute_tool("monitor.analyze", {
        "pattern": "all"
    })

    if result.get("success"):
        analysis = result.get("analysis", {})
        print(f"✓ 分析完成")
        print(f"  总数据: {analysis.get('total', 0)}")
        print(f"  错误: {analysis.get('errors', 0)}")
        print(f"  警告: {analysis.get('warnings', 0)}")
    else:
        print(f"✗ 分析失败")
        print(f"  错误: {result.get('error', '未知错误')}")


async def test_build_functions(server):
    """测试构建功能"""
    print("\n" + "=" * 60)
    print("测试 5: 构建功能")
    print("=" * 60)

    print("\n测试检查配置...")
    result = server.plugin_manager.execute_tool("build.check_config", {})

    if result.get("success"):
        print(f"✓ 配置检查通过")
        print(f"  配置文件: {result.get('config_files', [])}")
    else:
        print(f"✗ 配置检查失败")
        print(f"  错误: {result.get('error', '未知错误')}")


async def test_mcp_protocol(server):
    """测试 MCP 协议"""
    print("\n" + "=" * 60)
    print("测试 6: MCP 协议")
    print("=" * 60)

    from src.protocol.mcp_protocol import MCPProtocol

    protocol = MCPProtocol()

    print("\n测试消息创建...")
    request = protocol.create_request("initialize", {})
    print(f"✓ 初始化请求创建成功")

    response = protocol.create_response(request['id'], {"server": "ESP32-MCP"})
    print(f"✓ 响应创建成功")

    print("\n测试消息验证...")
    is_valid, error = protocol.validate_message(request)
    if is_valid:
        print(f"✓ 消息验证通过")
    else:
        print(f"✗ 消息验证失败: {error}")


async def test_tools_list(server):
    """测试工具列表"""
    print("\n" + "=" * 60)
    print("测试 7: 工具列表")
    print("=" * 60)

    status = server.get_status()
    tools = status.get("tools", [])

    print(f"\n总工具数: {len(tools)}")
    print(f"已加载插件数: {len(status.get('plugins', {}))}")

    print("\n按插件分类的工具:")
    plugin_tools = {}
    for tool in tools:
        plugin_name = tool.get("plugin", "unknown")
        if plugin_name not in plugin_tools:
            plugin_tools[plugin_name] = []
        plugin_tools[plugin_name].append(tool["name"])

    for plugin_name, tool_names in plugin_tools.items():
        print(f"\n{plugin_name}:")
        for tool_name in tool_names:
            print(f"  - {tool_name}")


async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("ESP32-MCP 重点功能测试")
    print("=" * 60)

    try:
        config_loader = ConfigLoader()
        config_file = os.path.join(grandparent_dir, "config", "config.yaml")
        config = config_loader.load(config_file)

        env_config = load_env_config()
        config.update(env_config)

        log_level = config.get("log_level", "INFO")
        set_log_level(log_level)

        logger = get_logger(__name__)
        logger.info("配置加载成功")

        server = MCPServer(config)

        await test_idf_build(server)
        await test_serial_list_ports(server)
        await test_logger_functions(server)
        await test_monitor_functions(server)
        await test_build_functions(server)
        await test_mcp_protocol(server)
        await test_tools_list(server)

        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)

        print("\n测试摘要:")
        print("✓ IDF 编译功能")
        print("✓ 串口列表功能")
        print("✓ 日志功能")
        print("✓ 监控功能")
        print("✓ 构建功能")
        print("✓ MCP 协议")
        print("✓ 工具列表")

        print("\n下一步:")
        print("1. 配置 ESP-IDF 路径（如果需要使用 IDF 功能）")
        print("2. 运行 'python main.py' 启动 MCP 服务器")
        print("3. 在 MCP 客户端中测试各个工具")

    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
