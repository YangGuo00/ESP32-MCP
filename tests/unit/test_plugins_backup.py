import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("测试插件导入...")

try:
    print("\n1. 导入 SerialPlugin...")
    from src.plugins.serial.plugin import SerialPlugin
    print(f"   ✓ SerialPlugin 类: {SerialPlugin}")
    plugin = SerialPlugin()
    print(f"   ✓ 实例化成功: {plugin.name}")
    result = plugin.initialize({})
    print(f"   ✓ 初始化结果: {result}")
    tools = plugin.get_tools()
    print(f"   ✓ 工具数量: {len(tools)}")
    for tool in tools:
        print(f"      - {tool['name']}")
except Exception as e:
    print(f"   ✗ 错误: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n2. 导入 LoggerPlugin...")
    from src.plugins.logger.plugin import LoggerPlugin
    print(f"   ✓ LoggerPlugin 类: {LoggerPlugin}")
    plugin = LoggerPlugin()
    print(f"   ✓ 实例化成功: {plugin.name}")
    result = plugin.initialize({})
    print(f"   ✓ 初始化结果: {result}")
    tools = plugin.get_tools()
    print(f"   ✓ 工具数量: {len(tools)}")
    for tool in tools:
        print(f"      - {tool['name']}")
except Exception as e:
    print(f"   ✗ 错误: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n3. 导入 MonitorPlugin...")
    from src.plugins.monitor.plugin import MonitorPlugin
    print(f"   ✓ MonitorPlugin 类: {MonitorPlugin}")
    plugin = MonitorPlugin()
    print(f"   ✓ 实例化成功: {plugin.name}")
    result = plugin.initialize({})
    print(f"   ✓ 初始化结果: {result}")
    tools = plugin.get_tools()
    print(f"   ✓ 工具数量: {len(tools)}")
    for tool in tools:
        print(f"      - {tool['name']}")
except Exception as e:
    print(f"   ✗ 错误: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n4. 导入 BuildPlugin...")
    from src.plugins.build.plugin import BuildPlugin
    print(f"   ✓ BuildPlugin 类: {BuildPlugin}")
    plugin = BuildPlugin()
    print(f"   ✓ 实例化成功: {plugin.name}")
    result = plugin.initialize({})
    print(f"   ✓ 初始化结果: {result}")
    tools = plugin.get_tools()
    print(f"   ✓ 工具数量: {len(tools)}")
    for tool in tools:
        print(f"      - {tool['name']}")
except Exception as e:
    print(f"   ✗ 错误: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n5. 导入 IDFPlugin...")
    from src.plugins.idf.plugin import IDFPlugin
    print(f"   ✓ IDFPlugin 类: {IDFPlugin}")
    plugin = IDFPlugin()
    print(f"   ✓ 实例化成功: {plugin.name}")
    result = plugin.initialize({})
    print(f"   ✓ 初始化结果: {result}")
    tools = plugin.get_tools()
    print(f"   ✓ 工具数量: {len(tools)}")
    for tool in tools:
        print(f"      - {tool['name']}")
except Exception as e:
    print(f"   ✗ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("插件导入测试完成！")
print("=" * 60)
