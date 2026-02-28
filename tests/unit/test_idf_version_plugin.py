import asyncio
import sys
import os

grandparent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, grandparent_dir)

from src.plugins.idf.plugin import IDFPlugin
from src.utils.config_loader import ConfigLoader, load_env_config


async def test_idf_version():
    """测试获取 IDF 版本功能"""
    print("\n" + "=" * 60)
    print("测试 IDF 版本获取功能")
    print("=" * 60)

    try:
        config_loader = ConfigLoader()
        config_file = os.path.join(grandparent_dir, "config", "config.yaml")
        config = config_loader.load(config_file)

        env_config = load_env_config()
        config.update(env_config)

        idf_config = config.get("plugins", {}).get("idf", {})
        
        idf_plugin = IDFPlugin()
        idf_plugin.initialize(idf_config)

        print("\n检查 ESP-IDF 路径...")
        if idf_plugin.esp_idf_path:
            print(f"✓ ESP-IDF 路径: {idf_plugin.esp_idf_path}")
        else:
            print("✗ ESP-IDF 路径未配置")
            return

        print("\n获取 ESP-IDF 版本...")
        result = idf_plugin.execute_tool("idf.version", {})

        if result.get("success"):
            print(f"✓ 获取成功")
            print(f"  版本: {result.get('version', 'Unknown')}")
            print(f"  消息: {result.get('message', '')}")
        else:
            print(f"✗ 获取失败")
            print(f"  错误: {result.get('error', '未知错误')}")
            if result.get('output'):
                print(f"  输出: {result.get('output')}")

        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_idf_version())
