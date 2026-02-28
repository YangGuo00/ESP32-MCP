import os
import subprocess
import sys
import time


def test_idf_version():
    """测试获取IDF版本号"""
    # IDF安装路径
    idf_path = r"D:\Software\idf\exe\Espressif\frameworks\esp-idf-v5.4.1"
    
    # 检查IDF路径是否存在
    if not os.path.exists(idf_path):
        print(f"错误: IDF路径不存在: {idf_path}")
        return False
    
    # 检查export.bat文件是否存在
    export_bat = os.path.join(idf_path, "export.bat")
    if not os.path.exists(export_bat):
        print(f"错误: export.bat文件不存在: {export_bat}")
        return False
    
    try:
        # 在Windows上，使用cmd.exe执行命令，先执行export.bat，然后执行idf.py --version
        # 使用&连接两个命令，确保在同一个cmd会话中执行
        cmd = f"cmd.exe /c \"{export_bat} & idf.py --version\""
        
        print(f"执行命令: {cmd}")
        print("正在执行export.bat...")
        
        # 执行命令
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=idf_path,
            timeout=60  # 设置60秒超时
        )
        
        # 检查命令执行结果
        if result.returncode != 0:
            print(f"错误: 命令执行失败")
            print(f"错误输出: {result.stderr}")
            print(f"标准输出: {result.stdout}")
            return False
        
        # 输出结果
        output = result.stdout.strip()
        print(f"命令输出:\n{output}")
        
        # 提取版本号信息
        lines = output.split('\n')
        version_output = None
        
        # 遍历所有行，找到以ESP-IDF开头的行
        for line in lines:
            line = line.strip()
            if line.startswith('ESP-IDF'):
                version_output = line
                break
        
        if version_output:
            print(f"IDF版本号: {version_output}")
            print("成功: 获取到IDF版本号")
            return True
        else:
            print("错误: 无法解析IDF版本号")
            return False
            
    except subprocess.TimeoutExpired:
        print("错误: 命令执行超时")
        return False
    except Exception as e:
        print(f"错误: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_idf_version()
    if success:
        print("测试通过!")
        sys.exit(0)
    else:
        print("测试失败!")
        sys.exit(1)
