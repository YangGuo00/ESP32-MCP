"""
ESP32-MCP FastMCP 服务器

使用 FastMCP 框架暴露 IDF 函数接口
"""

from fastmcp import FastMCP
import os
from pathlib import Path
from src.utils.config_loader import ConfigLoader, load_env_config
from tests.unit.idfTest import IDFController


# 创建 FastMCP 实例
mcp = FastMCP("ESP32-MCP Server")


# 全局 IDF 控制器实例
idf_controller = None


@mcp.tool()
def initialize(idf_path: str = None, project_path: str = None) -> str:
    """初始化 ESP-IDF 环境
    
    Args:
        idf_path: ESP-IDF 安装路径（可选，默认从配置文件读取）
        project_path: ESP32 项目路径（可选）
    
    Returns:
        初始化结果
    """
    global idf_controller
    
    try:
        print(f"[initialize] 开始初始化 IDF 环境...")
        
        # 加载配置
        config_loader = ConfigLoader()
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "config.yaml")
        config = config_loader.load(config_file)
        env_config = load_env_config()
        config.update(env_config)
        
        # 获取 IDF 配置
        idf_config = config.get("plugins", {}).get("idf", {})
        
        # 使用传入的参数覆盖配置
        if idf_path:
            idf_config["esp_idf_path"] = idf_path
        else:
            idf_path = idf_config.get("esp_idf_path")
        
        if project_path:
            idf_config["project_path"] = project_path
        else:
            project_path = idf_config.get("project_path", ".")
        
        print(f"[initialize] ESP-IDF 路径: {idf_path}")
        print(f"[initialize] 项目路径: {project_path}")
        
        # 创建 IDF 控制器
        print(f"[initialize] 创建 IDF 控制器...")
        idf_controller = IDFController(idf_path, project_path)
        
        # 初始化 IDF 环境
        print(f"[initialize] 初始化 IDF 环境...")
        result = idf_controller.initialize()
        
        if not result.success:
            print(f"[initialize] 初始化失败: {result.stderr}")
            return f"初始化失败: {result.stderr}"
        
        print(f"[initialize] IDF 环境初始化成功")
        return "IDF 环境初始化成功"
        
    except Exception as e:
        print(f"[initialize] 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return f"初始化失败: {str(e)}"


@mcp.tool()
def get_version() -> str:
    """获取 ESP-IDF 版本号"""
    global idf_controller
    
    if not idf_controller:
        return "IDF 控制器未初始化，请先调用 initialize()"
    
    print(f"[get_version] 开始获取版本...")
    result = idf_controller.get_version()
    
    if result.success:
        print(f"[get_version] 获取成功")
        return result.stdout
    else:
        print(f"[get_version] 获取失败: {result.stderr}")
        return f"获取失败: {result.stderr}"


@mcp.tool()
def set_target(target: str, project_path: str = None) -> str:
    """设置目标芯片
    
    Args:
        target: 目标芯片型号（如 esp32, esp32s3 等）
        project_path: ESP32 项目路径（可选）
    
    Returns:
        设置结果
    """
    global idf_controller
    
    if not idf_controller:
        return "IDF 控制器未初始化，请先调用 initialize()"
    
    print(f"[set_target] 开始设置目标芯片: {target}, 项目路径: {project_path}")
    result = idf_controller.set_target(target, project_path)
    
    if result.success:
        print(f"[set_target] 设置成功")
        return result.stdout
    else:
        print(f"[set_target] 设置失败")
        print(f"[set_target] 错误代码: {result.code}")
        print(f"[set_target] 错误信息: {result.stderr}")
        print(f"[set_target] 原始输出: {result.stdout[:1000] if result.stdout else '(无输出)'}")
        return f"设置失败\n错误信息: {result.stderr}\n原始输出: {result.stdout[:2000] if result.stdout else '(无输出)'}"


@mcp.tool()
def build(project_path: str, target: str = None) -> str:
    """编译项目
    
    Args:
        project_path: ESP32 项目路径
        target: 目标芯片型号（可选）
    
    Returns:
        编译结果
    """
    global idf_controller
    
    if not idf_controller:
        return "IDF 控制器未初始化，请先调用 initialize()"
    
    print(f"[build] 开始编译项目: {project_path}, 目标芯片: {target}")
    
    # 如果指定了目标芯片，先设置目标
    if target:
        print(f"[build] 先设置目标芯片: {target}")
        set_result = idf_controller.set_target(target, project_path)
        if not set_result.success:
            print(f"[build] 设置目标芯片失败")
            return f"设置目标芯片失败\n{set_result.stderr}"
    
    # 执行编译
    result = idf_controller.build(project_path)
    
    if result.success:
        print(f"[build] 编译成功")
        return result.stdout
    else:
        print(f"[build] 编译失败")
        print(f"[build] 错误代码: {result.code}")
        print(f"[build] 错误信息: {result.stderr}")
        print(f"[build] 原始输出: {result.stdout[:1000] if result.stdout else '(无输出)'}")
        return f"编译失败\n错误信息: {result.stderr}\n原始输出: {result.stdout[:2000] if result.stdout else '(无输出)'}"


@mcp.tool()
def flash(project_path: str, port: str = None, baud: int = 460800) -> str:
    """烧录固件
    
    Args:
        project_path: ESP32 项目路径
        port: 串口端口（可选）
        baud: 波特率（默认 460800）
    
    Returns:
        烧录结果
    """
    global idf_controller
    
    if not idf_controller:
        return "IDF 控制器未初始化，请先调用 initialize()"
    
    print(f"[flash] 开始烧录固件: {project_path}, 端口: {port}, 波特率: {baud}")
    result = idf_controller.flash(project_path, port, baud)
    
    if result.success:
        print(f"[flash] 烧录成功")
        return result.stdout
    else:
        print(f"[flash] 烧录失败: {result.stderr}")
        return f"烧录失败\n{result.stderr}"


@mcp.tool()
def erase_flash(project_path: str, port: str = None) -> str:
    """擦除 Flash
    
    Args:
        project_path: ESP32 项目路径
        port: 串口端口（可选）
    
    Returns:
        擦除结果
    """
    global idf_controller
    
    if not idf_controller:
        return "IDF 控制器未初始化，请先调用 initialize()"
    
    print(f"[erase_flash] 开始擦除 Flash: {project_path}, 端口: {port}")
    result = idf_controller.erase_flash(project_path, port)
    
    if result.success:
        print(f"[erase_flash] 擦除成功")
        return result.stdout
    else:
        print(f"[erase_flash] 擦除失败: {result.stderr}")
        return f"擦除失败\n{result.stderr}"


@mcp.tool()
def monitor(project_path: str, port: str = None) -> str:
    """打开监视器
    
    Args:
        project_path: ESP32 项目路径
        port: 串口端口（可选）
    
    Returns:
        监视器启动结果
    """
    global idf_controller
    
    if not idf_controller:
        return "IDF 控制器未初始化，请先调用 initialize()"
    
    print(f"[monitor] 开始打开监视器: {project_path}, 端口: {port}")
    result = idf_controller.monitor(project_path, port)
    
    if result.success:
        print(f"[monitor] 监视器启动成功")
        return result.stdout
    else:
        print(f"[monitor] 监视器启动失败: {result.stderr}")
        return f"监视器启动失败\n{result.stderr}"


@mcp.tool()
def menuconfig(project_path: str) -> str:
    """打开配置菜单
    
    Args:
        project_path: ESP32 项目路径
    
    Returns:
        配置菜单启动结果
    """
    global idf_controller
    
    if not idf_controller:
        return "IDF 控制器未初始化，请先调用 initialize()"
    
    print(f"[menuconfig] 开始打开配置菜单: {project_path}")
    result = idf_controller.menuconfig(project_path)
    
    if result.success:
        print(f"[menuconfig] 配置菜单启动成功")
        return result.stdout
    else:
        print(f"[menuconfig] 配置菜单启动失败: {result.stderr}")
        return f"配置菜单启动失败\n{result.stderr}"


@mcp.tool()
def fullclean(project_path: str) -> str:
    """
    清理 ESP32 项目的构建文件
    
    Args:
        project_path: ESP32 项目路径
    
    Returns:
        清理结果
    """
    global idf_controller
    
    if not idf_controller:
        return "IDF 控制器未初始化，请先调用 initialize()"
    
    print(f"[fullclean] 开始清理项目: {project_path}")
    result = idf_controller.fullclean(project_path)
    
    if result.success:
        print(f"[fullclean] 清理成功")
        return result.stdout
    else:
        print(f"[fullclean] 清理失败")
        print(f"[fullclean] 错误代码: {result.code}")
        print(f"[fullclean] 错误信息: {result.stderr}")
        print(f"[fullclean] 原始输出: {result.stdout[:500] if result.stdout else '(无输出)'}")
        return f"清理失败\n错误信息: {result.stderr}\n原始输出: {result.stdout[:1000] if result.stdout else '(无输出)'}"


if __name__ == "__main__":
    print("=" * 60)
    print("ESP32-MCP FastMCP 服务器")
    print("=" * 60)
    print("服务器已启动，等待 MCP 客户端连接...")
    print("可用工具:")
    print("  - initialize(idf_path, project_path): 初始化 ESP-IDF 环境")
    print("  - get_version(): 获取 ESP-IDF 版本号")
    print("  - set_target(target, project_path): 设置目标芯片")
    print("  - build(project_path, target): 编译项目")
    print("  - flash(project_path, port, baud): 烧录固件")
    print("  - erase_flash(project_path, port): 擦除 Flash")
    print("  - monitor(project_path, port): 打开监视器")
    print("  - menuconfig(project_path): 打开配置菜单")
    print("  - fullclean(project_path): 清理项目")
    print("=" * 60)
    
    # 测试代码
    print("\n" + "=" * 60)
    print("开始测试...")
    print("=" * 60)
    
    # 测试代码
    print("\n" + "=" * 60)
    print("开始测试...")
    print("=" * 60)
    
    # 测试项目路径
    test_project = r"E:\Desktop\embedded\ESP32\ESP32Pro\helloESP32"
    
    # 1. 初始化 IDF 环境
    print("\n[测试 1] 初始化 IDF 环境...")
    init_result = initialize(
        idf_path="D:/esp32/Espressif/frameworks/esp-idf-v5.3.3",
        project_path="."
    )
    print(f"初始化结果: {init_result}")
    
    if "成功" in init_result:
        # 2. 获取版本
        print("\n[测试 2] 获取 ESP-IDF 版本...")
        version_result = get_version()
        print(f"版本信息:\n{version_result}")
        
        # 3. 运行 fullclean
        print("\n[测试 3] 运行 fullclean...")
        clean_result = fullclean(test_project)
        print(f"清理结果:\n{clean_result}")
        
        # 4. 设置目标芯片
        print("\n[测试 4] 设置目标芯片...")
        target_result = set_target(target="esp32s3", project_path=test_project)
        print(f"设置结果:\n{target_result}")
        
        # 5. 编译项目
        print("\n[测试 5] 编译项目...")
        build_result = build(project_path=test_project, target="esp32s3")
        print(f"编译结果:\n{build_result}")
        
        # 6. 打开配置菜单
        print("\n[测试 6] 打开配置菜单...")
        menu_result = menuconfig(project_path=test_project)
        print(f"配置菜单结果:\n{menu_result}")
    else:
        print("\n初始化失败，跳过后续测试")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    # 启动 MCP 服务器（注释掉，避免阻塞）
    # mcp.run(transport="stdio")
