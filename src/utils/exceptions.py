class ESP32MCPError(Exception):
    """ESP32-MCP 基础异常"""
    pass


class PluginError(ESP32MCPError):
    """插件异常"""
    pass


class PluginLoadError(PluginError):
    """插件加载异常"""
    pass


class PluginInitError(PluginError):
    """插件初始化异常"""
    pass


class PluginExecuteError(PluginError):
    """插件执行异常"""
    pass


class IDFError(ESP32MCPError):
    """IDF 相关异常"""
    pass


class IDFCommandError(IDFError):
    """IDF 命令执行异常"""
    pass


class IDFBuildError(IDFError):
    """IDF 编译异常"""
    pass


class IDFFlashError(IDFError):
    """IDF 烧录异常"""
    pass


class SerialError(ESP32MCPError):
    """串口相关异常"""
    pass


class SerialConnectionError(SerialError):
    """串口连接异常"""
    pass


class SerialReadError(SerialError):
    """串口读取异常"""
    pass


class SerialWriteError(SerialError):
    """串口写入异常"""
    pass


class ConfigError(ESP32MCPError):
    """配置相关异常"""
    pass


class ConfigLoadError(ConfigError):
    """配置加载异常"""
    pass


class ConfigValidationError(ConfigError):
    """配置验证异常"""
    pass


class ProtocolError(ESP32MCPError):
    """协议相关异常"""
    pass


class MessageParseError(ProtocolError):
    """消息解析异常"""
    pass


class MessageHandleError(ProtocolError):
    """消息处理异常"""
    pass
