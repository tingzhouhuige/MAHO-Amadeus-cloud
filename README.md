# MAHO-Amadeus Cloud

这是基于 [bysq-2006/MAHO-Amadeus](https://github.com/bysq-2006/MAHO-Amadeus) 整理的云端大模型部署版本。当前版本保留 MAHO 与真由理两个角色，LLM 使用 DeepSeek/OpenAI 兼容接口，TTS 使用 Genie TTS，本地大模型不参与运行。

## 上游来源与授权说明

- 上游项目：<https://github.com/bysq-2006/MAHO-Amadeus>
- 本仓库是个人部署整理版本，包含云端 LLM 配置、Genie TTS 部署配置、角色启动脚本与说明文件。
- 截至 2026-05-24，上游仓库根目录未发现 `LICENSE` 文件。本仓库不声明上游代码、角色素材、模型、语音、图片或 Live2D 资源采用任何标准开源许可证。公开发布、再分发或商业使用前，请自行确认上游作者及相关权利方授权。

更多说明见：

- [NOTICE.md](NOTICE.md)
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
- [GITHUB_UPLOAD_CHECKLIST.md](GITHUB_UPLOAD_CHECKLIST.md)

## 当前配置

- LLM：DeepSeek `deepseek-chat`，通过 OpenAI 兼容接口调用。
- TTS：Genie TTS，本地 ONNX 推理。
- 翻译：通过 OpenAI 兼容接口翻译为日文后进入 TTS。
- ASR/麦克风：默认关闭。
- 角色：启动时可选择比屋定真帆或椎名真由理。

API Key 不写入仓库。请使用环境变量：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
```

也可以设置 Windows 用户环境变量 `DEEPSEEK_API_KEY`。

## 模型准备

按 [doc/GENIETTS接口说明.md](doc/GENIETTS接口说明.md) 下载并放置 MAHO Genie TTS 模型。通常需要：

- `backend/models/TTS-maho/`
- `backend/models/GenieData/`

如果要使用真由理角色，还需要按 [doc/may相关/真由理版本配置指南.md](doc/may相关/真由理版本配置指南.md) 准备：

- `backend/models/MAYU_genie_tts/`
- `backend/data/TTS-MAY-reference/ordinary.wav`

这些模型文件较大，且可能受来源平台条款约束，不应直接提交到 GitHub。

## 快速启动

安装依赖：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt

cd ..\frontend
npm install
```

双击项目根目录：

```text
一键启动_MAHO.bat
```

启动时会提示选择角色：

```text
1. Maho
2. Mayuri
```

选择后会同时应用到：

- 前端显示名称
- 前端 Live2D 模型
- 后端系统人设提示词
- Genie TTS 角色模型与参考音频

打开：

- [http://127.0.0.1:5173/login](http://127.0.0.1:5173/login)
- 默认登录用户和密码：`a` / `a`

停止服务：

```text
一键停止_MAHO.bat
```

## 手动启动

后端：

```powershell
cd backend
.\.venv\Scripts\python.exe main.py
```

前端：

```powershell
cd frontend
npm run dev
```

默认端口：

- 后端：<http://127.0.0.1:8080>
- 前端：<http://127.0.0.1:5173>

## 上传 GitHub 前检查

```powershell
git status --short
git diff --check
```

不要提交：

- API Key
- 本地模型文件
- Python 虚拟环境
- `node_modules`
- 日志、临时音频和运行时输出

## 第三方来源

- MAHO-Amadeus：<https://github.com/bysq-2006/MAHO-Amadeus>
- Genie-TTS：<https://github.com/High-Logic/Genie-TTS>
- MAHO TTS 模型说明：<https://www.modelscope.cn/models/bysq2006/maho-tts2/files>
- DeepSeek API：<https://api.deepseek.com>

完整记录见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
