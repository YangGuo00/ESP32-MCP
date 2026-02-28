"""
MCP Client Example - Testing idf_version Tool

This script demonstrates how to use the MCP client to call the idf_version tool
from the ESP32-MCP server (main.py).
"""

import asyncio
import sys
import os
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession
import logging

# Disable logging to stderr
logging.disable(logging.CRITICAL)


async def test_idf_version():
    """
    Test the idf_version tool through MCP client
    
    This function:
    1. Connects to the ESP32-MCP server (main.py)
    2. Lists available tools
    3. Calls the idf_version tool
    4. Displays the result
    """
    
    print("=" * 70)
    print("MCP Client - Testing idf_version Tool")
    print("=" * 70)
    
    # Get the path to main.py
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main_py_path = os.path.join(project_root, "main.py")
    
    print(f"\n项目根目录: {project_root}")
    print(f"服务器脚本: {main_py_path}")
    
    # Create server parameters with encoding fix
    server_params = StdioServerParameters(
        command="python",
        args=[main_py_path],
        env={
            "PYTHONIOENCODING": "utf-8",
            "FASTMCP_LOG_LEVEL": "WARNING"
        }
    )
    
    try:
        print("\n正在连接到 MCP 服务器...")
        
        # Connect to the server
        async with stdio_client(server_params) as (read_stream, write_stream):
            print("✓ 成功连接到服务器")
            
            # Create client session
            async with ClientSession(read_stream, write_stream) as session:
                print("✓ 会话已创建")
                
                # Initialize the session with timeout
                print("正在初始化会话...")
                try:
                    init_result = await asyncio.wait_for(session.initialize(), timeout=10.0)
                    print("✓ 会话已初始化")
                except asyncio.TimeoutError:
                    print("✗ 会话初始化超时")
                    return
                except Exception as e:
                    print(f"✗ 会话初始化失败: {str(e)}")
                    return
                
                # List available tools
                print("\n" + "-" * 70)
                print("可用的工具列表:")
                print("-" * 70)
                
                try:
                    tools_response = await asyncio.wait_for(session.list_tools(), timeout=5.0)
                    
                    if hasattr(tools_response, 'tools'):
                        for tool in tools_response.tools:
                            print(f"  - {tool.name}: {tool.description}")
                    else:
                        print("  (无法获取工具列表)")
                except asyncio.TimeoutError:
                    print("  ✗ 获取工具列表超时")
                except Exception as e:
                    print(f"  ✗ 获取工具列表失败: {str(e)}")
                
                # Call idf_version tool
                print("\n" + "-" * 70)
                print("调用 idf_version 工具...")
                print("-" * 70)
                
                try:
                    result = await asyncio.wait_for(session.call_tool("idf_version", {}), timeout=10.0)
                    
                    print("\n✓ 工具调用成功")
                    print(f"\n返回结果:")
                    print(f"  {result}")
                    
                    # Parse the result
                    if hasattr(result, 'content'):
                        for content_item in result.content:
                            if hasattr(content_item, 'text'):
                                print(f"\n  响应文本:")
                                print(f"    {content_item.text}")
                    else:
                        print(f"\n  原始结果: {result}")
                    
                except asyncio.TimeoutError:
                    print("\n✗ 工具调用超时")
                except Exception as e:
                    print(f"\n✗ 工具调用失败: {str(e)}")
                    import traceback
                    traceback.print_exc()
    
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)


async def test_multiple_tools():
    """
    Test multiple tools through MCP client
    
    This demonstrates calling multiple tools in sequence
    """
    
    print("\n" + "=" * 70)
    print("MCP Client - Testing Multiple Tools")
    print("=" * 70)
    
    # Get the path to main.py
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main_py_path = os.path.join(project_root, "main.py")
    
    # Create server parameters
    server_params = StdioServerParameters(
        command="python",
        args=[main_py_path]
    )
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # Test 1: Get IDF version
                print("\n[测试 1] 获取 ESP-IDF 版本")
                print("-" * 70)
                
                try:
                    result = await session.call_tool("idf_version", {})
                    print(f"结果: {result}")
                except Exception as e:
                    print(f"失败: {e}")
                
                # Test 2: List serial ports
                print("\n[测试 2] 列出串口")
                print("-" * 70)
                
                try:
                    result = await session.call_tool("serial_list_ports", {})
                    print(f"结果: {result}")
                except Exception as e:
                    print(f"失败: {e}")
                
                # Test 3: Get logs
                print("\n[测试 3] 获取系统日志")
                print("-" * 70)
                
                try:
                    result = await session.call_tool("logger_get_logs", {"lines": 10})
                    print(f"结果: {result}")
                except Exception as e:
                    print(f"失败: {e}")
    
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Client Example")
    parser.add_argument(
        "--multi",
        action="store_true",
        help="Test multiple tools instead of just idf_version"
    )
    
    args = parser.parse_args()
    
    if args.multi:
        asyncio.run(test_multiple_tools())
    else:
        asyncio.run(test_idf_version())
