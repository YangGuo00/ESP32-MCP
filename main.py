import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.server import MCPServer
from src.utils.config_loader import ConfigLoader, load_env_config
from src.utils.logger import get_logger, set_log_level


async def main():
    """主函数"""
    config_loader = ConfigLoader()

    config_file = os.path.join(os.path.dirname(__file__), "config", "config.yaml")
    config = config_loader.load(config_file)

    env_config = load_env_config()
    config.update(env_config)

    log_level = config.get("log_level", "INFO")
    set_log_level(log_level)

    logger = get_logger(__name__)
    logger.info("ESP32-MCP 服务器启动中...")

    server = MCPServer(config)

    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("接收到中断信号")
    except Exception as e:
        logger.error(f"服务器运行时出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
