# -*- coding: utf-8 -*-
"""自动更新模块"""

import os
import sys
import json
import urllib.request
import urllib.error
import tempfile
import subprocess
from typing import Optional, Tuple

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QProgressBar, QMessageBox, QDialogButtonBox
)
from PySide6.QtCore import QThread, Signal, Qt

from core.version import __version__, VERSION_STR, APP_NAME


# GitHub 仓库信息
GITHUB_REPO = "Airkria/Texture-processing"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


class UpdateInfo:
    """更新信息"""
    def __init__(self):
        self.version: str = ""
        self.download_url: str = ""
        self.changelog: str = ""
        self.release_date: str = ""


class UpdateChecker(QThread):
    """后台检查更新的线程"""
    finished = Signal(object)  # UpdateInfo or None
    error = Signal(str)

    def run(self):
        try:
            # 创建请求，添加 User-Agent（GitHub API 要求）
            request = urllib.request.Request(
                GITHUB_API_URL,
                headers={"User-Agent": f"{APP_NAME}-{VERSION_STR}"}
            )

            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))

            info = UpdateInfo()
            info.version = data.get('tag_name', '')
            info.release_date = data.get('published_at', '')[:10]
            info.changelog = data.get('body', '无更新说明')

            # 查找 Windows 版本的下载链接
            for asset in data.get('assets', []):
                if asset['name'].endswith('.exe'):
                    info.download_url = asset['browser_download_url']
                    break

            self.finished.emit(info)

        except urllib.error.HTTPError as e:
            self.error.emit(f"网络错误: {e.code}")
        except urllib.error.URLError as e:
            self.error.emit(f"连接失败: {e.reason}")
        except Exception as e:
            self.error.emit(f"检查更新失败: {str(e)}")


class UpdateDownloader(QThread):
    """后台下载更新的线程"""
    progress = Signal(int)  # 下载进度百分比
    finished = Signal(str)  # 下载完成，返回文件路径
    error = Signal(str)

    def __init__(self, download_url: str, version: str):
        super().__init__()
        self.download_url = download_url
        self.version = version

    def run(self):
        try:
            # 下载到临时目录
            temp_dir = tempfile.gettempdir()
            filename = f"{APP_NAME}_{self.version}.exe"
            filepath = os.path.join(temp_dir, filename)

            request = urllib.request.Request(
                self.download_url,
                headers={"User-Agent": f"{APP_NAME}-{VERSION_STR}"}
            )

            with urllib.request.urlopen(request, timeout=30) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                chunk_size = 8192

                with open(filepath, 'wb') as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.progress.emit(progress)

            self.finished.emit(filepath)

        except Exception as e:
            self.error.emit(f"下载失败: {str(e)}")


