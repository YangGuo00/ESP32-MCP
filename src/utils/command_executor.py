import subprocess
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from .logger import get_logger
from .exceptions import IDFCommandError


class CommandExecutor:
    """命令执行器"""

    def __init__(self, working_dir: str = None):
        self.working_dir = working_dir
        self.logger = get_logger(__name__)

    def execute(
        self,
        command: str,
        args: List[str] = None,
        env: Dict[str, str] = None,
        cwd: str = None,
        timeout: int = None
    ) -> Dict[str, Any]:
        """执行命令"""
        try:
            full_command = [command] + (args or [])
            self.logger.info(f"执行命令: {' '.join(full_command)}")

            process = subprocess.Popen(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd or self.working_dir,
                env=env or os.environ.copy()
            )

            stdout, stderr = process.communicate(timeout=timeout)

            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "command": ' '.join(full_command)
            }

        except subprocess.TimeoutExpired:
            process.kill()
            self.logger.error(f"命令执行超时: {' '.join(full_command)}")
            return {
                "success": False,
                "error": "命令执行超时",
                "command": ' '.join(full_command)
            }

        except Exception as e:
            self.logger.error(f"执行命令时出错: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "command": ' '.join(full_command)
            }

    def execute_async(
        self,
        command: str,
        args: List[str] = None,
        env: Dict[str, str] = None,
        cwd: str = None,
        callback=None
    ) -> subprocess.Popen:
        """异步执行命令"""
        try:
            full_command = [command] + (args or [])
            self.logger.info(f"异步执行命令: {' '.join(full_command)}")

            process = subprocess.Popen(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd or self.working_dir,
                env=env or os.environ.copy(),
                bufsize=1,
                universal_newlines=True
            )

            return process

        except Exception as e:
            self.logger.error(f"异步执行命令时出错: {str(e)}")
            raise IDFCommandError(f"异步执行命令失败: {str(e)}")

    def check_command_exists(self, command: str) -> bool:
        """检查命令是否存在"""
        try:
            result = subprocess.run(
                ["where", command] if os.name == 'nt' else ["which", command],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def execute_cmd(self, cmd: str, cwd: str = None, timeout: int = None) -> Dict[str, Any]:
        """执行完整的命令字符串"""
        try:
            self.logger.info(f"执行命令: {cmd}")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd or self.working_dir,
                shell=True
            )

            stdout, stderr = process.communicate(timeout=timeout)

            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "command": cmd
            }

        except subprocess.TimeoutExpired:
            process.kill()
            self.logger.error(f"命令执行超时: {cmd}")
            return {
                "success": False,
                "error": "命令执行超时",
                "command": cmd
            }

        except Exception as e:
            self.logger.error(f"执行命令时出错: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "command": cmd
            }
