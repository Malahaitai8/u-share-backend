# 🎤 语音识别"服务暂不可用"问题解决方案

## 问题原因

经过诊断，你的电脑上出现"服务暂不可用"错误的原因是：

1. ❌ **百度 API 密钥未配置** - `.env` 文件为空
2. ❌ **FFmpeg 未安装** - 无法转换音频格式
3. ❌ **Python 依赖缺失** - 缺少 `pydub` 和 `python-dotenv`

而你同学的电脑可以正常使用，是因为她已经：
- ✅ 配置了有效的百度 API 密钥
- ✅ 安装了 FFmpeg
- ✅ 安装了所有依赖包

## 🚀 快速修复（3步）

### 步骤 1: 获取并配置百度 API 密钥

1. 访问 https://console.bce.baidu.com/
2. 登录后进入：**产品服务** → **人工智能** → **语音技术**
3. 创建应用，获取 `API Key` 和 `Secret Key`
4. 编辑 `services/nlp_service/.env` 文件，添加：

```env
BAIDU_API_KEY=你的API_Key
BAIDU_SECRET_KEY=你的Secret_Key
```

### 步骤 2: 安装 FFmpeg

**使用 Chocolatey（推荐）：**

```powershell
# 以管理员身份运行 PowerShell
choco install ffmpeg
```

**手动安装：**
1. 下载：https://ffmpeg.org/download.html（选择 Windows 版本）
2. 解压到 `C:\ffmpeg`
3. 添加 `C:\ffmpeg\bin` 到系统 PATH
4. 重启命令行验证：`ffmpeg -version`

### 步骤 3: 安装 Python 依赖

```bash
cd services/nlp_service
pip install -r requirements.txt
```

## 🔍 验证修复

运行诊断脚本：

```bash
python check_voice_service.py
```

应该看到全部通过：
```
✅ 所有必要的环境变量都已配置
✅ FFmpeg 已安装
✅ 所有 Python 依赖都已安装
✅ NLP 服务正在运行
✅ 百度 API 认证成功
```

## 📝 启动服务

```bash
# 启动 NLP 服务
cd services/nlp_service
uvicorn app.main:app --reload --port 8083

# 另开一个终端，启动前端
cd u-share-frontend
npm run dev
```

## 🛠️ 辅助工具

我已经为你创建了两个辅助脚本：

1. **诊断脚本** - `check_voice_service.py`
   - 自动检查所有配置项
   - 快速定位问题

2. **配置脚本** - `setup_voice_service.py`
   - 交互式配置向导
   - 自动安装依赖

3. **详细指南** - `语音识别问题修复指南.md`
   - 完整的问题分析
   - 详细的修复步骤
   - 常见问题解答

## ⚠️ 注意事项

1. **百度 API 有免费额度**：每天 50,000 次调用，个人项目完全够用
2. **FFmpeg 必须安装**：WebM 音频需要转换为 WAV 才能被百度 API 识别
3. **.env 文件不会被 Git 同步**：每个人需要配置自己的密钥
4. **麦克风权限**：浏览器需要允许麦克风访问（仅限 HTTPS 或 localhost）

## 📞 如果还有问题

1. 运行诊断脚本：`python check_voice_service.py`
2. 查看 NLP 服务日志
3. 查看浏览器控制台（F12）
4. 检查网络请求（Network 标签）

---

**预计修复时间**：10-15 分钟（主要是获取 API 密钥和安装 FFmpeg）

修复完成后，语音识别功能将完全正常工作！🎉












