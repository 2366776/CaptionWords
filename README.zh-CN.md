# 字幕生词本 / Caption Words

[English](README.md) | 简体中文

这是一个适用于 Windows 11“实时字幕”的 Python 桌面工具。它通过 Windows UI 自动化读取系统实时字幕，不运行自己的语音识别程序。应用默认使用中文，也可以通过语言选择器切换为英文。

## 构建与运行

首次使用时，创建 Python 虚拟环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

运行 `build.ps1`，生成独立程序 `dist\CaptionWords.exe`。该单文件程序已包含 Python 和应用依赖；只有重新构建时才需要开发用 Python 环境。

按 `Win+Ctrl+L` 启动 Windows“实时字幕”，播放英文音频，然后运行 `dist\CaptionWords.exe`。点击百度 API 设置按钮，输入百度翻译开放平台提供的 APP ID 和密钥。

点击字幕中的单词，可将它加入或移出生词本，并翻译该单词和对应的字幕原句。在生词本窗口中，可以搜索已保存的单词、查看原句及译文、添加备注。备注会自动保存，也可以将生词和备注导出为文本文件。

生词本保存在 `%LOCALAPPDATA%\CaptionWords\vocabulary.json`。百度翻译凭据保存在 `%LOCALAPPDATA%\CaptionWords\baidu-credentials.bin`，并使用当前 Windows 用户凭据加密。

只有点击的单词和对应的字幕句子会发送给百度；音频和完整字幕内容始终保留在本机。使用翻译功能需要已启用百度账号、通用文本翻译服务，并且账户仍有可用配额。错误 `52003` 表示 APP ID 未获授权，或尚未启用对应服务。应用依赖当前 Windows“实时字幕”版本所提供的 UI 自动化元素。
