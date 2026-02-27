import os
import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path

from .logger import get_logger


class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.logger = get_logger(__name__)

    def load(self, config_path: str = None) -> Dict[str, Any]:
        """加载配置文件"""
        config_path = config_path or self.config_path

        if not config_path:
            self.logger.warning("未指定配置文件路径")
            return {}

        if not os.path.exists(config_path):
            self.logger.warning(f"配置文件不存在: {config_path}")
            return {}

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    self.config = yaml.safe_load(f) or {}
                elif config_path.endswith('.json'):
                    self.config = json.load(f) or {}
                else:
                    self.logger.error(f"不支持的配置文件格式: {config_path}")
                    return {}

            self.logger.info(f"配置文件加载成功: {config_path}")
            return self.config

        except Exception as e:
            self.logger.error(f"加载配置文件时出错: {str(e)}")
            return {}

    def save(self, config_path: str = None):
        """保存配置文件"""
        config_path = config_path or self.config_path

        if not config_path:
            self.logger.warning("未指定配置文件路径")
            return

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
                elif config_path.endswith('.json'):
                    json.dump(self.config, f, indent=2, ensure_ascii=False)

            self.logger.info(f"配置文件保存成功: {config_path}")

        except Exception as e:
            self.logger.error(f"保存配置文件时出错: {str(e)}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """设置配置项"""
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config.copy()

    def update(self, config: Dict[str, Any]):
        """更新配置"""
        self.config.update(config)


def load_env_config() -> Dict[str, Any]:
    """从环境变量加载配置"""
    config = {}

    esp_idf_path = os.getenv('ESP_IDF_PATH')
    if esp_idf_path:
        config['esp_idf_path'] = esp_idf_path

    log_level = os.getenv('LOG_LEVEL')
    if log_level:
        config['log_level'] = log_level

    return config
