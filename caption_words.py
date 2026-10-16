import ctypes
import hashlib
import html
import json
import os
import re
import sys
import time
import uuid
from ctypes import wintypes
from datetime import datetime
from pathlib import Path

import requests
import uiautomation as auto
from app_icon import create_action_icon, create_app_icon
from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, QUrl, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


APP_NAME = "Caption Words"
APP_DIRECTORY = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "CaptionWords"
VOCABULARY_PATH = APP_DIRECTORY / "vocabulary.json"
CREDENTIAL_PATH = APP_DIRECTORY / "baidu-credentials.bin"
BAIDU_ENDPOINT = "https://fanyi-api.baidu.com/api/trans/vip/translate"
WORD_PATTERN = re.compile(r"[\w]+(?:['’\-][\w]+)*", re.UNICODE)

TEXT = {
    "zh": {
        "app_title": "字幕生词本",
        "subtitle": "Windows 实时字幕英语学习工具",
        "select_word_hint": "点击字幕中的单词，查看释义并加入生词本",
        "transcript_hint": "点击任意单词即可查看释义并收藏",
        "connected": "已连接实时字幕",
        "not_connected": "未检测到实时字幕",
        "read_error": "读取字幕失败",
        "live_transcript": "实时字幕",
        "word_details": "单词详情",
        "word_translation": "单词释义",
        "caption_sentence": "字幕原句",
        "sentence_translation": "原句翻译",
        "configure_baidu": "百度 API 设置",
        "vocabulary": "生词本",
        "export": "导出",
        "configure_first": "请先设置百度翻译 API。",
        "translating": "正在翻译…",
        "wait_rate": "请稍等片刻再翻译下一个单词。",
        "saved_word": "已加入生词本",
        "removed_word": "已从生词本移除",
        "no_sentence": "未找到完整字幕句子",
        "translation_failed": "翻译失败：{error}",
        "settings_title": "百度翻译 API 设置",
        "settings_help": "输入百度翻译开放平台的 APP ID 和密钥。密钥仅保存在本机，并由 Windows 用户凭据加密。",
        "appid": "APP ID",
        "secret": "密钥",
        "save": "保存",
        "cancel": "取消",
        "required_fields": "APP ID 和密钥都不能为空。",
        "settings_saved": "百度翻译设置已保存。",
        "vocabulary_title": "我的生词本",
        "search_placeholder": "搜索单词、例句或备注",
        "original_sentence": "字幕原句",
        "my_note": "我的备注",
        "note_placeholder": "在这里记录用法、联想或需要复习的内容…",
        "remove": "删除生词",
        "translate_again": "重新翻译",
        "empty_vocabulary": "生词本还是空的",
        "empty_hint": "在实时字幕里点一个单词，它就会保存在这里。",
        "export_title": "导出生词本",
        "export_filter": "文本文件 (*.txt)",
        "export_done": "生词本已导出。",
        "nothing_to_export": "当前没有可导出的生词。",
        "api_error": "百度 API 错误 {code}：{message}",
        "api_no_result": "百度没有返回翻译结果。",
        "meaning_unavailable": "没有单词释义",
        "translation_pending": "等待百度翻译配置",
        "added_at": "划词时间：{date}",
        "col_word": "单词",
        "col_meaning": "单词释义",
        "col_source": "字幕原句",
        "col_translation": "原句翻译",
        "col_note": "备注",
        "col_date": "划词时间",
    },
    "en": {
        "app_title": "Caption Words",
        "subtitle": "English learning with Windows Live Captions",
        "select_word_hint": "Click a word in the captions to see its meaning and save it",
        "transcript_hint": "Click any word to see its meaning and save it",
        "connected": "Connected to Live Captions",
        "not_connected": "Live Captions not detected",
        "read_error": "Could not read captions",
        "live_transcript": "LIVE TRANSCRIPT",
        "word_details": "WORD DETAILS",
        "word_translation": "WORD TRANSLATION",
        "caption_sentence": "CAPTION SENTENCE",
        "sentence_translation": "SENTENCE TRANSLATION",
        "configure_baidu": "Baidu API settings",
        "vocabulary": "Vocabulary",
        "export": "Export",
        "configure_first": "Configure the Baidu Translation API first.",
        "translating": "Translating…",
        "wait_rate": "Please wait a moment before the next translation.",
        "saved_word": "Added to vocabulary",
        "removed_word": "Removed from vocabulary",
        "no_sentence": "No complete caption sentence found",
        "translation_failed": "Translation failed: {error}",
        "settings_title": "Baidu Translation API settings",
        "settings_help": "Enter the APP ID and key from Baidu Translation Open Platform. The key stays on this PC and is encrypted for your Windows account.",
        "appid": "APP ID",
        "secret": "Secret key",
        "save": "Save",
        "cancel": "Cancel",
        "required_fields": "APP ID and key are required.",
        "settings_saved": "Baidu Translation settings saved.",
        "vocabulary_title": "My Vocabulary",
        "search_placeholder": "Search words, sentences, or notes",
        "original_sentence": "ORIGINAL SENTENCE",
        "my_note": "MY NOTE",
        "note_placeholder": "Add a usage note, memory aid, or review reminder…",
        "remove": "Remove word",
        "translate_again": "Translate again",
        "empty_vocabulary": "Your vocabulary is empty",
        "empty_hint": "Click a word in Live Captions to save it here.",
        "export_title": "Export vocabulary",
        "export_filter": "Text file (*.txt)",
        "export_done": "Vocabulary exported.",
        "nothing_to_export": "There are no saved words to export.",
        "api_error": "Baidu API error {code}: {message}",
        "api_no_result": "Baidu returned no translation results.",
        "meaning_unavailable": "No word translation returned",
        "translation_pending": "Waiting for Baidu API setup",
        "added_at": "Saved: {date}",
        "col_word": "Word",
        "col_meaning": "Word meaning",
        "col_source": "Caption sentence",
        "col_translation": "Sentence translation",
        "col_note": "Note",
        "col_date": "Saved at",
    },
}


