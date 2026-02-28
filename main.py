"""
Main entry point for the ESP32-MCP Server using FastMCP.
Acts as the central controller for the MCP server that handles ESP32 operations.
Supports multiple transports: stdio, sse, and streamable-http using standalone FastMCP.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
print("Loading configuration from .env file...")
load_dotenv()
# Set required environment variable for FastMCP 2.8.1+
os.environ.setdefault('FASTMCP_LOG_LEVEL', 'INFO')

from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from src.plugins.idf.plugin import IDFPlugin
from src.plugins.serial.plugin import SerialPlugin
from src.plugins.monitor.plugin import MonitorPlugin
from src.plugins.logger.plugin import LoggerPlugin
from src.utils.config_loader import ConfigLoader, load_env_config
from src.utils.logger import get_logger, set_log_level

# Load configuration
config_loader = ConfigLoader()
config_file = os.path.join(os.path.dirname(__file__), "config", "config.yaml")
config = config_loader.load(config_file)
env_config = load_env_config()
config.update(env_config)

# Set log level
log_level = config.get("log_level", "INFO")
set_log_level(log_level)
logger = get_logger(__name__)

# Initialize plugins
idf_plugin = IDFPlugin()
serial_plugin = SerialPlugin()
monitor_plugin = MonitorPlugin()
logger_plugin = LoggerPlugin()

# Initialize plugins with config
idf_plugin.initialize(config.get("plugins", {}).get("idf", {}))
serial_plugin.initialize(config.get("plugins", {}).get("serial", {}))
monitor_plugin.initialize(config.get("plugins", {}).get("monitor", {}))
logger_plugin.initialize(config.get("plugins", {}).get("logger", {}))

# Initialize FastMCP server
mcp = FastMCP("ESP32-MCP Server")

# Register IDF tools
@mcp.tool(
    annotations=ToolAnnotations(
        title="Build ESP32 Project",
        description="Compile ESP32 project using idf.py build",
    ),
)
def idf_build(target: str = None):
    """Compile ESP32 project."""
    arguments = {}
    if target:
        arguments["target"] = target
    return idf_plugin.execute_tool("idf.build", arguments)

@mcp.tool(
    annotations=ToolAnnotations(
        title="Flash ESP32",
        description="Flash firmware to ESP32 device",
    ),
)
def idf_flash(port: str = None, baud: int = 460800):
    """Flash firmware to ESP32."""
    arguments = {}
    if port:
        arguments["port"] = port
    arguments["baud"] = baud
    return idf_plugin.execute_tool("idf.flash", arguments)

@mcp.tool(
    annotations=ToolAnnotations(
        title="Erase ESP32 Flash",
        description="Erase ESP32 Flash memory",
    ),
)
def idf_erase_flash(port: str = None):
    """Erase ESP32 Flash."""
    arguments = {}
    if port:
        arguments["port"] = port
    return idf_plugin.execute_tool("idf.erase_flash", arguments)

@mcp.tool(
    annotations=ToolAnnotations(
        title="Monitor ESP32 Serial",
        description="Open serial monitor for ESP32",
    ),
)
def idf_monitor(port: str = None):
    """Open serial monitor for ESP32."""
    arguments = {}
    if port:
        arguments["port"] = port
    return idf_plugin.execute_tool("idf.monitor", arguments)

@mcp.tool(
    annotations=ToolAnnotations(
        title="Open ESP32 Menuconfig",
        description="Open project configuration menu",
    ),
)
def idf_menuconfig():
    """Open project configuration menu."""
    return idf_plugin.execute_tool("idf.menuconfig", {})

@mcp.tool(
    annotations=ToolAnnotations(
        title="Clean ESP32 Project",
        description="Clean ESP32 project build files",
    ),
)
def idf_fullclean():
    """Clean ESP32 project build files."""
    return idf_plugin.execute_tool("idf.fullclean", {})

@mcp.tool(
    annotations=ToolAnnotations(
        title="Set ESP32 Target",
        description="Set target chip for ESP32 project",
    ),
)
def idf_set_target(target: str):
    """Set target chip for ESP32 project."""
    return idf_plugin.execute_tool("idf.set_target", {"target": target})

@mcp.tool(
    annotations=ToolAnnotations(
        title="Get ESP-IDF Version",
        description="Get ESP-IDF version number",
    ),
)
def idf_version():
    """
    Get ESP-IDF version number.
    
    Returns:
        dict: A dictionary containing the version information or error message.
    """
    try:
        result = idf_plugin.execute_tool("idf.version", {})
        if result.get("success"):
            version = result.get("version", "Unknown version")
            return {
                "success": True,
                "message": result.get("message", f"ESP-IDF version: {version}"),
                "version": version,
                "output": result.get("output", "")
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Failed to get ESP-IDF version"),
                "output": result.get("output", "")
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting ESP-IDF version: {str(e)}"
        }

# Register Serial tools
@mcp.tool(
    annotations=ToolAnnotations(
        title="List Serial Ports",
        description="List available serial ports",
    ),
)
def serial_list_ports():
    """List available serial ports."""
    return serial_plugin.execute_tool("serial.list_ports", {})

@mcp.tool(
    annotations=ToolAnnotations(
        title="Open Serial Port",
        description="Open serial port for communication",
    ),
)
def serial_open(port: str, baud: int = 115200):
    """Open serial port for communication."""
    return serial_plugin.execute_tool("serial.open", {"port": port, "baud": baud})

@mcp.tool(
    annotations=ToolAnnotations(
        title="Close Serial Port",
        description="Close serial port",
    ),
)
def serial_close(port: str):
    """Close serial port."""
    return serial_plugin.execute_tool("serial.close", {"port": port})

@mcp.tool(
    annotations=ToolAnnotations(
        title="Read Serial Data",
        description="Read data from serial port",
    ),
)
def serial_read(port: str, bytes: int = 1024):
    """Read data from serial port."""
    return serial_plugin.execute_tool("serial.read", {"port": port, "bytes": bytes})

@mcp.tool(
    annotations=ToolAnnotations(
        title="Write Serial Data",
        description="Write data to serial port",
    ),
)
def serial_write(port: str, data: str):
    """Write data to serial port."""
    return serial_plugin.execute_tool("serial.write", {"port": port, "data": data})

# Register Monitor tools
@mcp.tool(
    annotations=ToolAnnotations(
        title="Start Monitoring",
        description="Start monitoring ESP32 data",
    ),
)
def monitor_start():
    """Start monitoring ESP32 data."""
    return monitor_plugin.execute_tool("monitor.start", {})

@mcp.tool(
    annotations=ToolAnnotations(
        title="Stop Monitoring",
        description="Stop monitoring ESP32 data",
    ),
)
def monitor_stop():
    """Stop monitoring ESP32 data."""
    return monitor_plugin.execute_tool("monitor.stop", {})

@mcp.tool(
    annotations=ToolAnnotations(
        title="Get Monitoring Data",
        description="Get monitoring data",
    ),
)
def monitor_get_data():
    """Get monitoring data."""
    return monitor_plugin.execute_tool("monitor.get_data", {})

# Register Logger tools
@mcp.tool(
    annotations=ToolAnnotations(
        title="Get Logs",
        description="Get system logs",
    ),
)
def logger_get_logs(lines: int = 100):
    """Get system logs."""
    return logger_plugin.execute_tool("logger.get_logs", {"lines": lines})

@mcp.tool(
    annotations=ToolAnnotations(
        title="Clear Logs",
        description="Clear system logs",
    ),
)
def logger_clear_logs():
    """Clear system logs."""
    return logger_plugin.execute_tool("logger.clear_logs", {})

def get_transport_config():
    """
    Get transport configuration from environment variables.
    
    Returns:
        dict: Transport configuration with type, host, port, and other settings
    """
    # Default configuration
    config = {
        'transport': 'stdio',  # Default to stdio for backward compatibility
        'host': '0.0.0.0',
        'port': 8000,
        'path': '/mcp',
        'sse_path': '/sse'
    }
    
    # Override with environment variables if provided
    transport = os.getenv('MCP_TRANSPORT', 'stdio').lower()
    print(f"Transport: {transport}")
    # Validate transport type
    valid_transports = ['stdio', 'streamable-http', 'sse']
    if transport not in valid_transports:
        print(f"Warning: Invalid transport '{transport}'. Falling back to 'stdio'.")
        transport = 'stdio'
    
    config['transport'] = transport
    config['host'] = os.getenv('MCP_HOST', config['host'])
    # Use PORT from Render if available, otherwise fall back to MCP_PORT or default
    config['port'] = int(os.getenv('PORT', os.getenv('MCP_PORT', config['port'])))
    config['path'] = os.getenv('MCP_PATH', config['path'])
    config['sse_path'] = os.getenv('MCP_SSE_PATH', config['sse_path'])
    
    return config

if __name__ == "__main__":
    logger.info("ESP32-MCP FastMCP Server starting...")
    
    # Get transport configuration
    transport_config = get_transport_config()
    
    # Run the server
    if transport_config['transport'] == 'stdio':
        mcp.run(transport="stdio")
    else:
        mcp.run(
            transport=transport_config['transport'],
            host=transport_config['host'],
            port=transport_config['port'],
            path=transport_config['path'],
            sse_path=transport_config['sse_path']
        )
