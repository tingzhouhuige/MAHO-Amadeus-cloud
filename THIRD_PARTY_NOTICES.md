# Third-Party Notices

This file records the main upstream projects, services, and assets referenced by this package. It is not a complete dependency license inventory; package-manager dependencies remain governed by their own licenses.

## MAHO-Amadeus

- Source: <https://github.com/bysq-2006/MAHO-Amadeus>
- License status found: no root `LICENSE` file detected as of 2026-05-24.
- Notes: this repository is a modified deployment/configuration package derived from that upstream project. Keep attribution to the upstream author.

## Genie-TTS

- Source: <https://github.com/High-Logic/Genie-TTS>
- License: MIT license is shown by the upstream GitHub repository.
- Notes: this package uses the `genie_tts` Python dependency and follows the local `doc/GENIETTS接口说明.md` deployment path.

## MAHO TTS / LLM Model Downloads

- TTS model documentation: `doc/GENIETTS接口说明.md`
- Referenced model source: <https://www.modelscope.cn/models/bysq2006/maho-tts2/files>
- Legacy/local LLM documentation source: <https://www.modelscope.cn/models/bysq2006/maho-llm/files>
- Notes: model files are not committed. Users must download them separately and follow the source platform terms.

## DeepSeek API

- Service: <https://api.deepseek.com>
- Notes: used through an OpenAI-compatible API adapter when configured. API keys must stay outside Git.

## Frontend Runtime Libraries

The frontend uses Vue, Vite, Pinia, PixiJS, pixi-live2d-display, and related npm dependencies. Their exact versions are recorded in `frontend/package-lock.json` and governed by their package licenses.

## Backend Runtime Libraries

The backend uses FastAPI, Uvicorn, OpenAI Python SDK, HTTPX, Genie-TTS, and related Python dependencies. Their exact install set is governed by `backend/requirements.txt` and the resolved package metadata in the local environment.

## Character / Media Assets

Images, audio, Live2D files, and character references under `frontend/public`, `frontend/src/assets`, `backend/data`, and `doc/` may have separate rights from the code. Keep these files attributed to their original source and verify redistribution permission before making a public release.
