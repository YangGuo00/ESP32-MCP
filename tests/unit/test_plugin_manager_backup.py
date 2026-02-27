import sys
import os

grandparent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, grandparent_dir)

print("测试插件管理器加载...")

from src.core.plugin_manager import PluginManager
from src.utils.config_loader import ConfigLoader

config_loader = ConfigLoader()
config_file = os.path.join(grandparent_dir, "config", "config.yaml")
config = config_loader.load(config_file)

print(f"\n插件目录: {os.path.join(os.path.dirname(__file__), 'src', 'plugins')}")
print(f"插件目录存在: {os.path.exists(os.path.join(os.path.dirname(__file__), 'src', 'plugins'))}")

plugin_manager = PluginManager(plugin_dir=os.path.join(os.path.dirname(__file__), "src", "plugins"))

print(f"\n插件管理器插件目录: {plugin_manager.plugin_dir}")
print(f"插件目录存在: {os.path.exists(plugin_manager.plugin_dir)}")

if os.path.exists(plugin_manager.plugin_dir):
    print(f"插件目录内容: {os.listdir(plugin_manager.plugin_dir)}")

loaded_count = plugin_manager.load_plugins(config)
print(f"\n成功加载 {loaded_count} 个插件")
print(f"已加载的插件: {list(plugin_manager.plugins.keys())}")

for name, plugin in plugin_manager.plugins.items():
    print(f"\n插件: {name}")
    print(f"  描述: {plugin.description}")
    print(f"  版本: {plugin.version}")
    tools = plugin.get_tools()
    print(f"  工具数量: {len(tools)}")
