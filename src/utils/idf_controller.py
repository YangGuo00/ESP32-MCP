"""
IDF Controller - 持久化的 IDF 命令控制器

这个模块实现了一个持久化的 Python 进程来管理 IDF 工具，
避免每次都运行 export.bat 来初始化环境。
"""

import os
import sys
import json
import subprocess
import threading
import queue
from typing import Dict, Any, Optional


class IDFController:
    """IDF 控制器 - 持久化进程管理 IDF 命令"""
    
    def __init__(self, esp_idf_path: str):
        """
        初始化 IDF 控制器
        
        Args:
            esp_idf_path: ESP-IDF 安装路径
        """
        self.esp_idf_path = esp_idf_path
        self.process: Optional[subprocess.Popen] = None
        self.request_queue: queue.Queue = queue.Queue()
        self.response_queue: queue.Queue = queue.Queue()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
    def start(self):
        """启动 IDF 控制器"""
        if self.running:
            return
        
        self.running = True
        
        # 创建控制器脚本
        controller_script = self._create_controller_script()
        
        # 启动持久化进程
        self.process = subprocess.Popen(
            [sys.executable, controller_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # 启动读取线程
        self.thread = threading.Thread(target=self._read_output, daemon=True)
        self.thread.start()
        
        # 启动请求处理线程
        request_thread = threading.Thread(target=self._process_requests, daemon=True)
        request_thread.start()
    
    def stop(self):
        """停止 IDF 控制器"""
        if not self.running:
            return
        
        self.running = False
        
        # 发送停止命令
        self._send_command("EXIT")
        
        # 等待进程结束
        if self.process:
            self.process.wait(timeout=5)
        
        print("[IDFController] 已停止")
    
    def execute(self, command: str, args: list = None, cwd: str = None, timeout: int = 600) -> Dict[str, Any]:
        """
        执行 IDF 命令
        
        Args:
            command: IDF 命令（如 build, flash, monitor）
            args: 命令参数
            cwd: 工作目录
            timeout: 超时时间（秒）
        
        Returns:
            命令执行结果
        """
        if not self.running:
            return {
                "success": False,
                "error": "idf_controller: IDF 控制器未启动"
            }
        
        # 构建请求
        request = {
            "command": command,
            "args": args or [],
            "cwd": cwd,
            "timeout": timeout
        }
        
        # 发送请求
        self.request_queue.put(request)
        
        # 等待响应（带超时）
        try:
            response = self.response_queue.get(timeout=timeout)
            return response
        except queue.Empty:
            return {
                "success": False,
                "error": f"命令执行超时({timeout}秒)"
            }
    
    def _create_controller_script(self) -> str:
        """创建控制器脚本"""
        script = '''import os
import sys
import json
import queue
import threading
from typing import Dict, Any

# ESP-IDF 路径
ESP_IDF_PATH = r"''' + self.esp_idf_path + '''"

# 请求队列
request_queue = queue.Queue()
response_queue = queue.Queue()

def main():
    while True:
        try:
            # 从 stdin 读取请求
            line = sys.stdin.readline()
            if not line:
                break
            
            try:
                request = json.loads(line.strip())
                
                # 执行命令
                result = execute_command(request)
                
                # 返回结果（JSON 格式）
                print(json.dumps(result, ensure_ascii=False))
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                error = {"success": False, "error": "JSON 解析错误: " + str(e)}
                print(json.dumps(error, ensure_ascii=False))
                sys.stdout.flush()
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            error = {"success": False, "error": "控制器错误: " + str(e)}
            print(json.dumps(error, ensure_ascii=False))
            sys.stdout.flush()

def execute_command(request: Dict[str, Any]) -> Dict[str, Any]:
    """执行 IDF 命令"""
    command = request.get("command")
    args = request.get("args", [])
    cwd = request.get("cwd")
    timeout = request.get("timeout", 60)
    
    try:
        # 切换到工作目录
        if cwd:
            os.chdir(cwd)
        
        # 构建命令
        if command == "version":
            import subprocess
            idf_py = os.path.join(ESP_IDF_PATH, "tools", "idf.py")
            result = subprocess.run(
                [sys.executable, idf_py, "--version"],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            version = result.stdout.strip()
            return {
                "success": True,
                "version": version,
                "output": result.stdout
            }
        
        elif command == "set-target":
            idf_py = os.path.join(ESP_IDF_PATH, "tools", "idf.py")
            target = args[0] if args else "esp32"
            result = subprocess.run(
                [sys.executable, idf_py, "set-target", target],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "stderr": result.stderr
            }
        
        elif command == "build":
            idf_py = os.path.join(ESP_IDF_PATH, "tools", "idf.py")
            build_args = ["build"]
            if args:
                build_args.extend(args)
            
            result = subprocess.run(
                [sys.executable, idf_py] + build_args,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "stderr": result.stderr
            }
        
        elif command == "flash":
            idf_py = os.path.join(ESP_IDF_PATH, "tools", "idf.py")
            flash_args = ["flash"]
            if args:
                flash_args.extend(args)
            
            result = subprocess.run(
                [sys.executable, idf_py] + flash_args,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "stderr": result.stderr
            }
        
        elif command == "monitor":
            idf_py = os.path.join(ESP_IDF_PATH, "tools", "idf.py")
            monitor_args = ["monitor"]
            if args:
                monitor_args.extend(args)
            
            # monitor 是交互式命令，需要特殊处理
            result = subprocess.Popen(
                [sys.executable, idf_py] + monitor_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 读取初始输出
            initial_output = []
            for _ in range(10):
                line = result.stdout.readline()
                if line:
                    initial_output.append(line)
                else:
                    break
            
            return {
                "success": True,
                "output": "\\n".join(initial_output),
                "monitor_pid": result.pid
            }
        
        elif command == "fullclean":
            idf_py = os.path.join(ESP_IDF_PATH, "tools", "idf.py")
            result = subprocess.run(
                [sys.executable, idf_py, "fullclean"],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "stderr": result.stderr
            }
        
        elif command == "erase-flash":
            idf_py = os.path.join(ESP_IDF_PATH, "tools", "idf.py")
            erase_args = ["erase-flash"]
            if args:
                erase_args.extend(args)
            
            result = subprocess.run(
                [sys.executable, idf_py] + erase_args,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "stderr": result.stderr
            }
        
        elif command == "menuconfig":
            idf_py = os.path.join(ESP_IDF_PATH, "tools", "idf.py")
            result = subprocess.run(
                [sys.executable, idf_py, "menuconfig"],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "stderr": result.stderr
            }
        
        else:
            return {
                "success": False,
                "error": "未知命令: " + command
            }

if __name__ == "__main__":
    main()
'''
        
        # 保存到临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(script)
            return f.name
    
    def _read_output(self):
        """读取控制器的输出"""
        while self.running:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break
                
                # 解析响应（JSON 格式）
                try:
                    response = json.loads(line.strip())
                    self.response_queue.put(response)
                except json.JSONDecodeError:
                    # 忽略非 JSON 输出
                    pass
            except:
                break
    
    def _process_requests(self):
        """处理请求队列"""
        while self.running:
            try:
                request = self.request_queue.get(timeout=1)
                
                if request.get("command") == "EXIT":
                    # 停止命令
                    break
                
                # 写入请求到 stdin
                request_json = json.dumps(request, ensure_ascii=False)
                self.process.stdin.write(request_json + "\n")
                self.process.stdin.flush()
                
            except queue.Empty:
                continue
            except:
                break
    
    def _send_command(self, command: str, args: list = None, cwd: str = None, timeout: int = 60) -> Dict[str, Any]:
        """发送命令到控制器"""
        request = {
            "command": command,
            "args": args or [],
            "cwd": cwd,
            "timeout": timeout
        }
        
        self.request_queue.put(request)
        
        # 等待响应（带超时）
        try:
            response = self.response_queue.get(timeout=timeout)
            return response
        except queue.Empty:
            return {
                "success": False,
                "error": "命令执行超时(" + str(timeout) + "秒)"
            }
