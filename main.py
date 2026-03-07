"""
ESP32-MCP FastMCP 服务器

使用 FastMCP 框架暴露 IDF 函数接口
"""

from fastmcp import FastMCP
from src.plugins.idf.plugin import IDFPlugin
import os
from pathlib import Path
from src.utils.config_loader import ConfigLoader, load_env_config


# 创建 FastMCP 实例
mcp = FastMCP("ESP32-MCP Server")


# 全局 IDF 控制器实例
idf_controller = None


@mcp.tool()
def get_version() -> str:
    """获取 ESP-IDF 版本号"""
    global idf_controller
    
    if not idf_controller:
        return "IDF 控制器未初始化，请先调用 initialize()"
    
    result = idf_controller.get_version()
    return result.stdout if result.success else f"获取失败: {result.stderr}"


@mcp.tool()
def set_target(target: str, project_path: str = None) -> str:
    """设置目标芯片"""
    global idf_controller
    
    if not idf_controller:
        return "IDF 控制器未初始化，请先调用 initialize()"
    
    result = idf_controller.set_target(target, project_path)
    return result.stdout if result.success else f"设置失败\n{result.stderr}"


@mcp.tool()
def build(project_path: str, target: str = None) -> str:
    """编译项目"""
    global idf_controller
    
    if not idf_controller:
        return "IDF 控制器未初始化，请先调用 initialize()"
    
    result = idf_controller.build(project_path, target)
    return result.stdout if result.success else f"编译失败\n{result.stderr}"


@mcp.tool()
def flash(project_path: str, port: str = None, baud: int = 460800) -> str:
    """烧录固件"""
    global idf_controller
    
    if not idf_controller:
        return "IDF 控制器未初始化，请先调用 initialize()"
    
    result = idf_controller.flash(project_path, port, baud)
    return result.stdout if result.success else f"烧录失败\n{result.stderr}"


@mcp.tool()
def erase_flash(project_path: str, port: str = None) -> str:
    """擦除 Flash"""
    global idf_controller
    
    if not idf_controller:
        return "IDF 控制器未初始化，请先调用 initialize()"
    
    result = idf_controller.erase_flash(project_path, port)
    return result.stdout if result.success else f"擦除失败\n{result.stderr}"


@mcp.tool()
def monitor(project_path: str, port: str = None) -> str:
    """打开监视器"""
    global idf_controller
    
    if not idf_controller:
        return "IDF 控制器未初始化，请先调用 initialize()"
    
    result = idf_controller.monitor(project_path, port)
    return result.stdout if result.success else f"监视器启动失败\n{result.stderr}"


@mcp.tool()
def menuconfig(project_path: str) -> str:
    """打开配置菜单"""
    global idf_controller
    
    if not idf_controller:
        return "IDF 控制器未初始化，请先调用 initialize()"
    
    result = idf_controller.menuconfig(project_path)
    return result.stdout if result.success else f"配置菜单启动失败\n{result.stderr}"


@mcp.tool()
def fullclean(project_path: str) -> str:
    """清理项目"""
    global idf_controller
    
    if not idf_controller:
        return "IDF 控制器未初始化，请先调用 initialize()"
    
    result = idf_controller.fullclean(project_path)
    return result.stdout if result.success else f"清理失败\n{result.stderr}"


if __name__ == "__main__":    
    idf_controller = IDFPlugin()
    
    config_loader = ConfigLoader()
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "config.yaml")
    config = config_loader.load(config_file)
    env_config = load_env_config()
    config.update(env_config)
    
    idf_config = config.get("plugins", {}).get("idf", {})
    idf_controller.initialize(idf_config)
    
    # print(idf_controller._version({}))

    # print(idf_controller._fullclean({"project_path": "E:/Desktop/embedded/ESP32/ESP32Pro/01-GPIO"}))

    # mcp.run(transport="stdio")
