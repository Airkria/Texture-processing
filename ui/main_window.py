# -*- coding: utf-8 -*-
"""主窗口UI模块 - PySide6 现代化界面 (白色主题)"""

import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QPushButton, QComboBox, QLineEdit,
    QFileDialog, QMessageBox, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QRect, QPoint
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QColor, QFont, QPainter, QPolygon

# 支持的图片格式
SUPPORTED_FORMATS = {'.png', '.tga', '.bmp', '.jpg', '.jpeg'}

# ============================================================================
# 【Alpha匹配规则】
# ============================================================================
# 颜色图常见后缀（会被替换为Alpha后缀进行匹配）
COLOR_SUFFIXES = ['_D', '_Color', '_Albedo', '_BaseColor', '_Diffuse', '_Base', '_Col']
# Alpha图常见后缀
ALPHA_SUFFIXES = ['_A', '_Opacity']


def find_alpha_for_color(color_name_no_ext, dir_path):
    """
    智能匹配彩色图对应的Alpha图路径

    匹配策略：
    1. 追加方式：color_name + '_A' / '_Opacity'
    2. 后缀替换：color_name 中的颜色后缀替换为 Alpha 后缀
       例如：T_Grass_2K_D -> T_Grass_2K_A

    Args:
        color_name_no_ext: 彩色图文件名（不含扩展名）
        dir_path: 文件所在目录

    Returns:
        匹配到的Alpha图完整路径，未找到返回None
    """
    for ext in SUPPORTED_FORMATS:
        # 策略1：追加方式
        for alpha_suffix in ALPHA_SUFFIXES:
            alpha_path = os.path.join(dir_path, color_name_no_ext + alpha_suffix + ext)
            if os.path.exists(alpha_path):
                return alpha_path

        # 策略2：后缀替换方式
        for color_suffix in COLOR_SUFFIXES:
            if color_name_no_ext.endswith(color_suffix):
                base_name = color_name_no_ext[:-len(color_suffix)]
                for alpha_suffix in ALPHA_SUFFIXES:
                    alpha_path = os.path.join(dir_path, base_name + alpha_suffix + ext)
                    if os.path.exists(alpha_path):
                        return alpha_path

    return None


def is_alpha_match_color(alpha_name_no_ext, color_name_no_ext):
    """
    判断Alpha图是否与彩色图匹配（用于删除时联动）

    匹配规则（与find_alpha_for_color一致）：
    1. 追加方式：color_name + '_A' / '_Opacity' == alpha_name
    2. 后缀替换：color_name 的颜色后缀替换为 Alpha 后缀后 == alpha_name

    Args:
        alpha_name_no_ext: Alpha图文件名（不含扩展名）
        color_name_no_ext: 彩色图文件名（不含扩展名）

    Returns:
        True如果匹配，否则False
    """
    # 策略1：追加方式
    for alpha_suffix in ALPHA_SUFFIXES:
        if alpha_name_no_ext == color_name_no_ext + alpha_suffix:
            return True

    # 策略2：后缀替换方式
    for color_suffix in COLOR_SUFFIXES:
        if color_name_no_ext.endswith(color_suffix):
            base_name = color_name_no_ext[:-len(color_suffix)]
            for alpha_suffix in ALPHA_SUFFIXES:
                if alpha_name_no_ext == base_name + alpha_suffix:
                    return True

    return False

# ============================================================================
# 【样式参数 - 可在此处微调数值】
# ============================================================================

# 主背景色
COLOR_MAIN_BG = "#f8f9fa"

# ============================================================================
# 【窗口尺寸参数】
# ============================================================================
WINDOW_WIDTH = 510                          # 【修改1】窗口宽度 (原480，增加30px)
WINDOW_HEIGHT = 610                         # 窗口高度

# ============================================================================
# 【修改1】外部框架描边 - 彩色图框和Alpha图框的外边框
# ============================================================================
FILE_FRAME_BORDER_WIDTH = "2px"             # 外框边框宽度
FILE_FRAME_BORDER_COLOR = "#3498db"         # 外框边框颜色 (蓝色)
FILE_FRAME_BORDER_RADIUS = "6px"            # 外框圆角

FILE_FRAME_STYLE = f"""
QFrame {{
    background-color: #ffffff;
    border: {FILE_FRAME_BORDER_WIDTH} solid {FILE_FRAME_BORDER_COLOR};
    border-radius: {FILE_FRAME_BORDER_RADIUS};
}}
"""

