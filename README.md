# Caption Words / 字幕生词本

English | [简体中文](README.zh-CN.md)

A Python desktop companion for Windows 11 Live Captions. It reads the built-in caption text through Windows UI Automation and does not run its own speech recognizer. The app starts in Chinese and can switch to English from the language selector.

## Build and run

Create the project environment and install its dependencies once:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run `build.ps1` to create the standalone `dist\CaptionWords.exe`. The one-file executable includes Python and the app dependencies; the development Python environment is only needed to rebuild it.

Start Windows Live Captions with `Win+Ctrl+L`, play English audio, then launch `dist\CaptionWords.exe`. Click the Baidu API settings button to enter the APP ID and key from the Baidu Translation Open Platform.

Click a transcript word to toggle it in the saved vocabulary and translate both the word and its source sentence. Open the vocabulary window to search saved words, review their original and translated sentences, and add notes. Notes save automatically. Export writes the vocabulary and notes to a text file.

Vocabulary is stored at `%LOCALAPPDATA%\CaptionWords\vocabulary.json`. Baidu credentials are encrypted for the current Windows user at `%LOCALAPPDATA%\CaptionWords\baidu-credentials.bin`.

Only the clicked word and its caption sentence are sent to Baidu. Audio and the full transcript remain local. Translation requires an active Baidu account, the General Text Translation service, and available quota. Error `52003` means the APP ID is unauthorized or the service is not enabled. The app depends on the UI Automation elements exposed by the installed Windows Live Captions version.