class DataBlob(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]


def _dpapi(data: bytes, decrypt: bool = False) -> bytes:
    source = ctypes.create_string_buffer(data)
    input_blob = DataBlob(len(data), ctypes.cast(source, ctypes.POINTER(ctypes.c_byte)))
    output_blob = DataBlob()
    crypt = ctypes.windll.crypt32
    if decrypt:
        success = crypt.CryptUnprotectData(
            ctypes.byref(input_blob), None, None, None, None, 1, ctypes.byref(output_blob)
        )
    else:
        success = crypt.CryptProtectData(
            ctypes.byref(input_blob), None, None, None, None, 1, ctypes.byref(output_blob)
        )
    if not success:
        raise ctypes.WinError()
    try:
        return ctypes.string_at(output_blob.pbData, output_blob.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(output_blob.pbData)


class CredentialStore:
    def load(self) -> tuple[str, str] | None:
        if not CREDENTIAL_PATH.exists():
            return None
        try:
            value = _dpapi(CREDENTIAL_PATH.read_bytes(), decrypt=True).decode("utf-8")
            app_id, app_key = value.split("\n", 1)
            return app_id, app_key
        except (OSError, UnicodeError, ValueError):
            return None

    def save(self, app_id: str, app_key: str) -> None:
        APP_DIRECTORY.mkdir(parents=True, exist_ok=True)
        payload = bytearray((app_id + "\n" + app_key).encode("utf-8"))
        try:
            CREDENTIAL_PATH.write_bytes(_dpapi(bytes(payload)))
        finally:
            payload[:] = b"\0" * len(payload)


class VocabularyStore:
    def __init__(self) -> None:
        self.entries: list[dict[str, str]] = []
        self.load()

    @staticmethod
    def _value(item: dict, *names: str) -> str:
        for name in names:
            if item.get(name) is not None:
                return str(item[name])
        return ""

    def load(self) -> None:
        if not VOCABULARY_PATH.exists():
            return
        try:
            data = json.loads(VOCABULARY_PATH.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(data, list):
            return
        entries: dict[str, dict[str, str]] = {}
        for item in data:
            if isinstance(item, str):
                values = {"word": item}
            elif isinstance(item, dict):
                values = {
                    "word": self._value(item, "Word", "word"),
                    "word_translation": self._value(item, "WordTranslation", "word_translation"),
                    "source_sentence": self._value(item, "SourceSentence", "source_sentence"),
                    "sentence_translation": self._value(item, "SentenceTranslation", "sentence_translation"),
                    "note": self._value(item, "Note", "note"),
                    "added_at": self._value(item, "AddedAt", "added_at"),
                }
            else:
                continue
            word = values.get("word", "").strip()
            if not word:
                continue
            values.setdefault("word_translation", "")
            values.setdefault("source_sentence", "")
            values.setdefault("sentence_translation", "")
            values.setdefault("note", "")
            values.setdefault("added_at", "")
            entries[word.casefold()] = values
        self.entries = sorted(entries.values(), key=lambda entry: entry["word"].casefold())

    def find(self, word: str) -> dict[str, str] | None:
        return next((entry for entry in self.entries if entry["word"].casefold() == word.casefold()), None)

    def toggle(self, word: str, sentence: str) -> bool:
        existing = self.find(word)
        if existing is not None:
            self.entries.remove(existing)
            self.save()
            return False
        self.entries.append({
            "word": word,
            "word_translation": "",
            "source_sentence": sentence,
            "sentence_translation": "",
            "note": "",
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        self.save()
        return True

    def save(self) -> None:
        APP_DIRECTORY.mkdir(parents=True, exist_ok=True)
        temporary_path = VOCABULARY_PATH.with_suffix(".tmp")
        temporary_path.write_text(json.dumps(self.entries, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temporary_path, VOCABULARY_PATH)


class TranslationWorkerSignals(QObject):
    finished = Signal(str, object, object)


class TranslationWorker(QRunnable):
    def __init__(self, word: str, sentence: str, credentials: tuple[str, str], language: str) -> None:
        super().__init__()
        self.word = word
        self.sentence = sentence
        self.credentials = credentials
        self.language = language
        self.signals = TranslationWorkerSignals()

    def run(self) -> None:
        try:
            result = translate(self.word, self.sentence, self.credentials, self.language)
            self.signals.finished.emit(self.word, result, None)
        except Exception as error:
            self.signals.finished.emit(self.word, None, str(error))


class CaptionReaderSignals(QObject):
    finished = Signal(object, object)


class CaptionReader(QRunnable):
    def __init__(self) -> None:
        super().__init__()
        self.signals = CaptionReaderSignals()

    def run(self) -> None:
        try:
            root = auto.GetRootControl()
            caption_window = root.WindowControl(ClassName="LiveCaptionsDesktopWindow", searchDepth=1)
            if not caption_window.Exists(0, 0):
                self.signals.finished.emit(None, None)
                return
            text_control = caption_window.TextControl(AutomationId="CaptionsTextBlock", searchDepth=5)
            if not text_control.Exists(0, 0):
                self.signals.finished.emit(None, None)
                return
            self.signals.finished.emit(text_control.Name or "", None)
        except Exception as error:
            self.signals.finished.emit(None, str(error))


def translate(word: str, sentence: str, credentials: tuple[str, str], language: str = "zh") -> dict[str, str]:
    app_id, app_key = credentials
    query = word if sentence == word else word + "\n" + sentence
    salt = uuid.uuid4().hex[:16]
    signature = hashlib.md5((app_id + query + salt + app_key).encode("utf-8")).hexdigest()
    response = requests.post(
        BAIDU_ENDPOINT,
        data={"q": query, "from": "en", "to": "zh", "appid": app_id, "salt": salt, "sign": signature},
        timeout=12,
    )
    response.raise_for_status()
    payload = response.json()
    if "error_code" in payload:
        strings = TEXT[language]
        raise RuntimeError(strings["api_error"].format(code=payload["error_code"], message=payload.get("error_msg", "")))
    results = payload.get("trans_result", [])
    if not results:
        raise RuntimeError(TEXT["zh"]["api_no_result"])
    word_result = next((row.get("dst", "") for row in results if row.get("src") == word), "")
    sentence_result = next((row.get("dst", "") for row in results if row.get("src") == sentence), "")
    if not word_result:
        word_result = results[0].get("dst", "")
    if not sentence_result and len(results) > 1:
        sentence_result = results[1].get("dst", "")
    return {"word_translation": word_result, "sentence_translation": sentence_result if sentence != word else ""}


class ApiSettingsDialog(QDialog):
    def __init__(self, language: str, current: tuple[str, str] | None, parent=None) -> None:
        super().__init__(parent)
        self.language = language
        self.current = current
        self.credentials: tuple[str, str] | None = None
        self.setWindowTitle(TEXT[language]["settings_title"])
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(12)
        self.help_label = QLabel()
        self.help_label.setWordWrap(True)
        layout.addWidget(self.help_label)
        self.app_id_caption = QLabel()
        self.app_id_caption.setObjectName("sectionLabel")
        layout.addWidget(self.app_id_caption)
        self.app_id = QLineEdit(current[0] if current else "")
        self.app_id.setClearButtonEnabled(True)
        layout.addWidget(self.app_id)
        self.app_key_caption = QLabel()
        self.app_key_caption.setObjectName("sectionLabel")
        layout.addWidget(self.app_key_caption)
        self.app_key = QLineEdit()
        self.app_key.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.app_key)
        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        buttons.addStretch(1)
        self.cancel_button = QPushButton()
        self.save_button = QPushButton()
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.save_credentials)
        buttons.addWidget(self.cancel_button)
        buttons.addWidget(self.save_button)
        layout.addLayout(buttons)
        self.apply_language(language)

    def apply_language(self, language: str) -> None:
        self.language = language
        strings = TEXT[language]
        self.setWindowTitle(strings["settings_title"])
        self.help_label.setText(strings["settings_help"])
        self.app_id.setPlaceholderText(strings["appid"])
        self.app_key.setPlaceholderText(strings["secret"])
        self.cancel_button.setText(strings["cancel"])
        self.save_button.setText(strings["save"])
        self.app_id_caption.setText(strings["appid"])
        self.app_key_caption.setText(strings["secret"])
        self.save_button.setObjectName("primaryButton")

    def save_credentials(self) -> None:
        app_id = self.app_id.text().strip()
        app_key = self.app_key.text()
        if not app_key and self.current and app_id == self.current[0]:
            app_key = self.current[1]
        if not app_id or not app_key:
            QMessageBox.information(self, TEXT[self.language]["settings_title"], TEXT[self.language]["required_fields"])
            return
        self.credentials = (app_id, app_key)
        self.accept()


class VocabularyWindow(QDialog):
    def __init__(self, store: VocabularyStore, language: str, translate_callback, parent=None) -> None:
        super().__init__(parent)
        self.store = store
        self.language = language
        self.translate_callback = translate_callback
        self._loading = False
        self.setMinimumSize(760, 500)
        root = QHBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        self.left_panel = QFrame()
        self.left_panel.setObjectName("panel")
        left = QVBoxLayout(self.left_panel)
        left.setContentsMargins(14, 14, 14, 14)
        left.setSpacing(10)
        self.search = QLineEdit()
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.refresh)
        self.entry_list = QListWidget()
        self.entry_list.currentItemChanged.connect(self.show_entry)
        left.addWidget(self.search)
        left.addWidget(self.entry_list, 1)
        root.addWidget(self.left_panel, 1)

        self.right_panel = QFrame()
        self.right_panel.setObjectName("panel")
        right = QGridLayout(self.right_panel)
        right.setContentsMargins(24, 22, 24, 22)
        right.setVerticalSpacing(12)
        self.word = QLabel()
        self.word.setObjectName("wordHeading")
        self.meaning = QLabel()
        self.meaning.setWordWrap(True)
        self.source_caption = QLabel()
        self.source_caption.setObjectName("sectionLabel")
        self.source_sentence = QLabel()
        self.source_sentence.setWordWrap(True)
        self.translation_caption = QLabel()
        self.translation_caption.setObjectName("sectionLabel")
        self.sentence_translation = QLabel()
        self.sentence_translation.setWordWrap(True)
        self.note_caption = QLabel()
        self.note_caption.setObjectName("sectionLabel")
        self.note = QTextEdit()
        self.note.textChanged.connect(self.save_note)
        self.translate_button = QPushButton()
        self.remove_button = QPushButton()
        self.translate_button.clicked.connect(self.translate_selected)
        self.remove_button.clicked.connect(self.remove_selected)
        self.translate_button.setIcon(create_action_icon("refresh"))
        self.remove_button.setIcon(create_action_icon("trash", "#a54a3a"))
        self.remove_button.setObjectName("dangerButton")
        right.addWidget(self.word, 0, 0, 1, 2)
        right.addWidget(self.meaning, 1, 0, 1, 2)
        right.addWidget(self.source_caption, 2, 0, 1, 2)
        right.addWidget(self.source_sentence, 3, 0, 1, 2)
        right.addWidget(self.translation_caption, 4, 0, 1, 2)
        right.addWidget(self.sentence_translation, 5, 0, 1, 2)
        right.addWidget(self.note_caption, 6, 0, 1, 2)
        right.addWidget(self.note, 7, 0, 1, 2)
        right.addWidget(self.translate_button, 8, 0)
        right.addWidget(self.remove_button, 8, 1)
        right.setRowStretch(7, 1)
        root.addWidget(self.right_panel, 2)
        self.apply_language(language)
        self.refresh()

    def apply_language(self, language: str) -> None:
        self.language = language
        strings = TEXT[language]
        self.setWindowTitle(strings["vocabulary_title"])
        self.search.setPlaceholderText(strings["search_placeholder"])
        self.source_caption.setText(strings["original_sentence"])
        self.translation_caption.setText(strings["sentence_translation"])
        self.note_caption.setText(strings["my_note"])
        self.note.setPlaceholderText(strings["note_placeholder"])
        self.translate_button.setText(strings["translate_again"])
        self.remove_button.setText(strings["remove"])
        self.refresh()

    def refresh(self, *_args) -> None:
        selected_word = self.entry_list.currentItem().data(256) if self.entry_list.currentItem() else None
        query = self.search.text().casefold().strip()
        matches = [entry for entry in self.store.entries if not query or any(
            query in entry.get(key, "").casefold()
            for key in ("word", "word_translation", "source_sentence", "sentence_translation", "note")
        )]
        self._loading = True
        self.entry_list.clear()
        selected = None
        for entry in matches:
            item = QListWidgetItem(entry.get("word", ""))
            item.setData(256, entry.get("word", ""))
            self.entry_list.addItem(item)
            if entry.get("word", "").casefold() == str(selected_word or "").casefold():
                selected = item
        if selected is not None:
            self.entry_list.setCurrentItem(selected)
        elif self.entry_list.count():
            self.entry_list.setCurrentRow(0)
        self._loading = False
        if not self.entry_list.count():
            self.show_entry(None, None)

    def show_entry(self, current, _previous) -> None:
        entry = None
        if current is not None:
            word = current.data(256)
            entry = self.store.find(word)
        self._loading = True
        strings = TEXT[self.language]
        if entry is None:
            self.word.setText(strings["empty_vocabulary"])
            self.meaning.setText(strings["empty_hint"])
            self.source_sentence.clear()
            self.sentence_translation.clear()
            self.note.clear()
        else:
            self.word.setText(entry.get("word", ""))
            self.meaning.setText(entry.get("word_translation", "") or strings["meaning_unavailable"])
            self.source_sentence.setText(entry.get("source_sentence", ""))
            self.sentence_translation.setText(entry.get("sentence_translation", ""))
            self.note.setPlainText(entry.get("note", ""))
        self._loading = False

    def save_note(self) -> None:
        if self._loading or self.entry_list.currentItem() is None:
            return
        entry = self.store.find(self.entry_list.currentItem().data(256))
        if entry is not None:
            entry["note"] = self.note.toPlainText()
            self.store.save()

    def translate_selected(self) -> None:
        if self.entry_list.currentItem() is None:
            return
        entry = self.store.find(self.entry_list.currentItem().data(256))
        if entry is not None:
            self.translate_callback(entry)

    def remove_selected(self) -> None:
        if self.entry_list.currentItem() is None:
            return
        word = self.entry_list.currentItem().data(256)
        entry = self.store.find(word)
        if entry is not None:
            self.store.entries.remove(entry)
            self.store.save()
            self.refresh()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.language = "zh"
        self.store = VocabularyStore()
        self.credential_store = CredentialStore()
        self.credentials = self.credential_store.load()
        self.pool = QThreadPool.globalInstance()
        self.workers: set[TranslationWorker] = set()
        self.caption_workers: set[CaptionReader] = set()
        self.caption_poll_interval = 500
        self.last_lookup = 0.0
        self.selected_word = ""
        self.transcript = ""
        self.contexts: dict[int, tuple[str, str]] = {}
        self.vocabulary_window: VocabularyWindow | None = None
        self.status_key = "not_connected"
        self.setMinimumSize(820, 580)
        self.resize(1080, 760)
        self.setStyleSheet("""
            QWidget { color: #253832; font-family: 'Segoe UI'; font-size: 13px; }
            QMainWindow, QDialog { background: #f3f6f4; }
            QFrame#panel { background: #ffffff; border: 1px solid #e2eae6; border-radius: 14px; }
            QLabel#wordHeading { color: #183f36; font-size: 22px; font-weight: 700; }
            QLabel#emptyHint { color: #788780; font-size: 14px; font-weight: 500; }
            QLabel#sectionLabel { color: #71817b; font-size: 10px; font-weight: 700; letter-spacing: 1px; }
            QLabel#statusLabel { background: #edf2ef; color: #687871; border: 1px solid #e1e9e4; border-radius: 12px; padding: 6px 11px; font-size: 12px; font-weight: 600; }
            QLabel#statusLabel[connected="true"] { background: #e8f5ef; color: #21745b; border-color: #cfe8dc; }
            QLabel#transcriptHint { color: #87958f; font-size: 11px; }
            QPushButton { background: #f4f7f5; color: #30463e; border: 1px solid #dce7e1; border-radius: 8px; padding: 9px 12px; font-weight: 600; }
            QPushButton:hover { background: #eaf2ed; border-color: #c5d8ce; }
            QPushButton:pressed { background: #dcebe3; }
            QPushButton:focus, QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 1px solid #65a994; }
            QPushButton#primaryButton { background: #176b5b; color: #ffffff; border-color: #176b5b; }
            QPushButton#primaryButton:hover { background: #125849; border-color: #125849; }
            QPushButton#dangerButton { background: #fff7f5; color: #a54a3a; border-color: #f0d9d3; }
            QPushButton#dangerButton:hover { background: #ffefeb; border-color: #e9c2b8; }
            QLineEdit, QTextEdit, QTextBrowser, QListWidget, QComboBox { background: #ffffff; border: 1px solid #dfe8e3; border-radius: 8px; padding: 9px; selection-background-color: #d9eee5; selection-color: #183f36; }
            QTextBrowser { border: none; padding: 12px; }
            QListWidget { padding: 6px; outline: none; }
            QListWidget::item { padding: 10px 11px; border-radius: 6px; }
            QListWidget::item:hover { background: #f3f7f4; }
            QListWidget::item:selected { background: #e5f2eb; color: #183f36; }
            QScrollBar:vertical { background: transparent; width: 9px; margin: 4px 2px; }
            QScrollBar::handle:vertical { background: #cbd8d1; border-radius: 4px; min-height: 28px; }
            QScrollBar::handle:vertical:hover { background: #aabdb3; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)
        self.setWindowIcon(create_app_icon())
        self._build_ui()
        self.apply_language()
        self.caption_timer = QTimer(self)
        self.caption_timer.setSingleShot(True)
        self.caption_timer.timeout.connect(self.read_captions)
        self.caption_timer.start(0)

    def _build_ui(self) -> None:
        central = QWidget()
        outer = QVBoxLayout(central)
        outer.setContentsMargins(24, 20, 24, 24)
        outer.setSpacing(14)
        header = QHBoxLayout()
        header.setSpacing(14)
        title_group = QVBoxLayout()
        title_group.setSpacing(3)
        self.logo_label = QLabel()
        self.logo_label.setPixmap(create_app_icon().pixmap(48, 48))
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 23px; font-weight: 700; color: #183f36;")
        self.subtitle_label = QLabel()
        self.subtitle_label.setStyleSheet("color: #788780; font-size: 12px;")
        title_group.addWidget(self.title_label)
        title_group.addWidget(self.subtitle_label)
        header.addWidget(self.logo_label)
        header.addLayout(title_group)
        header.addStretch(1)
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")
        self.language_box = QComboBox()
        self.language_box.setMinimumWidth(112)
        self.language_box.addItem("中文", "zh")
        self.language_box.addItem("English", "en")
        self.language_box.currentIndexChanged.connect(self.change_language)
        header.addWidget(self.status_label)
        header.addSpacing(16)
        header.addWidget(self.language_box)
        outer.addLayout(header)
        outer.addSpacing(16)

        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)
        transcript_panel = QFrame()
        transcript_panel.setObjectName("panel")
        transcript_layout = QVBoxLayout(transcript_panel)
        transcript_layout.setContentsMargins(18, 16, 18, 16)
        self.transcript_heading = QLabel()
        self.transcript_heading.setObjectName("sectionLabel")
        transcript_header = QHBoxLayout()
        transcript_header.setSpacing(10)
        self.transcript_hint = QLabel()
        self.transcript_hint.setObjectName("transcriptHint")
        transcript_header.addWidget(self.transcript_heading)
        transcript_header.addStretch(1)
        transcript_header.addWidget(self.transcript_hint)
        self.transcript_view = QTextBrowser()
        self.transcript_view.setOpenLinks(False)
        self.transcript_view.setOpenExternalLinks(False)
        self.transcript_view.anchorClicked.connect(self.on_word_clicked)
        self.transcript_view.document().setDefaultStyleSheet("a { color: #59756a; text-decoration: none; } a:hover { color: #176b5b; }")
        transcript_layout.addLayout(transcript_header)
        transcript_layout.addWidget(self.transcript_view, 1)

        details_panel = QFrame()
        details_panel.setObjectName("panel")
        details = QVBoxLayout(details_panel)
        details.setContentsMargins(18, 16, 18, 16)
        details.setSpacing(8)
        self.details_heading = QLabel()
        self.details_heading.setObjectName("sectionLabel")
        self.word_label = QLabel()
        self.word_label.setObjectName("emptyHint")
        self.word_label.setWordWrap(True)
        self.word_translation_heading = self._section_label()
        self.word_translation = QLabel()
        self.word_translation.setWordWrap(True)
        self.word_translation.setStyleSheet("font-size: 18px; color: #147d70; font-weight: 600;")
        self.sentence_heading = self._section_label()
        self.source_sentence = QLabel()
        self.source_sentence.setWordWrap(True)
        self.sentence_translation_heading = self._section_label()
        self.sentence_translation = QLabel()
        self.sentence_translation.setWordWrap(True)
        self.sentence_translation.setStyleSheet("font-size: 14px; color: #147d70; font-weight: 600;")
        details.addWidget(self.details_heading)
        details.addWidget(self.word_label)
        details.addWidget(self.word_translation_heading)
        details.addWidget(self.word_translation)
        details.addSpacing(8)
        details.addWidget(self.sentence_heading)
        details.addWidget(self.source_sentence)
        details.addWidget(self.sentence_translation_heading)
        details.addWidget(self.sentence_translation)
        details.addStretch(1)
        buttons = QVBoxLayout()
        self.api_button = QPushButton()
        self.vocabulary_button = QPushButton()
        self.export_button = QPushButton()
        self.api_button.setIcon(create_action_icon("settings"))
        self.vocabulary_button.setIcon(create_action_icon("book"))
        self.export_button.setIcon(create_action_icon("export"))
        self.vocabulary_button.setObjectName("primaryButton")
        self.api_button.clicked.connect(self.configure_api)
        self.vocabulary_button.clicked.connect(self.open_vocabulary)
        self.export_button.clicked.connect(self.export_vocabulary)
        buttons.addWidget(self.api_button)
        buttons.addWidget(self.vocabulary_button)
        buttons.addWidget(self.export_button)
        details.addLayout(buttons)
        splitter.addWidget(transcript_panel)
        splitter.addWidget(details_panel)
        splitter.setStretchFactor(0, 65)
        splitter.setStretchFactor(1, 35)
        outer.addWidget(splitter, 1)
        self.setCentralWidget(central)

    @staticmethod
    def _section_label() -> QLabel:
        label = QLabel()
        label.setObjectName("sectionLabel")
        return label

    def apply_language(self) -> None:
        strings = TEXT[self.language]
        self.setWindowTitle(strings["app_title"])
        self.title_label.setText(strings["app_title"])
        self.subtitle_label.setText(strings["subtitle"])
        self.transcript_heading.setText(strings["live_transcript"])
        self.transcript_hint.setText(strings["transcript_hint"])
        self.details_heading.setText(strings["word_details"])
        self.word_translation_heading.setText(strings["word_translation"])
        self.sentence_heading.setText(strings["caption_sentence"])
        self.sentence_translation_heading.setText(strings["sentence_translation"])
        self.api_button.setText(strings["configure_baidu"])
        self.vocabulary_button.setText(strings["vocabulary"])
        self.export_button.setText(strings["export"])
        self.set_status(self.status_key)
        if not self.selected_word:
            self.word_label.setText(strings["select_word_hint"])
            self.word_label.setObjectName("emptyHint")
        else:
            self.word_label.setObjectName("wordHeading")
        if self.vocabulary_window is not None:
            self.vocabulary_window.apply_language(self.language)
        if self.transcript:
            self.set_transcript(self.transcript)

    def change_language(self, index: int) -> None:
        language = self.language_box.itemData(index)
        if language in TEXT and language != self.language:
            self.language = language
            self.apply_language()

    def set_status(self, key: str) -> None:
        self.status_key = key
        self.status_label.setText("● " + TEXT[self.language][key])
        self.status_label.setProperty("connected", key == "connected")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def read_captions(self) -> None:
        worker = CaptionReader()
        worker.signals.finished.connect(self.caption_read_finished)
        worker.signals.finished.connect(lambda *_args, task=worker: self.caption_workers.discard(task))
        self.caption_workers.add(worker)
        self.pool.start(worker)

    def caption_read_finished(self, text: object, error: object) -> None:
        if error:
            self.set_status("read_error")
            self.caption_poll_interval = 2000
        elif text is None:
            self.set_status("not_connected")
            self.caption_poll_interval = 3000
        else:
            self.set_status("connected")
            self.caption_poll_interval = 500
            if text and text != self.transcript:
                self.set_transcript(text)
        self.caption_timer.start(self.caption_poll_interval)

    @staticmethod
    def sentence_at(text: str, offset: int) -> str:
        start_line = text.rfind("\n", 0, offset) + 1
        end_line = text.find("\n", offset)
        if end_line < 0:
            end_line = len(text)
        line = text[start_line:end_line].strip()
        local_offset = max(0, offset - start_line)
        start = 0
        for match in re.finditer(r"[.!?]\s+", line):
            if match.end() <= local_offset:
                start = match.end()
            else:
                break
        end = len(line)
        for match in re.finditer(r"[.!?](?:\s+|$)", line):
            if match.start() >= local_offset:
                end = match.end() - 1
                break
        return line[start:end].strip()

    def set_transcript(self, text: str) -> None:
        self.transcript = text
        self.contexts.clear()
        pieces = []
        cursor = 0
        for index, match in enumerate(WORD_PATTERN.finditer(text)):
            pieces.append(html.escape(text[cursor:match.start()]))
            word = match.group(0)
            sentence = self.sentence_at(text, match.start())
            self.contexts[index] = (word, sentence)
            saved = self.store.find(word) is not None
            color = "#16806c" if saved else "#59756a"
            weight = "600" if saved else "400"
            pieces.append(f'<a href="word:{index}" style="color:{color};font-weight:{weight}">{html.escape(word)}</a>')
            cursor = match.end()
        pieces.append(html.escape(text[cursor:]))
        self.transcript_view.setHtml(
            '<div style="white-space:pre-wrap; font-size:17px; line-height:1.65; color:#253832">'
            + "".join(pieces) + "</div>"
        )
        self.transcript_view.moveCursor(QTextCursor.MoveOperation.End)

    def on_word_clicked(self, url: QUrl) -> None:
        if url.scheme() != "word":
            return
        try:
            index = int(url.path() or url.toString().split(":", 1)[1])
        except (ValueError, IndexError):
            return
        context = self.contexts.get(index)
        if context is None:
            return
        word, sentence = context
        self.selected_word = word
        self.word_label.setObjectName("wordHeading")
        self.word_label.setText(word)
        self.source_sentence.setText(sentence)
        self.word_translation.clear()
        self.sentence_translation.clear()
        added = self.store.toggle(word, sentence)
        self.set_transcript(self.transcript)
        if self.vocabulary_window is not None:
            self.vocabulary_window.refresh()
        if added:
            self.word_translation.setText(TEXT[self.language]["saved_word"])
        else:
            self.word_translation.setText(TEXT[self.language]["removed_word"])
        if self.credentials is None:
            self.word_translation.setText(TEXT[self.language]["configure_first"])
            return
        self.start_translation(word, sentence, save_entry=added)

    def start_translation(self, word: str, sentence: str, save_entry: bool) -> None:
        if self.credentials is None:
            self.word_translation.setText(TEXT[self.language]["configure_first"])
            return
        if time.monotonic() - self.last_lookup < 1.0:
            self.word_translation.setText(TEXT[self.language]["wait_rate"])
            return
        self.last_lookup = time.monotonic()
        self.word_translation.setText(TEXT[self.language]["translating"])
        self.selected_word = word
        worker = TranslationWorker(word, sentence or word, self.credentials, self.language)
        worker.save_entry = save_entry
        worker.signals.finished.connect(self.translation_finished)
        worker.signals.finished.connect(lambda *_args, task=worker: self.workers.discard(task))
        self.workers.add(worker)
        self.pool.start(worker)

    def translation_finished(self, word: str, result: object, error: object) -> None:
        if error:
            if self.selected_word == word:
                self.word_translation.setText(TEXT[self.language]["translation_failed"].format(error=error))
            return
        if self.selected_word == word:
            self.word_translation.setText(result["word_translation"] or TEXT[self.language]["meaning_unavailable"])
            self.sentence_translation.setText(result["sentence_translation"])
        worker = next((item for item in self.workers if item.word == word), None)
        if worker is not None and getattr(worker, "save_entry", False):
            entry = self.store.find(word)
            if entry is not None:
                entry["word_translation"] = result["word_translation"]
                entry["sentence_translation"] = result["sentence_translation"]
                self.store.save()
                if self.vocabulary_window is not None:
                    self.vocabulary_window.refresh()

    def translate_existing(self, entry: dict[str, str]) -> None:
        self.word_label.setObjectName("wordHeading")
        self.word_label.setText(entry["word"])
        self.source_sentence.setText(entry.get("source_sentence", ""))
        self.start_translation(entry["word"], entry.get("source_sentence", "") or entry["word"], True)

    def configure_api(self) -> None:
        dialog = ApiSettingsDialog(self.language, self.credentials, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.credentials:
            self.credentials = dialog.credentials
            self.credential_store.save(*self.credentials)
            QMessageBox.information(self, TEXT[self.language]["settings_title"], TEXT[self.language]["settings_saved"])

    def open_vocabulary(self) -> None:
        if self.vocabulary_window is None:
            self.vocabulary_window = VocabularyWindow(self.store, self.language, self.translate_existing, self)
            self.vocabulary_window.finished.connect(lambda _result: setattr(self, "vocabulary_window", None))
        self.vocabulary_window.refresh()
        self.vocabulary_window.show()
        self.vocabulary_window.raise_()
        self.vocabulary_window.activateWindow()

    def export_vocabulary(self) -> None:
        if not self.store.entries:
            QMessageBox.information(self, APP_NAME, TEXT[self.language]["nothing_to_export"])
            return
        from PySide6.QtWidgets import QFileDialog

        path, _selected = QFileDialog.getSaveFileName(
            self, TEXT[self.language]["export_title"], "vocabulary.txt", TEXT[self.language]["export_filter"]
        )
        if not path:
            return
        columns = ("word", "word_translation", "source_sentence", "sentence_translation", "note", "added_at")
        headings = ("col_word", "col_meaning", "col_source", "col_translation", "col_note", "col_date")
        lines = ["\t".join(TEXT[self.language][heading] for heading in headings)]
        for entry in self.store.entries:
            lines.append("\t".join((entry.get(column, "") or "").replace("\t", " ").replace("\n", " ") for column in columns))
        Path(path).write_text("\n".join(lines), encoding="utf-8-sig")
        QMessageBox.information(self, APP_NAME, TEXT[self.language]["export_done"])


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")
    app.setWindowIcon(create_app_icon())
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())