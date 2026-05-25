# NOTICE

This repository is a modified deployment package of **MAHO-Amadeus**.

## Upstream Source

- Upstream project: <https://github.com/bysq-2006/MAHO-Amadeus>
- Upstream author/owner: `bysq-2006`
- Local changes in this package include deployment scripts, DeepSeek/OpenAI-compatible API configuration, Genie TTS integration fixes, frontend interaction fixes, and documentation/packaging notes.

## License Status

As of 2026-05-25, the upstream `bysq-2006/MAHO-Amadeus` repository does not appear to provide a root `LICENSE` file in the public repository. Because no explicit upstream license grant was found, this package does **not** claim that the upstream project is open source under MIT, Apache, GPL, or any other standard license.

Do not remove upstream attribution. Before publishing, redistributing, or using this repository commercially, confirm permission with the upstream author and the rights holders of any included character, image, model, voice, audio, or Live2D assets.

## Fictional Work / Character Assets

MAHO-Amadeus is inspired by *Steins;Gate*. Character names, likenesses, related setting elements, images, audio, and Live2D assets may be owned by their respective rights holders. This repository is not affiliated with, endorsed by, or sponsored by those rights holders.

## Models And Runtime Assets

Large model files and runtime downloads are intentionally excluded from Git by `.gitignore`. Follow the documentation under `doc/` to download required assets from their original sources and comply with their licenses or terms.

## Live2D Runtime

The frontend includes Live2D Cubism Core runtime code, whose embedded notice points to the Live2D Proprietary Software License Agreement:

<https://www.live2d.com/eula/live2d-proprietary-software-license-agreement_en.html>

Use and redistribution of that runtime must comply with Live2D's applicable terms. This repository does not grant rights to Live2D software or character models.

## API Keys

Do not commit API keys. Configure cloud model keys through environment variables such as `DEEPSEEK_API_KEY` or a local-only secret store.
