#!/usr/bin/env python3
"""
语音识别服务快速配置脚本
自动帮助用户配置语音识别所需的环境
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def setup_env_file():
    """配置 .env 文件"""
    print_header("配置百度 API 密钥")
    
    env_path = Path("services/nlp_service/.env")
    
    print("\n请按照以下步骤获取百度 API 密钥：")
    print("1. 访问 https://console.bce.baidu.com/")
    print("2. 登录并进入'产品服务' -> '人工智能' -> '语音技术'")
    print("3. 创建应用获取 API Key 和 Secret Key\n")
    
    api_key = input("请输入 BAIDU_API_KEY（回车跳过）: ").strip()
    secret_key = input("请输入 BAIDU_SECRET_KEY（回车跳过）: ").strip()
    
    if not api_key or not secret_key:
        print("\n⚠️  跳过配置，稍后请手动编辑 services/nlp_service/.env 文件")
        print("   格式如下：")
        print("   BAIDU_API_KEY=你的API_Key")
        print("   BAIDU_SECRET_KEY=你的Secret_Key")
        return False
    
    # 创建 .env 文件
    env_content = f"""# 百度语音识别 API 配置
BAIDU_API_KEY={api_key}
BAIDU_SECRET_KEY={secret_key}

# 百度千帆大模型配置（可选）
QIANFAN_AK=
QIANFAN_SK=
"""
    
    try:
        env_path.parent.mkdir(parents=True, exist_ok=True)
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"\n✅ 已创建配置文件: {env_path}")
        return True
    except Exception as e:
        print(f"\n❌ 创建配置文件失败: {e}")
        return False

def install_dependencies():
    """安装 Python 依赖"""
    print_header("安装 Python 依赖")
    
    requirements_path = Path("services/nlp_service/requirements.txt")
    if not requirements_path.exists():
        print(f"❌ 找不到 {requirements_path}")
        return False
    
    print(f"\n正在安装依赖包...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)],
            check=True
        )
        print("\n✅ 依赖包安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 依赖包安装失败: {e}")
        print(f"   请手动运行: pip install -r {requirements_path}")
        return False

def check_ffmpeg():
    """检查并提示安装 FFmpeg"""
    print_header("检查 FFmpeg")
    
    import shutil
    ffmpeg_path = shutil.which("ffmpeg")
    
    if ffmpeg_path:
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
    
    print("❌ FFmpeg 未安装")
    print("\nWindows 安装方法：")
    print("1. 使用 Chocolatey（推荐）:")
    print("   choco install ffmpeg")
    print("\n2. 手动安装：")
    print("   - 访问 https://ffmpeg.org/download.html")
    print("   - 下载 Windows 版本")
    print("   - 解压并添加到系统 PATH")
    
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
    
    print("\n" + "语音识别服务快速配置".center(60, "="))
    print("\n此脚本将帮助你配置语音识别所需的环境")
    
    results = []
    
    # 1. 配置环境变量
    result = setup_env_file()
    results.append(("百度 API 配置", result))
    
    # 2. 安装依赖
    print("\n是否安装 Python 依赖？(y/n): ", end="")
    if input().lower().strip() == 'y':
        result = install_dependencies()
        results.append(("Python 依赖安装", result))
    else:
        print("跳过依赖安装")
        results.append(("Python 依赖安装", False))
    
    # 3. 检查 FFmpeg
    result = check_ffmpeg()
    results.append(("FFmpeg 检查", result))
    
    # 总结
    print_header("配置总结")
    
    all_success = True
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
        if not success:
            all_success = False
    
    if all_success:
        print("\n✅ 所有配置完成！")
        print("\n下一步：")
        print("1. 启动 NLP 服务:")
        print("   cd services/nlp_service")
        print("   uvicorn app.main:app --reload --port 8083")
        print("\n2. 启动前端项目，测试语音识别功能")
    else:
        print("\n⚠️  部分配置未完成，请按照提示完成剩余配置")
        print("\n完成后，运行诊断脚本验证:")
        print("   python check_voice_service.py")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()