class UpdateDialog(QDialog):
    """更新提示对话框"""

    def __init__(self, update_info: UpdateInfo, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.downloader = None
        self.download_path = None

        self.setWindowTitle("发现新版本")
        self.setMinimumWidth(450)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 版本信息
        title = QLabel(f"新版本 {self.update_info.version} 已发布")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        date_label = QLabel(f"发布日期: {self.update_info.release_date}")
        date_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(date_label)

        # 更新日志
        changelog_title = QLabel("更新内容:")
        changelog_title.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(changelog_title)

        changelog = QTextEdit()
        changelog.setPlainText(self.update_info.changelog)
        changelog.setReadOnly(True)
        changelog.setMaximumHeight(200)
        changelog.setStyleSheet("background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 4px;")
        layout.addWidget(changelog)

        # 进度条（初始隐藏）
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        layout.addWidget(self.progress_bar)

        # 按钮
        button_box = QDialogButtonBox()
        self.update_btn = QPushButton("立即更新")
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        cancel_btn = QPushButton("稍后提醒")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #bdc3c7;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
        """)
        button_box.addButton(self.update_btn, QDialogButtonBox.AcceptRole)
        button_box.addButton(cancel_btn, QDialogButtonBox.RejectRole)
        self.update_btn.clicked.connect(self.start_download)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def start_download(self):
        """开始下载更新"""
        if not self.update_info.download_url:
            QMessageBox.warning(self, "错误", "未找到下载链接")
            return

        self.update_btn.setEnabled(False)
        self.update_btn.setText("下载中...")
        self.progress_bar.setVisible(True)

        self.downloader = UpdateDownloader(
            self.update_info.download_url,
            self.update_info.version
        )
        self.downloader.progress.connect(self.on_progress)
        self.downloader.finished.connect(self.on_download_finished)
        self.downloader.error.connect(self.on_download_error)
        self.downloader.start()

    def on_progress(self, percent: int):
        self.progress_bar.setValue(percent)

    def on_download_finished(self, filepath: str):
        self.download_path = filepath
        self.progress_bar.setVisible(False)
        self.update_btn.setText("下载完成")

        # 询问是否立即安装
        reply = QMessageBox.question(
            self,
            "下载完成",
            "更新已下载完成，是否立即安装？\n程序将关闭并替换为新版本。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            self.install_update()
        else:
            self.accept()

    def on_download_error(self, error_msg: str):
        self.progress_bar.setVisible(False)
        self.update_btn.setEnabled(True)
        self.update_btn.setText("重试下载")
        QMessageBox.critical(self, "下载失败", error_msg)

    def install_update(self):
        """安装更新（替换当前程序并重启）"""
        if not self.download_path or not os.path.exists(self.download_path):
            QMessageBox.critical(self, "错误", "下载文件不存在")
            return

        try:
            # 获取当前程序路径
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
            else:
                QMessageBox.warning(self, "提示", "当前为开发模式，无法自动更新")
                return

            # 创建更新脚本（批处理）
            batch_content = f"""@echo off
echo 正在更新 {APP_NAME}...
timeout /t 2 /nobreak > nul
copy /y "{self.download_path}" "{current_exe}"
if %errorlevel% equ 0 (
    echo 更新完成，正在启动...
    start "" "{current_exe}"
) else (
    echo 更新失败，请手动下载新版本
    pause
)
del "%~f0"
"""
            batch_path = os.path.join(tempfile.gettempdir(), "update_batchmerger.bat")
            with open(batch_path, 'w', encoding='utf-8') as f:
                f.write(batch_content)

            # 启动更新脚本并退出当前程序
            subprocess.Popen(['cmd', '/c', batch_path], shell=True)
            sys.exit(0)

        except Exception as e:
            QMessageBox.critical(self, "更新失败", f"无法安装更新: {str(e)}")


def check_for_update(parent=None, silent: bool = False):
    """
    检查更新

    Args:
        parent: 父窗口
        silent: 静默模式（无更新时不提示）

    Returns:
        bool: 是否发现新版本
    """
    checker = UpdateChecker()

    result = [None]
    error_msg = [None]

    def on_finished(info: UpdateInfo):
        result[0] = info

    def on_error(msg: str):
        error_msg[0] = msg

    checker.finished.connect(on_finished)
    checker.error.connect(on_error)
    checker.start()
    checker.wait()

    if error_msg[0]:
        if not silent:
            QMessageBox.warning(parent, "检查更新失败", error_msg[0])
        return False

    if result[0]:
        info = result[0]
        # 比较版本号
        current = tuple(map(int, __version__.split('.')))
        new_version = info.version.lstrip('v')
        try:
            new = tuple(map(int, new_version.split('.')))
        except ValueError:
            if not silent:
                QMessageBox.warning(parent, "版本解析失败", f"无法解析版本号: {info.version}")
            return False

        if new > current:
            # 有新版本，显示更新对话框
            dialog = UpdateDialog(info, parent)
            dialog.exec()
            return True
        else:
            if not silent:
                QMessageBox.information(parent, "已是最新版本", f"当前版本 {VERSION_STR} 已是最新版本")
            return False

    return False
