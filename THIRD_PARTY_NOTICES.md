# Third-Party Notices

This file records the main upstream projects, services, and assets referenced by this package. It is not a complete dependency license inventory; package-manager dependencies remain governed by their own licenses.

## MAHO-Amadeus

- Source: <https://github.com/bysq-2006/MAHO-Amadeus>
- License status found: no root `LICENSE` file detected in the public repository as of 2026-05-25.
- Notes: this repository is a modified deployment/configuration package derived from that upstream project. Keep attribution to the upstream author.

## Genie-TTS

- Source: <https://github.com/High-Logic/Genie-TTS>
- License: MIT license is shown by the upstream GitHub repository.
- Notes: this package uses the `genie_tts` Python dependency and follows the local `doc/GENIETTS接口说明.md` deployment path.

## MAHO TTS / LLM Model Downloads

- TTS model documentation: `doc/GENIETTS接口说明.md`
- Referenced model source: <https://www.modelscope.cn/models/bysq2006/maho-tts2/files>
- Mayuri model documentation and download reference: `doc/may相关/真由理版本配置指南.md`
- Legacy/local LLM documentation source: <https://www.modelscope.cn/models/bysq2006/maho-llm/files>
- Notes: model files are not committed. Users must download them separately and follow the source platform terms.

## Live2D Cubism Core

- Runtime file present in the frontend: `frontend/public/live2dcubismcore.min.js`
- License terms referenced by its embedded copyright notice: <https://www.live2d.com/eula/live2d-proprietary-software-license-agreement_en.html>
- Notes: Live2D Cubism Core is proprietary software. Any use or redistribution must follow Live2D's applicable license terms; this package does not relicense it.

## DeepSeek API

- Service: <https://api.deepseek.com>
- Notes: used through an OpenAI-compatible API adapter when configured. API keys must stay outside Git.

## Frontend Runtime Libraries

The frontend uses Vue, Vite, Pinia, PixiJS, pixi-live2d-display, and related npm dependencies. Their exact versions are recorded in `frontend/package-lock.json` and governed by their package licenses.

## Backend Runtime Libraries

The backend uses FastAPI, Uvicorn, OpenAI Python SDK, HTTPX, Genie-TTS, and related Python dependencies. Their exact install set is governed by `backend/requirements.txt` and the resolved package metadata in the local environment.

## Character / Media Assets

Images, audio, Live2D files, and character references under `frontend/public`, `frontend/src/assets`, `backend/data`, and `doc/` may have separate rights from the code. Keep these files attributed to their original source and verify redistribution permission before making a public release.
