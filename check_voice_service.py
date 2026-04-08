#!/usr/bin/env python3
"""
语音识别服务诊断工具
用于检查语音识别功能不可用的原因
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_env_file():
    """检查 .env 文件配置"""
    print_header("1. 检查环境变量配置")
    
    env_path = Path("services/nlp_service/.env")
    env_example_path = Path("services/nlp_service/.env.example")
    
    if not env_path.exists():
        print("❌ .env 文件不存在!")
        if env_example_path.exists():
            print(f"   提示: 请复制 {env_example_path} 为 .env 并配置百度API密钥")
        else:
            print("   提示: 需要创建 .env 文件并配置以下内容:")
            print("""
   BAIDU_API_KEY=你的百度API Key
   BAIDU_SECRET_KEY=你的百度Secret Key
   QIANFAN_AK=你的千帆AK（可选）
   QIANFAN_SK=你的千帆SK（可选）
            """)
        return False
    
    print(f"✅ 找到 .env 文件: {env_path}")
    
    # 检查必要的环境变量
    required_vars = ['BAIDU_API_KEY', 'BAIDU_SECRET_KEY']
    missing_vars = []
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
            for var in required_vars:
                if var not in content or f"{var}=" not in content:
                    missing_vars.append(var)
                elif f"{var}=你的" in content or f"{var}=your" in content.lower():
                    print(f"⚠️  {var} 未正确配置（仍为示例值）")
                    missing_vars.append(var)
    except Exception as e:
        print(f"❌ 读取 .env 文件失败: {e}")
        return False
    
    if missing_vars:
        print(f"❌ 缺少以下环境变量配置: {', '.join(missing_vars)}")
        print("\n   如何获取百度API密钥:")
        print("   1. 访问 https://console.bce.baidu.com/")
        print("   2. 登录并进入'产品服务' -> '人工智能' -> '语音技术'")
        print("   3. 创建应用获取 API Key 和 Secret Key")
        return False
    
    print("✅ 所有必要的环境变量都已配置")
    return True

def check_ffmpeg():
    """检查 FFmpeg 是否安装"""
    print_header("2. 检查 FFmpeg 依赖")
    
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        print("❌ FFmpeg 未安装!")
        print("\n   安装方法:")
        if sys.platform == "win32":
            print("   Windows:")
            print("   1. 访问 https://ffmpeg.org/download.html")
            print("   2. 下载 Windows 版本")
            print("   3. 解压并添加到系统 PATH")
            print("   或使用 Chocolatey: choco install ffmpeg")
        elif sys.platform == "darwin":
            print("   macOS: brew install ffmpeg")
        else:
            print("   Linux: sudo apt install ffmpeg  或  sudo yum install ffmpeg")
        return False
    
    print(f"✅ FFmpeg 已安装: {ffmpeg_path}")
    
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        version_line = result.stdout.split('\n')[0]
        print(f"   版本: {version_line}")
        return True
    except Exception as e:
        print(f"⚠️  FFmpeg 已安装但无法执行: {e}")
        return False

def check_python_dependencies():
    """检查 Python 依赖"""
    print_header("3. 检查 Python 依赖")
    
    requirements_path = Path("services/nlp_service/requirements.txt")
    if not requirements_path.exists():
        print("⚠️  找不到 requirements.txt")
        return False
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'httpx',
        'pydub',
        'python-dotenv',
        'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少以下依赖包: {', '.join(missing_packages)}")
        print(f"   安装命令: pip install -r {requirements_path}")
        return False
    
    return True

def check_service_running():
    """检查服务是否运行"""
    print_header("4. 检查 NLP 服务状态")
    
    try:
        import requests
        response = requests.get("http://localhost:8083/diagnose", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print("✅ NLP 服务正在运行")
            print(f"   诊断信息: {data}")
            
            # 检查百度 token 状态
            if data.get('baidu_token') == 'ok':
                print("   ✅ 百度 API 认证成功")
            else:
                print(f"   ❌ 百度 API 认证失败: {data.get('baidu_token')}")
                return False
            
            # 检查 ffmpeg 状态
            if 'not_found' in str(data.get('ffmpeg', '')):
                print("   ❌ FFmpeg 未找到")
                return False
            else:
                print(f"   ✅ FFmpeg 可用")
            
            return True
        else:
            print(f"❌ 服务返回错误状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到 NLP 服务 (端口 8083): {e}")
        print("   提示: 请确保已启动 NLP 服务")
        print("   启动命令: cd services/nlp_service && uvicorn app.main:app --reload --port 8083")
        return False

def main():
    """主函数"""
    # 设置控制台编码
    if sys.platform == "win32":
        try:
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        except:
            pass
    
    print("\n" + "语音识别服务诊断工具".center(60, "="))
    
    checks = [
        check_env_file,
        check_ffmpeg,
        check_python_dependencies,
        check_service_running
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"\n❌ 检查过程中出现错误: {e}")
            results.append(False)
    
    print_header("诊断总结")
    
    if all(results):
        print("✅ 所有检查都通过！语音识别服务应该可以正常工作。")
        print("\n如果仍然遇到问题，请检查:")
        print("  1. 浏览器是否允许麦克风权限")
        print("  2. 前端代理配置是否正确（vite.config.js）")
        print("  3. 查看浏览器控制台和后端日志获取详细错误信息")
    else:
        print("❌ 发现以下问题，请修复后重试:")
        if not results[0]:
            print("  ❌ 百度API密钥未配置或配置错误")
        if not results[1]:
            print("  ❌ FFmpeg 未安装")
        if not results[2]:
            print("  ❌ Python 依赖包缺失")
        if not results[3]:
            print("  ❌ NLP 服务未运行或配置错误")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()

