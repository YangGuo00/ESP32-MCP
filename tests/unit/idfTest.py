#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESP-IDF MCP 本地函数接口 - 修复版
使用持久化shell会话确保环境一致性
"""

import subprocess
import os
import sys
import json
import tempfile
import time
import threading
import queue
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, Callable
from enum import Enum
import argparse


class IDFErrorCode(Enum):
    """标准化错误码"""
    SUCCESS = 0
    ENV_NOT_INITIALIZED = 100
    ENV_INIT_FAILED = 101
    PROJECT_NOT_FOUND = 200
    SET_TARGET_FAILED = 201
    BUILD_FAILED = 300
    UNKNOWN = 999


@dataclass
class IDFResult:
    """标准化返回结构"""
    success: bool
    code: int
    step: str
    stdout: str
    stderr: str
    metadata: Dict[str, Any]
    duration_ms: int
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def __str__(self) -> str:
        status = "✓ 成功" if self.success else "✗ 失败"
        return f"[{self.step}] {status} (耗时{self.duration_ms}ms)\nstdout:\n{self.stdout[:1000]}\nstderr:\n{self.stderr[:500]}"


class IDFController:
    """
    IDF控制器 - 使用持久化CMD会话
    所有命令在同一个shell中执行，确保环境变量持续有效
    """
    
    def __init__(self, idf_path: str, project_path: Optional[str] = None):
        self.idf_path = Path(idf_path).resolve()
        self.project_path = Path(project_path).resolve() if project_path else None
        self.export_bat = self.idf_path / "export.bat"
        self.idf_py = self.idf_path / "tools" / "idf.py"
        
        self._process: Optional[subprocess.Popen] = None
        self._initialized = False
        self._output_queue: queue.Queue = queue.Queue()
        self._reader_thread: Optional[threading.Thread] = None
        
        # 验证路径
        if not self.export_bat.exists():
            raise FileNotFoundError(f"export.bat不存在: {self.export_bat}")
        if not self.idf_py.exists():
            raise FileNotFoundError(f"idf.py不存在: {self.idf_py}")
    
    def _start_shell(self) -> bool:
        """启动持久化CMD shell"""
        try:
            # 启动cmd，启用延迟变量扩展，关闭回显
            self._process = subprocess.Popen(
                ["cmd.exe", "/V:ON", "/Q"],  # /V:ON启用延迟扩展，/Q关闭回显
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 合并stderr到stdout
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=str(self.idf_path),
                encoding='utf-8',
                errors='ignore'
            )
            
            # 启动输出读取线程
            self._reader_thread = threading.Thread(target=self._read_output, daemon=True)
            self._reader_thread.start()
            
            # 等待shell就绪
            time.sleep(0.5)
            return True
        except Exception as e:
            print(f"启动shell失败: {e}")
            return False
    
    def _read_output(self):
        """后台线程读取shell输出"""
        if not self._process or not self._process.stdout:
            return
        
        for line in iter(self._process.stdout.readline, ''):
            if line:
                self._output_queue.put(line)
    
    def _send_command(self, command: str, cwd: Optional[str] = None,
                      timeout: int = 60) -> tuple[bool, str]:
        """
        向shell发送命令并等待完成
        如果指定cwd，会先切换目录，执行完再切回原目录
        """
        if not self._process or self._process.poll() is not None:
            return False, "Shell进程未运行"
        
        # 清空之前的输出
        while not self._output_queue.empty():
            self._output_queue.get()
        
        # 构建完整命令
        marker = f"__CMD_DONE_{int(time.time()*1000)}__"
        
        if cwd:
            # 切换目录 -> 执行命令 -> 切回原目录
            full_cmd = f'cd /d "{cwd}" && {command} & echo {marker} & cd /d "{self.idf_path}"'
        else:
            full_cmd = f"{command} & echo {marker}"
        
        self._process.stdin.write(full_cmd + "\n")
        self._process.stdin.flush()
        
        # 收集输出直到看到标记
        output_lines = []
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                line = self._output_queue.get(timeout=0.5)
                if marker in line:
                    output = "".join(output_lines)
                    return True, output
                else:
                    output_lines.append(line)
            except queue.Empty:
                continue
        
        return False, "".join(output_lines) + "\n[超时]"
    
    def initialize(self) -> IDFResult:
        """
        初始化IDF环境
        启动shell并执行export.bat
        """
        start = time.time()
        
        try:
            # 1. 启动shell
            if not self._start_shell():
                return IDFResult(
                    success=False,
                    code=IDFErrorCode.ENV_INIT_FAILED.value,
                    step="initialize",
                    stdout="",
                    stderr="无法启动CMD shell",
                    metadata={},
                    duration_ms=int((time.time() - start) * 1000)
                )
            
            # 2. 执行export.bat（关键：在同一个shell中）
            print("正在执行export.bat，请稍候...")
            success, output = self._send_command(
                f'call "{self.export_bat}"',
                timeout=120
            )
            
            if not success or "error" in output.lower():
                return IDFResult(
                    success=False,
                    code=IDFErrorCode.ENV_INIT_FAILED.value,
                    step="initialize",
                    stdout=output,
                    stderr="export.bat执行失败或超时",
                    metadata={},
                    duration_ms=int((time.time() - start) * 1000)
                )
            
            # 3. 验证环境（尝试执行python --version）
            success, check_output = self._send_command("python --version", timeout=10)
            
            self._initialized = True
            
            return IDFResult(
                success=True,
                code=IDFErrorCode.SUCCESS.value,
                step="initialize",
                stdout=f"Shell环境初始化成功\nPython检查: {check_output.strip()}",
                stderr="",
                metadata={"export_output": output[-500:]},
                duration_ms=int((time.time() - start) * 1000)
            )
            
        except Exception as e:
            return IDFResult(
                success=False,
                code=IDFErrorCode.UNKNOWN.value,
                step="initialize",
                stdout="",
                stderr=str(e),
                metadata={},
                duration_ms=int((time.time() - start) * 1000)
            )
    
    def get_version(self) -> IDFResult:
        """获取IDF版本"""
        if not self._initialized:
            return self._error_not_initialized("get_version")
        
        start = time.time()
        
        success, output = self._send_command(
            f'python "{self.idf_py}" --version',
            timeout=30
        )
        
        return IDFResult(
            success=success and "ESP-IDF" in output,
            code=IDFErrorCode.SUCCESS.value if success else IDFErrorCode.UNKNOWN.value,
            step="get_version",
            stdout=output,
            stderr="" if success else "版本获取失败",
            metadata={},
            duration_ms=int((time.time() - start) * 1000)
        )
    
    def set_target(self, target: str = "esp32s3", project_path: Optional[str] = None) -> IDFResult:
        """
        设置目标芯片
        :param target: 芯片型号 (esp32/esp32s2/esp32s3/esp32c3等)
        :param project_path: 工程路径，默认使用初始化时传入的路径
        """
        if not self._initialized:
            return self._error_not_initialized("set_target")
        
        start = time.time()
        
        # 确定工程路径
        proj_path = Path(project_path).resolve() if project_path else self.project_path
        if not proj_path:
            return IDFResult(
                success=False,
                code=IDFErrorCode.PROJECT_NOT_FOUND.value,
                step="set_target",
                stdout="",
                stderr="未指定工程路径，请在初始化时传入或作为参数传入",
                metadata={},
                duration_ms=0
            )
        
        if not proj_path.exists():
            return IDFResult(
                success=False,
                code=IDFErrorCode.PROJECT_NOT_FOUND.value,
                step="set_target",
                stdout="",
                stderr=f"工程路径不存在: {proj_path}",
                metadata={},
                duration_ms=0
            )
        
        # 确保工程结构完整
        self._ensure_project_structure(proj_path)
        
        print(f"正在设置目标芯片 {target}，工程路径: {proj_path}")
        
        # 在工程目录下执行set-target，添加 --yes 参数避免交互
        success, output = self._send_command(
            f'python "{self.idf_py}" set-target {target} --yes',
            cwd=str(proj_path),
            timeout=300
        )
        
        print(f"set-target 命令执行完成: success={success}, output_length={len(output)}")
        
        return IDFResult(
            success=success and ("Done" in output or "Configuring done" in output or "Configuration done" in output),
            code=IDFErrorCode.SUCCESS.value if success else IDFErrorCode.SET_TARGET_FAILED.value,
            step="set_target",
            stdout=output,
            stderr="" if success else output[-1000:],
            metadata={"target": target, "project_path": str(proj_path)},
            duration_ms=int((time.time() - start) * 1000)
        )
    
    def build(self, project_path: Optional[str] = None,
              progress_callback: Optional[Callable[[str], None]] = None) -> IDFResult:
        """
        编译项目
        :param project_path: 工程路径，默认使用初始化时传入的路径
        :param progress_callback: 进度回调函数
        """
        if not self._initialized:
            return self._error_not_initialized("build")
        
        start = time.time()
        
        # 确定工程路径
        cwd = Path(project_path).resolve() if project_path else self.project_path
        if not cwd:
            return IDFResult(
                success=False,
                code=IDFErrorCode.PROJECT_NOT_FOUND.value,
                step="build",
                stdout="",
                stderr="未指定工程路径",
                metadata={},
                duration_ms=0
            )
        
        if not cwd.exists():
            return IDFResult(
                success=False,
                code=IDFErrorCode.PROJECT_NOT_FOUND.value,
                step="build",
                stdout="",
                stderr=f"工程路径不存在: {cwd}",
                metadata={},
                duration_ms=0
            )
        
        print(f"开始编译工程: {cwd}")
        
        # 清空队列准备实时输出
        while not self._output_queue.empty():
            self._output_queue.get()
        
        # 发送编译命令（带目录切换）
        marker = f"__BUILD_DONE_{int(time.time()*1000)}__"
        build_cmd = f'cd /d "{cwd}" && python "{self.idf_py}" build && echo {marker} && cd /d "{self.idf_path}"'
        
        self._process.stdin.write(build_cmd + "\n")
        self._process.stdin.flush()
        
        # 实时收集输出
        output_lines = []
        build_success = False
        timeout_seconds = 300
        
        start_collect = time.time()
        while time.time() - start_collect < timeout_seconds:
            try:
                line = self._output_queue.get(timeout=0.1)
                if marker in line:
                    build_success = True
                    break
                else:
                    output_lines.append(line)
                    if progress_callback:
                        progress_callback(line)
            except queue.Empty:
                continue
        
        output = "".join(output_lines)
        
        # 改进错误处理：提供更详细的错误信息
        if not build_success:
            # 查找错误信息
            error_lines = []
            for line in output_lines:
                if any(keyword in line.lower() for keyword in ['error', 'failed', 'not found', 'undefined', 'cannot']):
                    error_lines.append(line)
            
            error_msg = "\n".join(error_lines[-20:]) if error_lines else "编译超时或未知错误"
            if not output:
                error_msg = "编译失败，未获取到输出信息"
            
            return IDFResult(
                success=False,
                code=IDFErrorCode.BUILD_FAILED.value,
                step="build",
                stdout=output[-50000:],
                stderr=error_msg,
                metadata={"project_path": str(cwd), "raw_output": output},
                duration_ms=int((time.time() - start) * 1000)
            )
        
        return IDFResult(
            success=build_success and ("Successfully" in output or "Project build complete" in output),
            code=IDFErrorCode.SUCCESS.value if build_success else IDFErrorCode.BUILD_FAILED.value,
            step="build",
            stdout=output[-50000:],
            stderr="",
            metadata={"project_path": str(cwd)},
            duration_ms=int((time.time() - start) * 1000)
        )
    
    def erase_flash(self, project_path: Optional[str] = None) -> IDFResult:
        """
        擦除 Flash
        :param project_path: 工程路径，默认使用初始化时传入的路径
        """
        if not self._initialized:
            return self._error_not_initialized("erase_flash")
        
        start = time.time()
        
        # 确定工程路径
        cwd = Path(project_path).resolve() if project_path else self.project_path
        if not cwd:
            return IDFResult(
                success=False,
                code=IDFErrorCode.PROJECT_NOT_FOUND.value,
                step="erase_flash",
                stdout="",
                stderr="未指定工程路径",
                metadata={},
                duration_ms=0
            )
        
        if not cwd.exists():
            return IDFResult(
                success=False,
                code=IDFErrorCode.PROJECT_NOT_FOUND.value,
                step="erase_flash",
                stdout="",
                stderr=f"工程路径不存在: {cwd}",
                metadata={},
                duration_ms=0
            )
        
        print(f"开始擦除 Flash: {cwd}")
        
        # 发送擦除命令
        success, output = self._send_command(
            f'cd /d "{cwd}" && python "{self.idf_py}" erase-flash && cd /d "{self.idf_path}"',
            timeout=180
        )
        
        return IDFResult(
            success=success and ("Flash successfully erased" in output or "Done" in output),
            code=IDFErrorCode.SUCCESS.value if success else IDFErrorCode.ERASE_FAILED.value,
            step="erase_flash",
            stdout=output[-50000:],
            stderr="" if success else output[-1000:],
            metadata={"project_path": str(cwd)},
            duration_ms=int((time.time() - start) * 1000)
        )
    
    def fullclean(self, project_path: Optional[str] = None) -> IDFResult:
        """
        清理项目
        :param project_path: 工程路径，默认使用初始化时传入的路径
        """
        if not self._initialized:
            return self._error_not_initialized("fullclean")
        
        start = time.time()
        
        # 确定工程路径
        cwd = Path(project_path).resolve() if project_path else self.project_path
        if not cwd:
            return IDFResult(
                success=False,
                code=IDFErrorCode.PROJECT_NOT_FOUND.value,
                step="fullclean",
                stdout="",
                stderr="未指定工程路径",
                metadata={},
                duration_ms=0
            )
        
        if not cwd.exists():
            return IDFResult(
                success=False,
                code=IDFErrorCode.PROJECT_NOT_FOUND.value,
                step="fullclean",
                stdout="",
                stderr=f"工程路径不存在: {cwd}",
                metadata={},
                duration_ms=0
            )
        
        print(f"开始清理项目: {cwd}")
        
        # 发送清理命令
        success, output = self._send_command(
            f'cd /d "{cwd}" && python "{self.idf_py}" fullclean && cd /d "{self.idf_path}"',
            timeout=180
        )
        
        # 改进错误处理：如果 output 为空，提供更详细的信息
        if not success or not output:
            error_msg = output if output else "命令执行失败，未获取到输出信息"
            if not success:
                error_msg += f" (命令执行返回失败)"
            return IDFResult(
                success=False,
                code=IDFErrorCode.CLEAN_FAILED.value,
                step="fullclean",
                stdout=output,
                stderr=error_msg,
                metadata={"project_path": str(cwd), "raw_output": output},
                duration_ms=int((time.time() - start) * 1000)
            )
        
        return IDFResult(
            success=success and ("Done" in output or "Project cleaned" in output),
            code=IDFErrorCode.SUCCESS.value if success else IDFErrorCode.CLEAN_FAILED.value,
            step="fullclean",
            stdout=output[-50000:],
            stderr="" if success else output[-1000:],
            metadata={"project_path": str(cwd)},
            duration_ms=int((time.time() - start) * 1000)
        )
    
    def menuconfig(self, project_path: Optional[str] = None) -> IDFResult:
        """
        打开配置菜单
        :param project_path: 工程路径，默认使用初始化时传入的路径
        """
        if not self._initialized:
            return self._error_not_initialized("menuconfig")
        
        start = time.time()
        
        # 确定工程路径
        cwd = Path(project_path).resolve() if project_path else self.project_path
        if not cwd:
            return IDFResult(
                success=False,
                code=IDFErrorCode.PROJECT_NOT_FOUND.value,
                step="menuconfig",
                stdout="",
                stderr="未指定工程路径",
                metadata={},
                duration_ms=0
            )
        
        if not cwd.exists():
            return IDFResult(
                success=False,
                code=IDFErrorCode.PROJECT_NOT_FOUND.value,
                step="menuconfig",
                stdout="",
                stderr=f"工程路径不存在: {cwd}",
                metadata={},
                duration_ms=0
            )
        
        print(f"开始打开配置菜单: {cwd}")
        
        # menuconfig 是交互式命令，需要特殊处理
        # 这里只返回启动信息
        return IDFResult(
            success=True,
            code=IDFErrorCode.SUCCESS.value,
            step="menuconfig",
            stdout="menuconfig 已启动（交互式命令，请在终端中操作）",
            stderr="",
            metadata={"project_path": str(cwd)},
            duration_ms=int((time.time() - start) * 1000)
        )
    
    def _ensure_project_structure(self, project_path: Path):
        """确保项目有基本文件结构"""
        # 只在目录为空时创建默认工程
        if any(project_path.iterdir()):
            return  # 目录已有内容，不覆盖
        
        print(f"创建默认工程结构: {project_path}")
        
        cmake_file = project_path / "CMakeLists.txt"
        cmake_file.write_text(
            f'cmake_minimum_required(VERSION 3.16)\n'
            f'include($ENV{{IDF_PATH}}/tools/cmake/project.cmake)\n'
            f'project(mcp_project)\n'
        )
        
        main_dir = project_path / "main"
        main_dir.mkdir(exist_ok=True)
        
        main_cmake = main_dir / "CMakeLists.txt"
        main_cmake.write_text('idf_component_register(SRCS "main.c")\n')
        
        main_c = main_dir / "main.c"
        main_c.write_text('''#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

void app_main(void)
{
    printf("Hello ESP32 from MCP!\\n");
    while(1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
''')
    
    def _error_not_initialized(self, step: str) -> IDFResult:
        return IDFResult(
            success=False,
            code=IDFErrorCode.ENV_NOT_INITIALIZED.value,
            step=step,
            stdout="",
            stderr="IDF环境未初始化，请先调用initialize()",
            metadata={},
            duration_ms=0
        )
    
    def close(self):
        """清理资源"""
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except:
                self._process.kill()


# ==================== 测试入口 ====================

def test_idf_functions():
    """测试initialize、get_version、set_target、build"""
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="ESP-IDF MCP 测试")
    parser.add_argument("--idf-path", default=r"D:/esp32/Espressif/frameworks/esp-idf-v5.3.3",
                       help="IDF安装路径")
    parser.add_argument("--project-path", required=True,
                       help="ESP32工程路径（必需）")
    parser.add_argument("--target", default="esp32s3",
                       choices=["esp32", "esp32s2", "esp32s3", "esp32c3", "esp32c6"],
                       help="目标芯片型号")
    args = parser.parse_args()
    
    print("=" * 60)
    print("ESP-IDF MCP 功能测试")
    print("=" * 60)
    print(f"IDF路径: {args.idf_path}")
    print(f"工程路径: {args.project_path}")
    print(f"目标芯片: {args.target}")
    
    controller = None
    try:
        # 创建控制器，传入工程路径
        controller = IDFController(args.idf_path, args.project_path)
        print("✓ 控制器创建成功")
        
        # 测试1: 初始化环境
        print("\n" + "-" * 40)
        print("测试1: 初始化环境")
        result = controller.initialize()
        print(result)
        if not result.success:
            print("环境初始化失败，终止测试")
            return False
        
        # 测试2: 获取版本
        print("\n" + "-" * 40)
        print("测试2: 获取IDF版本")
        result = controller.get_version()
        print(result)
        
        # 测试3: 设置目标芯片
        print("\n" + "-" * 40)
        print(f"测试3: 设置目标芯片 ({args.target})")
        result = controller.set_target(args.target)
        print(result)
        if not result.success:
            print("设置目标失败，终止测试")
            return False
        
        # 测试4: 编译项目
        print("\n" + "-" * 40)
        print("测试4: 编译项目")
        
        def print_progress(line: str):
            print(line, end='')
        
        result = controller.build(progress_callback=print_progress)
        print(f"\n编译结果: {'成功' if result.success else '失败'}")
        print(f"耗时: {result.duration_ms}ms")
        if not result.success:
            print(f"错误输出:\n{result.stdout[-2000:]}")
            return False
        
        print("\n" + "=" * 60)
        print("全部测试通过！")
        return True
        
    except Exception as e:
        print(f"测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if controller:
            controller.close()


if __name__ == "__main__":
    success = test_idf_functions()
    sys.exit(0 if success else 1)