# MAHO-Amadeus Cloud Deployment

这是一个基于 [bysq-2006/MAHO-Amadeus](https://github.com/bysq-2006/MAHO-Amadeus) 整理的云端大模型部署版本。当前版本把本地大语言模型改为 DeepSeek/OpenAI 兼容接口，保留前端角色交互、Genie TTS 和翻译组件，并加入 Windows 一键启动/停止脚本。

## 上游来源与授权声明

- 上游项目：<https://github.com/bysq-2006/MAHO-Amadeus>
- 上游作者/仓库所有者：`bysq-2006`
- 本仓库为个人部署整理版本，包含云端 LLM 配置、TTS 性能与前端交互修复、一键启动脚本、上传前授权声明文件。

截至 2026-05-24，上游仓库未发现根目录 `LICENSE` 文件。因此本仓库不声明上游代码、角色素材、模型、语音、图片或 Live2D 资源采用 MIT、Apache、GPL 等任何标准开源许可证。公开发布、再分发或商用前，请自行确认上游作者及相关权利方授权。

更多说明见：

- [NOTICE.md](NOTICE.md)
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
- [GITHUB_UPLOAD_CHECKLIST.md](GITHUB_UPLOAD_CHECKLIST.md)

## 当前版本说明

本版本默认配置：

- LLM：DeepSeek `deepseek-chat`，通过 OpenAI 兼容接口调用。
- TTS：Genie TTS，本地 ONNX 推理。
- 翻译：通过 OpenAI 兼容接口翻译为日文后进入 TTS。
- ASR/麦克风：默认关闭。
- 本地大模型：不使用 Ollama，本地模型文件不纳入 Git。

API Key 不写入仓库。请使用环境变量或本地密钥存储，例如：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
```

也可以在 Windows 用户环境变量里配置 `DEEPSEEK_API_KEY`。

## 目录结构

```text
.
├── backend/                 # FastAPI 后端、对话逻辑、LLM/TTS/翻译组件
│   ├── config.yaml           # 当前部署配置，API Key 字段保持为空
│   ├── core/                 # 核心业务代码
│   ├── data/                 # 参考音频、用户数据库等小型数据
│   ├── models/               # 模型目录，仅保留 .gitkeep，真实模型不上传
│   └── requirements.txt      # Python 依赖
├── frontend/                # Vue 3 前端
│   ├── public/               # 前端静态资源、Live2D 资源
│   └── src/                  # 前端源码
├── doc/                     # 上游与本地部署文档
├── scripts/                 # Windows 启动/停止脚本
├── 一键启动_MAHO.bat          # 一键启动前后端
├── 一键停止_MAHO.bat          # 一键停止前后端
├── 打开_MAHO网页.url           # 打开登录页
├── 打开_MAHO主页.url           # 打开主页
├── NOTICE.md                # 来源与版权边界声明
└── THIRD_PARTY_NOTICES.md   # 第三方来源与许可证记录
```

不会上传的本地运行目录包括：

- `backend/.venv/`
- `frontend/node_modules/`
- `backend/models/` 下的真实模型文件
- `.runtime/`
- 日志、临时音频和运行时输出

## 快速启动

### 1. 安装依赖

后端：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

前端：

```powershell
cd frontend
npm install
```

### 2. 下载 Genie TTS 模型

按照 [doc/GENIETTS接口说明.md](doc/GENIETTS接口说明.md) 下载并放置模型文件。通常需要将以下目录放到 `backend/models/` 下：

- `TTS-maho/`
- `GenieData/`

这些模型文件较大，且受来源平台条款约束，不应直接提交到 GitHub。

### 3. 配置 DeepSeek

确认 [backend/config.yaml](backend/config.yaml) 使用：

```yaml
llm:
  select: openai_api
```

并配置环境变量：

```powershell
setx DEEPSEEK_API_KEY "你的 DeepSeek API Key"
```

重新打开终端后生效。

### 4. 一键启动

双击根目录：

```text
一键启动_MAHO.bat
```

然后打开：

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

- 后端：`http://127.0.0.1:8080`
- 前端：`http://127.0.0.1:5173`

## 上传 GitHub 前检查

上传前请确认：

```powershell
git status --short
git diff --check
```

不要提交：

- API Key
- 本地模型文件
- Python 虚拟环境
- `node_modules`
- 日志和临时文件

## 第三方组件

主要第三方来源：

- MAHO-Amadeus：<https://github.com/bysq-2006/MAHO-Amadeus>
- Genie-TTS：<https://github.com/High-Logic/Genie-TTS>
- MAHO TTS 模型说明：<https://www.modelscope.cn/models/bysq2006/maho-tts2/files>
- DeepSeek API：<https://api.deepseek.com>

完整记录见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
