# MAHO-Amadeus Cloud

一个可以在浏览器中与《命运石之门》角色对话的 Live2D 小应用。

本项目基于 [bysq-2006/MAHO-Amadeus](https://github.com/bysq-2006/MAHO-Amadeus) 整理，当前支持 **比屋定真帆** 与 **椎名真由理** 两个角色。对话由 DeepSeek API 生成，回复会经过翻译后交给 Genie TTS 合成角色语音，并配合 Live2D 立绘呈现在页面中。

## 项目来源

这个仓库不是从零开始的新作，而是对 `bysq-2006/MAHO-Amadeus` 的个人适配版本。原项目提供了 Vue 前端、Python 后端、Live2D 角色交互框架以及可替换的 LLM、TTS、翻译组件设计；本版本在其基础上改为云端 DeepSeek 对话，并加入双角色启动、真由理语音配置与 Windows 一键运行脚本。

《命运石之门》角色及相关设定、角色立绘和语音素材的权利属于各自权利方。本项目仅作为非官方的学习与个人体验项目展示，不代表原作者、作品权利方、Live2D 或模型作者的官方发布或授权版本。

## 当前功能

- 启动时选择真帆或真由理，不同角色拥有各自的立绘、声音与人物设定
- 以《命运石之门 0》的世界观进行简短日常对话
- DeepSeek `deepseek-chat` 云端对话，不需要启动本地大语言模型
- Genie TTS 角色语音合成
- 文本显示、语音播放与下一轮提问流程

## 运行环境

- Windows
- Python 3.11
- Node.js 与 npm
- 可用的 DeepSeek API Key
- 对应角色的 Genie TTS 模型文件

## 模型文件

真帆语音需要以下目录：

```text
backend/models/TTS-maho/
backend/models/GenieData/
```

真由理语音还需要：

```text
backend/models/MAYU_genie_tts/
backend/data/TTS-MAY-reference/ordinary.wav
```

真帆模型的放置方式可参考 [doc/GENIETTS接口说明.md](doc/GENIETTS接口说明.md)，真由理配置可参考 [doc/may相关/真由理版本配置指南.md](doc/may相关/真由理版本配置指南.md)。

## 安装

安装后端依赖：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

安装前端依赖：

```powershell
cd ..\frontend
npm install
```

设置 DeepSeek API Key：

```powershell
[Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "你的 API Key", "User")
```

重新打开终端或重新启动程序后即可读取该配置。

## 启动

双击项目根目录中的 `一键启动_MAHO.bat`，按提示选择角色：

```text
1. Maho
2. Mayuri
```

启动完成后打开：

[http://127.0.0.1:5173/login](http://127.0.0.1:5173/login)

默认登录账号与密码均为 `a`。

结束使用时，双击 `一键停止_MAHO.bat` 即可关闭前后端服务。

## 角色说明

### 比屋定真帆

以《命运石之门 0》时期的真帆为基础，保留她作为脑科学研究者、红莉栖前辈以及 Amadeus 相关研究人员的身份。对话风格偏理性、克制，偶尔会有不坦率的关心。

### 椎名真由理

以未来道具研究所 Lab Member 002 的真由理为基础，保留她温柔、天然、重视伙伴的性格。对话风格更加轻松柔和，也会用她熟悉的方式称呼研究所成员。

## 项目结构

```text
backend/       对话、翻译与语音服务
frontend/      Live2D 页面与交互界面
doc/           组件与角色配置说明
scripts/       启动与停止脚本
```

## 来源与许可

- 项目代码基础来自 [bysq-2006/MAHO-Amadeus](https://github.com/bysq-2006/MAHO-Amadeus)。截至 2026 年 5 月 25 日，其公开仓库根目录未显示独立 `LICENSE` 文件；因此本仓库保留来源说明，不将上游代码声明为某种开源许可证授权内容。
- 语音推理组件使用 [High-Logic/Genie-TTS](https://github.com/High-Logic/Genie-TTS)，其仓库标注为 MIT License。
- 真帆语音模型入口来自 [ModelScope / maho-tts2](https://www.modelscope.cn/models/bysq2006/maho-tts2/files)；真由理语音模型下载入口记录在 [doc/may相关/真由理版本配置指南.md](doc/may相关/真由理版本配置指南.md)。模型及参考音频应按其原始来源的条款使用。
- 页面运行依赖 Live2D Cubism Core；其许可条款见 [Live2D Proprietary Software License Agreement](https://www.live2d.com/eula/live2d-proprietary-software-license-agreement_en.html)。
- 云端对话服务使用 [DeepSeek 开放平台](https://platform.deepseek.com/)。

更完整的组件与素材记录见 [NOTICE.md](NOTICE.md) 和 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。公开分发或用于商业用途前，需要分别确认上游代码、角色素材、语音模型和 Live2D 运行组件的适用许可。
