# -*- coding: utf-8 -*-
"""
TextureAlphaMerger - 批量将透明图片合并到图片的Alpha通道

入口文件 (PySide6版本)
"""

import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer

from ui.main_window import TextureAlphaMergerApp, LIGHT_STYLE
from core.processor import ImageProcessor
from core.version import VERSION_STR
from core.updater import check_for_update


def main():
    """主入口"""
    # 创建应用
    app = QApplication(sys.argv)

    # 设置应用级别样式（包括QMessageBox等对话框）
    app.setStyleSheet(LIGHT_STYLE)

    # 创建主窗口
    window = TextureAlphaMergerApp()
    processor = ImageProcessor()

    # 设置窗口标题包含版本号
    window.setWindowTitle(f"TextureAlphaMerger {VERSION_STR}")

    def on_export(color_files, alpha_files, output_path, output_format, output_size):
        """导出回调"""
        if not color_files:
            QMessageBox.warning(window, "提示", "请添加彩色图文件")
            return

        # 调用处理器进行合并
        result = processor.merge_files_with_mapping(
            color_files=color_files,
            alpha_files=alpha_files,
            output_dir=output_path if output_path else None,
            output_format=output_format,
            output_size=output_size
        )

        # 显示结果
        msg = f"处理完成！\n合并Alpha: {result['success']} 个文件"
        if result['resized'] > 0:
            msg += f"\n缩放图片: {result['resized']} 个文件"
        if result['skipped'] > 0:
            msg += f"\n跳过: {result['skipped']} 个文件"
        if result['failed'] > 0:
            msg += f"\n失败: {result['failed']} 个文件"

        QMessageBox.information(window, "完成", msg)

    def check_update():
        """延迟检查更新（窗口显示后）"""
        check_for_update(window, silent=True)

    window.export_requested.connect(on_export)
    window.show()

    # 延迟1秒后检查更新（不阻塞启动）
    QTimer.singleShot(1000, check_update)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