# ============================================================================
# 【列表框样式】内部文件列表框
# ============================================================================
STYLE_LIST_BG = "#ffffff"                   # 列表背景色
STYLE_LIST_BORDER_WIDTH = "1px"             # 内部列表框边框宽度
STYLE_LIST_BORDER_COLOR = "#bdc3c7"         # 内部列表框边框颜色 (深灰色)
STYLE_LIST_ITEM_PADDING = "2px 4px"         # 文件名行高
STYLE_LIST_ITEM_MARGIN = "1px"              # 列表项间距
STYLE_LIST_SELECTED_BG = "#2980b9"          # 选中背景色
STYLE_LIST_SELECTED_FG = "#3a3a3a"          # 选中文字颜色
STYLE_LIST_HOVER_BG = "#eaf2f8"             # 悬停背景色

# ============================================================================
# 占位提示文字颜色
# ============================================================================
STYLE_PLACEHOLDER_COLOR = "#525252"         # 彩色图框提示文字颜色
STYLE_PLACEHOLDER_COLOR_ALPHA = "#525252"   # Alpha框提示文字颜色

# ============================================================================
# 【修改4】重置按钮参数
# ============================================================================
RESET_BUTTON_WIDTH = 40                     # 重置按钮宽度
RESET_BUTTON_FONT_SIZE = 25                 # 重置按钮图标大小

# ============================================================================
# 主样式表
# ============================================================================
LIGHT_STYLE = f"""
QMainWindow {{
    background-color: {COLOR_MAIN_BG};
}}
/* ========== 标签样式 ========== */
QLabel {{
    color: #333333;
    border: none;
    background: transparent;
    margin: 0px;
    padding: 0px;
}}
QLabel#titleLabel {{
    color: #2c3e50;
    font-size: 18px;
    font-weight: bold;
}}
QLabel#frameTitle {{
    color: #3498db;
    font-size: 12px;
    font-weight: bold;
    border: none;
    background: transparent;
}}
QLabel#descLabel {{
    color: #7f8c8d;
    font-size: 11px;
}}
/* ========== 列表框样式 ========== */
QListWidget {{
    background-color: {STYLE_LIST_BG};
    border: {STYLE_LIST_BORDER_WIDTH} solid {STYLE_LIST_BORDER_COLOR};
    border-radius: 4px;
    color: #333333;
    font-size: 11px;
    outline: none;
}}
QListWidget::item {{
    padding: {STYLE_LIST_ITEM_PADDING};
    border-radius: 3px;
    margin: {STYLE_LIST_ITEM_MARGIN};
}}
QListWidget::item:selected {{
    background-color: {STYLE_LIST_SELECTED_BG};
    color: {STYLE_LIST_SELECTED_FG};
}}
QListWidget::item:hover {{
    background-color: {STYLE_LIST_HOVER_BG};
}}
/* ========== 按钮样式 ========== */
QPushButton {{
    background-color: #ecf0f1;
    color: #333333;
    border: 1px solid #dce1e6;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 11px;
    font-family: "Microsoft YaHei UI";
}}
QPushButton:hover {{
    background-color: #3498db;
    color: #ffffff;
    border-color: #3498db;
}}
QPushButton:pressed {{
    background-color: #2980b9;
}}
QPushButton:disabled {{
    background-color: #f5f5f5;
    color: #bdc3c7;
    border-color: #e0e0e0;
}}
QPushButton#addBtn {{
    background-color: #3498db;
    color: #ffffff;
    border-color: #3498db;
}}
QPushButton#addBtn:hover {{
    background-color: #2980b9;
}}
QPushButton#removeBtn {{
    background-color: #e74c3c;
    color: #ffffff;
    border-color: #e74c3c;
}}
QPushButton#removeBtn:hover {{
    background-color: #c0392b;
}}
QPushButton#clearBtn {{
    background-color: #95a5a6;
    color: #ffffff;
    border-color: #95a5a6;
}}
QPushButton#clearBtn:hover {{
    background-color: #7f8c8d;
}}
QPushButton#exportBtn {{
    font-size: 13px;
    font-weight: bold;
    padding: 10px 25px;
}}
QPushButton#exportBtn:enabled {{
    background-color: #27ae60;
    color: #ffffff;
    border-color: #27ae60;
}}
QPushButton#exportBtn:enabled:hover {{
    background-color: #219a52;
}}
/* ========== 下拉框样式 ========== */
QComboBox {{
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #dce1e6;
    border-radius: 4px;
    padding: 5px 10px;
    padding-right: 25px;
    font-size: 11px;
    min-width: 60px;
}}
QComboBox:hover {{
    border-color: #bdc3c7;
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 20px;
    border: none;
    background: transparent;
}}
QComboBox::down-arrow {{
    width: 10px;
    height: 10px;
}}
QComboBox QAbstractItemView {{
    background-color: #ffffff;
    color: #333333;
    selection-background-color: #3498db;
    selection-color: #ffffff;
    border: 1px solid #dce1e6;
}}
/* ========== 输入框样式 ========== */
QLineEdit {{
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #dce1e6;
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 11px;
}}
QLineEdit:read-only {{
    background-color: #f8f9fa;
    color: #7f8c8d;
}}
/* ========== 对话框样式（QMessageBox等） ========== */
QMessageBox {{
    background-color: #ffffff;
}}
QMessageBox QLabel {{
    color: #333333;
    background-color: transparent;
}}
QMessageBox QPushButton {{
    background-color: #3498db;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 6px 20px;
    min-width: 80px;
}}
QMessageBox QPushButton:hover {{
    background-color: #2980b9;
}}
"""


class DropListWidget(QListWidget):
    """支持拖拽的列表控件"""

    files_dropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DropOnly)
        self.setSelectionMode(QListWidget.ExtendedSelection)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                ext = os.path.splitext(file_path)[1].lower()
                if ext in SUPPORTED_FORMATS:
                    files.append(file_path)
        if files:
            self.files_dropped.emit(files)
        event.acceptProposedAction()


class ArrowComboBox(QComboBox):
    """【修改3】自定义下拉框，在内部右侧绘制三角形箭头"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.arrow_color = QColor("#7f8c8d")  # 箭头颜色

    def paintEvent(self, event):
        # 先调用父类的绘制
        super().paintEvent(event)

        # 绘制三角形箭头
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.arrow_color)

        # 计算箭头位置（右侧中间）
        arrow_width = 8    # 箭头底部宽度
        arrow_height = 5   # 箭头高度
        margin_right = 10  # 右边距

        center_y = self.height() // 2
        right_x = self.width() - margin_right

        # 三角形的三个点
        triangle = QPolygon([
            QPoint(right_x - arrow_width // 2, center_y - arrow_height // 2),
            QPoint(right_x + arrow_width // 2, center_y - arrow_height // 2),
            QPoint(right_x, center_y + arrow_height // 2),
        ])
        painter.drawPolygon(triangle)


class ColorFileFrame(QFrame):
    """彩色图文件列表框架"""

    files_changed = Signal(list)
    files_removed = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.files = []
        self.setStyleSheet(FILE_FRAME_STYLE)
        self.setup_ui()
        self._show_placeholder()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # 标题
        title = QLabel("彩色图")
        title.setObjectName("frameTitle")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("QLabel { border: none; background: transparent; }")
        layout.addWidget(title)

        # 文件列表
        self.file_list = DropListWidget()
        self.file_list.files_dropped.connect(self.add_files)
        self.file_list.itemDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self.file_list, 1)

        # 占位提示
        self.placeholder_text = "拖拽文件到此或点击下方添加按钮"

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)

        self.add_btn = QPushButton("添加")
        self.add_btn.setObjectName("addBtn")
        self.add_btn.setFixedWidth(60)
        self.add_btn.clicked.connect(self._on_add_click)

        self.remove_btn = QPushButton("清除选定")
        self.remove_btn.setObjectName("removeBtn")
        self.remove_btn.setFixedWidth(70)
        self.remove_btn.clicked.connect(self.remove_selected)

        self.clear_btn = QPushButton("清空列表")
        self.clear_btn.setObjectName("clearBtn")
        self.clear_btn.setFixedWidth(70)
        self.clear_btn.clicked.connect(self.clear_all)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _show_placeholder(self):
        if not self.files:
            self.file_list.clear()
            item = QListWidgetItem(self.placeholder_text)
            item.setForeground(QColor(STYLE_PLACEHOLDER_COLOR))
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            item.setTextAlignment(Qt.AlignCenter)
            self.file_list.addItem(item)

    def _hide_placeholder(self):
        if self.file_list.count() == 1:
            item = self.file_list.item(0)
            if item and item.text() == self.placeholder_text:
                self.file_list.clear()

    def _on_add_click(self):
        files, _ = QFileDialog.getOpenFileNames(
            None,
            "选择图片文件",
            "",
            "图片文件 (*.png *.tga *.bmp *.jpg *.jpeg);;所有文件 (*.*)"
        )
        if files:
            self.add_files(files)

    def _on_double_click(self, item):
        if not self.files:
            self._on_add_click()

    def add_files(self, files):
        new_files = []
        for f in files:
            if f not in self.files:
                ext = os.path.splitext(f)[1].lower()
                if ext in SUPPORTED_FORMATS:
                    self.files.append(f)
                    new_files.append(f)

        if new_files:
            self._hide_placeholder()
            self.update_list()
            self.files_changed.emit(self.files)

    def remove_selected(self):
        selected_rows = sorted([self.file_list.row(item) for item in self.file_list.selectedItems()], reverse=True)
        if not selected_rows:
            return

        removed = []
        for row in selected_rows:
            removed.append(self.files.pop(row))

        self.update_list()
        if not self.files:
            self._show_placeholder()
        self.files_changed.emit(self.files)
        self.files_removed.emit(removed)

    def clear_all(self):
        if not self.files:
            return
        removed = self.files.copy()
        self.files.clear()
        self._show_placeholder()
        self.files_changed.emit([])
        self.files_removed.emit(removed)

    def update_list(self):
        self.file_list.clear()
        for f in self.files:
            self.file_list.addItem(os.path.basename(f))

    def get_files(self):
        return self.files


class AlphaDisplayFrame(QFrame):
    """Alpha图显示框架"""

    files_changed = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.files = []
        self.setStyleSheet(FILE_FRAME_STYLE)
        self.setup_ui()
        self._show_placeholder()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # 标题
        title = QLabel("Alpha图")
        title.setObjectName("frameTitle")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("QLabel { border: none; background: transparent; }")
        layout.addWidget(title)

        # 文件列表（只读）
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.NoSelection)
        layout.addWidget(self.file_list, 1)

        # 占位提示
        self.placeholder_text = "匹配的Alpha图将自动显示在这里"

        # 【修改2】Alpha图只做显示，去掉底部按钮区域

    def _show_placeholder(self):
        if not self.files:
            self.file_list.clear()
            item = QListWidgetItem(self.placeholder_text)
            item.setForeground(QColor(STYLE_PLACEHOLDER_COLOR_ALPHA))
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.file_list.addItem(item)

    def _hide_placeholder(self):
        if self.file_list.count() == 1:
            item = self.file_list.item(0)
            if item and item.text() == self.placeholder_text:
                self.file_list.clear()

    def set_files(self, files):
        self.files = files.copy()
        if self.files:
            self._hide_placeholder()
        self.update_list()
        if not self.files:
            self._show_placeholder()
        self.files_changed.emit(self.files)

    def remove_files_by_color(self, removed_color_files):
        alpha_to_remove = []
        for color_file in removed_color_files:
            name_no_ext = os.path.splitext(os.path.basename(color_file))[0]
            for alpha_file in self.files:
                alpha_name = os.path.splitext(os.path.basename(alpha_file))[0]
                # 使用智能匹配函数判断关联
                if is_alpha_match_color(alpha_name, name_no_ext):
                    alpha_to_remove.append(alpha_file)

        for f in alpha_to_remove:
            if f in self.files:
                self.files.remove(f)

        self.update_list()
        if not self.files:
            self._show_placeholder()
        self.files_changed.emit(self.files)

    def clear_all(self):
        self.files.clear()
        self._show_placeholder()
        self.files_changed.emit([])

    def update_list(self):
        self.file_list.clear()
        for f in self.files:
            item = QListWidgetItem(os.path.basename(f))
            item.setForeground(QColor("#27ae60"))
            self.file_list.addItem(item)

    def get_files(self):
        return self.files

    def get_files_mapped(self):
        return self.files.copy()


class TextureAlphaMergerApp(QMainWindow):
    """主应用程序窗口"""

    export_requested = Signal(list, list, str, str, int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TextureAlphaMerger")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)  # 【修改1】使用变量
        self.setStyleSheet(LIGHT_STYLE)

        self.color_files = []
        self.alpha_files = []
        self.alpha_files_mapped = []  # 【关键修复】完整映射列表（包含None）
        self.output_path = ""

        self.setup_ui()

    def setup_ui(self):
        # 主窗口居中
        from PySide6.QtGui import QScreen
        screen = QScreen.availableGeometry(self.screen())
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

        # 中央控件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(8)

        # 标题
        title = QLabel("TextureAlphaMerger")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # 说明文字
        desc1 = QLabel("将选定图片的Alpha图合并到图片的A通道中")
        desc1.setObjectName("descLabel")
        desc1.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(desc1)

        desc2 = QLabel("自动匹配：xx_A/xx_Opacity 或 xx_D->xx_A 后缀替换")
        desc2.setObjectName("descLabel")
        desc2.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(desc2)

        main_layout.addSpacing(5)

        # 彩色图和Alpha图并排区域
        files_layout = QHBoxLayout()
        files_layout.setSpacing(10)

        self.color_frame = ColorFileFrame()
        self.color_frame.files_changed.connect(self.on_color_files_changed)
        self.color_frame.files_removed.connect(self.on_color_files_removed)

        self.alpha_frame = AlphaDisplayFrame()
        self.alpha_frame.files_changed.connect(self.on_alpha_files_changed)

        files_layout.addWidget(self.color_frame, 1)
        files_layout.addWidget(self.alpha_frame, 1)
        main_layout.addLayout(files_layout, 1)

        # 保存格式行
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("保存格式:"))
        self.format_combo = ArrowComboBox()  # 【修改3】使用自定义带箭头的ComboBox
        self.format_combo.addItems(["PNG", "TGA", "BMP", "JPG"])  # 【逻辑1】添加JPG格式
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        main_layout.addLayout(format_layout)

        # 保存尺寸行
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("保存尺寸:"))
        self.size_combo = ArrowComboBox()  # 【修改3】使用自定义带箭头的ComboBox
        self.size_combo.addItems(["256", "512", "1024", "2048", "4096"])
        self.size_combo.setCurrentText("2048")
        size_layout.addWidget(self.size_combo)
        size_layout.addStretch()
        main_layout.addLayout(size_layout)

        # 保存目录行
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("保存目录:"))
        self.output_entry = QLineEdit("源路径文件夹")
        self.output_entry.setReadOnly(True)
        self.output_entry.setFixedWidth(180)
        output_layout.addWidget(self.output_entry)

        browse_btn = QPushButton("···")
        browse_btn.setFixedSize(35, 28)
        browse_btn.clicked.connect(self.select_output_folder)
        output_layout.addWidget(browse_btn)

        # 【修改4】重置按钮 - 使用圆圈箭头图标
        reset_btn = QPushButton("↺")
        reset_btn.setObjectName("clearBtn")
        reset_btn.setFixedWidth(RESET_BUTTON_WIDTH)
        reset_btn.setFont(QFont("Segoe UI Symbol", RESET_BUTTON_FONT_SIZE))
        reset_btn.clicked.connect(self.reset_output_folder)
        output_layout.addWidget(reset_btn)

        output_layout.addStretch()
        main_layout.addLayout(output_layout)

        # 导出按钮
        main_layout.addSpacing(10)
        export_layout = QHBoxLayout()
        export_layout.addStretch()

        self.export_btn = QPushButton("导出合成")
        self.export_btn.setObjectName("exportBtn")
        self.export_btn.setFixedSize(120, 38)
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.on_export)
        export_layout.addWidget(self.export_btn)

        main_layout.addLayout(export_layout)

    def on_color_files_changed(self, files):
        self.color_files = files
        self.auto_detect_alpha()
        self.update_export_btn()

    def on_color_files_removed(self, removed_files):
        self.alpha_frame.remove_files_by_color(removed_files)

    def auto_detect_alpha(self):
        alpha_files_full = []  # 完整列表，与color_files一一对应（None表示无匹配）
        alpha_files_display = []  # 用于显示的列表（只包含找到的文件）

        for color_file in self.color_files:
            dir_path = os.path.dirname(color_file)
            name_no_ext = os.path.splitext(os.path.basename(color_file))[0]

            # 使用智能匹配函数
            alpha_path = find_alpha_for_color(name_no_ext, dir_path)
            if alpha_path:
                alpha_files_full.append(alpha_path)
                alpha_files_display.append(alpha_path)
            else:
                alpha_files_full.append(None)  # 【关键修复】用None占位，保持一一对应

        # 保存完整映射用于导出
        self.alpha_files_mapped = alpha_files_full
        # 显示时只显示找到的文件
        self.alpha_frame.set_files(alpha_files_display)

    def on_alpha_files_changed(self, files):
        self.alpha_files = files
        self.update_export_btn()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(None, "选择保存目录")
        if folder:
            self.output_path = folder
            self.output_entry.setText(folder)

    def reset_output_folder(self):
        self.output_path = ""
        self.output_entry.setText("源路径文件夹")

    def update_export_btn(self):
        # 【逻辑修改】只要有彩色图就可以导出（无Alpha图时会进行缩放处理）
        self.export_btn.setEnabled(bool(self.color_files))

    def on_export(self):
        # 【关键修复】使用完整的映射列表（包含None占位符，与color_files一一对应）
        self.export_requested.emit(
            self.color_files,
            self.alpha_files_mapped,
            self.output_path,
            self.format_combo.currentText(),
            int(self.size_combo.currentText())
        )
