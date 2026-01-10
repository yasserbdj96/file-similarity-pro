from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Signal, QRect, QSize
from PySide6.QtGui import QPixmap, QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QPainter, QTextFormat
import os
import warnings
import re
from config import config

warnings.filterwarnings("ignore", category=UserWarning, module="PIL.Image")

IMAGE_EXT = (".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif", ".svg", ".ico")
TEXT_EXT = (".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".xml", ".log", ".csv", ".java", ".cpp", ".c", ".h", ".rs", ".go")

class LineNumberArea(QWidget):
    """Line number display for text editor"""
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class CodeEditor(QPlainTextEdit):
    """Enhanced text editor with line numbers and syntax highlighting"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)
        
        # Set font
        font = QFont("Consolas", config.get_int('TEXT_FONT_SIZE', 10))
        self.setFont(font)
        self.setTabStopDistance(config.get_int('TEXT_TAB_SIZE', 4) * self.fontMetrics().horizontalAdvance(' '))

    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        
        # Get colors based on theme
        bg_color = QColor("#2d2d2d") if self.property("dark_mode") else QColor("#f0f0f0")
        text_color = QColor("#888888") if self.property("dark_mode") else QColor("#666666")
        
        painter.fillRect(event.rect(), bg_color)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(text_color)
                painter.drawText(0, int(top), self.line_number_area.width() - 5, 
                               self.fontMetrics().height(), Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

class PythonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Python code"""
    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.highlighting_rules = []

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6" if dark_mode else "#0000FF"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            '\\bdef\\b', '\\bclass\\b', '\\bif\\b', '\\belse\\b', '\\belif\\b',
            '\\bfor\\b', '\\bwhile\\b', '\\breturn\\b', '\\bimport\\b', '\\bfrom\\b',
            '\\bas\\b', '\\btry\\b', '\\bexcept\\b', '\\bfinally\\b', '\\bwith\\b',
            '\\blambda\\b', '\\byield\\b', '\\bin\\b', '\\band\\b', '\\bor\\b', '\\bnot\\b'
        ]
        for word in keywords:
            self.highlighting_rules.append((re.compile(word), keyword_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178" if dark_mode else "#A31515"))
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.highlighting_rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955" if dark_mode else "#008000"))
        self.highlighting_rules.append((re.compile(r'#[^\n]*'), comment_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8" if dark_mode else "#098658"))
        self.highlighting_rules.append((re.compile(r'\b[0-9]+\.?[0-9]*\b'), number_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)

class JavaScriptHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JavaScript/JSON"""
    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.highlighting_rules = []

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6" if dark_mode else "#0000FF"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            '\\bvar\\b', '\\blet\\b', '\\bconst\\b', '\\bfunction\\b', '\\breturn\\b',
            '\\bif\\b', '\\belse\\b', '\\bfor\\b', '\\bwhile\\b', '\\bswitch\\b',
            '\\bcase\\b', '\\bbreak\\b', '\\bcontinue\\b', '\\btry\\b', '\\bcatch\\b',
            '\\bthrow\\b', '\\bnew\\b', '\\bthis\\b', '\\btrue\\b', '\\bfalse\\b', '\\bnull\\b'
        ]
        for word in keywords:
            self.highlighting_rules.append((re.compile(word), keyword_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178" if dark_mode else "#A31515"))
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.highlighting_rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955" if dark_mode else "#008000"))
        self.highlighting_rules.append((re.compile(r'//[^\n]*'), comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)

class PreviewWindow(QDialog):
    file_deleted = Signal()
    
    def __init__(self, group, group_number, dark_mode=False, parent=None):
        super().__init__(parent)
        self.group = group
        self.files = [f for f in group['files'] if os.path.exists(f)]
        self.dark_mode = dark_mode
        
        width = config.get_int('PREVIEW_WIDTH', 1400)
        height = config.get_int('PREVIEW_HEIGHT', 900)
        self.setWindowTitle(f"Preview Group {group_number} - {len(self.files)} Files")
        self.resize(width, height)
        
        self.apply_theme()
        self.setup_ui(group_number)
    
    def setup_ui(self, group_number):
        main_layout = QVBoxLayout()
        
        # Info section
        info_text = f"<b>Group {group_number}</b> - Similarity: {self.group['similarity']:.1f}% - Type: {self.group['type']}"
        info_label = QLabel(info_text)
        info_label.setMaximumHeight(40)
        info_label.setStyleSheet(self.get_info_style())
        main_layout.addWidget(info_label)
        
        # Determine file type and create appropriate preview
        if self.files and self.files[0].lower().endswith(IMAGE_EXT):
            self.create_image_preview(main_layout)
        elif self.files and self.files[0].lower().endswith(TEXT_EXT):
            self.create_enhanced_text_preview(main_layout)
        else:
            self.create_generic_preview(main_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.delete_selected_btn = QPushButton("🗑️ Delete Selected")
        self.delete_selected_btn.clicked.connect(self.delete_selected_files)
        self.delete_selected_btn.setStyleSheet(self.get_delete_button_style())
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.delete_selected_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QDialog { background-color: #1e1e1e; color: #e0e0e0; }
                QLabel { color: #e0e0e0; }
                QPushButton {
                    background-color: #0d7377; color: white; border: none;
                    padding: 8px 16px; border-radius: 4px; font-weight: bold;
                }
                QPushButton:hover { background-color: #14a085; }
                QPushButton:pressed { background-color: #0a5f63; }
                QScrollArea { background-color: #1e1e1e; border: none; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background-color: #f5f5f5; color: #333333; }
                QLabel { color: #333333; }
                QPushButton {
                    background-color: #4a90e2; color: white; border: none;
                    padding: 8px 16px; border-radius: 4px; font-weight: bold;
                }
                QPushButton:hover { background-color: #3a7bc8; }
                QPushButton:pressed { background-color: #2c6bb6; }
                QScrollArea { background-color: #f0f0f0; border: none; }
                QCheckBox { color: #333333; }
                QTextEdit { background-color: white; color: #333333; border: 1px solid #ccc; }
                QPlainTextEdit { background-color: white; color: #333333; border: 1px solid #ccc; }
            """)
    
    def get_info_style(self):
        if self.dark_mode:
            return "font-size: 14px; padding: 8px 12px; background: #0d4d4f; color: #14a085; border-radius: 5px; border: 1px solid #14a085;"
        else:
            return "font-size: 14px; padding: 8px 12px; background: #e3f2fd; color: #1565c0; border-radius: 5px; border: 1px solid #bbdefb;"
    
    def get_delete_button_style(self):
        return "QPushButton { background-color: #f44336; color: white; } QPushButton:hover { background-color: #d32f2f; }"
    
    def create_enhanced_text_preview(self, main_layout):
        """Create side-by-side text comparison with syntax highlighting and line numbers"""
        # Create scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        container.setStyleSheet(f"background-color: {'#1e1e1e' if self.dark_mode else '#f0f0f0'};")
        grid_layout = QVBoxLayout()
        grid_layout.setSpacing(10)
        
        self.checkboxes = []
        
        # Color palette for different files
        colors = [
            ("#2d1f1f" if self.dark_mode else "#fff3e0"),
            ("#1f2d1f" if self.dark_mode else "#e8f5e9"),
            ("#1f1f2d" if self.dark_mode else "#e3f2fd"),
            ("#2d1f2d" if self.dark_mode else "#f3e5f5"),
        ]
        
        # Create rows with 2 files each
        for row_start in range(0, len(self.files), 2):
            row_splitter = QSplitter(Qt.Horizontal)
            
            # Add first file in this row
            for offset in range(2):
                idx = row_start + offset
                if idx >= len(self.files):
                    break
                
                file_path = self.files[idx]
                file_widget = QWidget()
                file_layout = QVBoxLayout()
                bg_color = colors[idx % len(colors)]
                file_widget.setStyleSheet(f"background-color: {bg_color}; border: 2px solid {'#3d3d3d' if self.dark_mode else '#ddd'}; border-radius: 5px;")
                
                # Checkbox
                checkbox = QCheckBox(f"Select for deletion")
                checkbox.setStyleSheet(f"color: {'#e0e0e0' if self.dark_mode else '#333333'}; padding: 8px; font-weight: bold;")
                self.checkboxes.append((checkbox, file_path))
                file_layout.addWidget(checkbox)
                
                # File name with language badge
                lang = self.detect_language(file_path)
                name_label = QLabel(f"<b>{os.path.basename(file_path)}</b> <span style='background: {'#0d7377' if self.dark_mode else '#4a90e2'}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 10px;'>{lang}</span>")
                name_label.setStyleSheet(f"background: {'#0d4d4f' if self.dark_mode else '#e8f4fd'}; color: {'#14a085' if self.dark_mode else '#0d47a1'}; padding: 8px; font-size: 12px; border-bottom: 2px solid {'#14a085' if self.dark_mode else '#4a90e2'};")
                file_layout.addWidget(name_label)
                
                # Code editor with line numbers
                text_edit = CodeEditor()
                text_edit.setReadOnly(True)
                text_edit.setProperty("dark_mode", self.dark_mode)
                text_edit.setStyleSheet(f"""
                    CodeEditor {{
                        background-color: {'#1e1e1e' if self.dark_mode else '#ffffff'};
                        color: {'#e0e0e0' if self.dark_mode else '#333333'};
                        border: none; padding: 5px;
                    }}
                """)
                
                try:
                    max_chars = config.get_int('TEXT_PREVIEW_CHARS', 50000)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(max_chars)
                        if len(content) >= max_chars:
                            content += "\n\n... (file truncated for preview)"
                        text_edit.setPlainText(content)
                    
                    # Apply syntax highlighting
                    self.apply_syntax_highlighting(text_edit, lang)
                    
                except Exception as e:
                    text_edit.setPlainText(f"Error reading file: {str(e)}")
                    text_edit.setStyleSheet(f"background-color: {'#3d1f1f' if self.dark_mode else '#ffebee'}; color: {'#ff6b6b' if self.dark_mode else '#c62828'};")
                
                file_layout.addWidget(text_edit)
                
                # File stats
                try:
                    size = os.path.getsize(file_path)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = sum(1 for _ in f)
                    stat = os.stat(file_path)
                    info_text = f"📏 {self.format_size(size)} | 📝 {lines} lines | 🕒 {self.format_time(stat.st_mtime)}\n📄 {file_path}"
                except:
                    info_text = f"📄 {file_path}"
                
                info_label = QLabel(info_text)
                info_label.setStyleSheet(f"font-size: 10px; color: {'#999' if self.dark_mode else '#666'}; padding: 8px; background-color: {'#262626' if self.dark_mode else '#f5f5f5'}; border-top: 2px solid {'#3d3d3d' if self.dark_mode else '#eee'};")
                file_layout.addWidget(info_label)
                
                file_widget.setLayout(file_layout)
                row_splitter.addWidget(file_widget)
            
            grid_layout.addWidget(row_splitter)
        
        container.setLayout(grid_layout)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
    
    def detect_language(self, file_path):
        """Detect programming language from file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        lang_map = {
            '.py': 'Python', '.js': 'JavaScript', '.json': 'JSON', '.html': 'HTML',
            '.css': 'CSS', '.xml': 'XML', '.md': 'Markdown', '.txt': 'Text',
            '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.h': 'C/C++',
            '.rs': 'Rust', '.go': 'Go', '.log': 'Log', '.csv': 'CSV'
        }
        return lang_map.get(ext, 'Text')
    
    def apply_syntax_highlighting(self, text_edit, lang):
        """Apply syntax highlighting based on language"""
        if lang in ['Python']:
            PythonHighlighter(text_edit.document(), self.dark_mode)
        elif lang in ['JavaScript', 'JSON']:
            JavaScriptHighlighter(text_edit.document(), self.dark_mode)
    
    def create_image_preview(self, main_layout):
        """Create enhanced image preview with better layout"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        container.setStyleSheet(f"background-color: {'#1e1e1e' if self.dark_mode else '#f0f0f0'};")
        grid = QGridLayout()
        grid.setSpacing(15)
        
        cols = min(3, len(self.files))
        self.checkboxes = []
        
        preview_size = config.get_int('IMAGE_PREVIEW_SIZE', 400)
        
        for idx, file_path in enumerate(self.files):
            row = idx // cols
            col = idx % cols
            
            image_widget = QWidget()
            image_layout = QVBoxLayout()
            image_widget.setStyleSheet(f"border: 2px solid {'#0d7377' if self.dark_mode else '#4a90e2'}; border-radius: 8px; padding: 10px; background: {'#2d2d2d' if self.dark_mode else 'white'};")
            
            # Checkbox
            checkbox = QCheckBox(f"Select for deletion")
            checkbox.setStyleSheet(f"color: {'#e0e0e0' if self.dark_mode else '#333333'}; font-weight: bold; padding: 5px;")
            self.checkboxes.append((checkbox, file_path))
            image_layout.addWidget(checkbox)
            
            # Image display
            image_label = QLabel()
            pixmap = self.load_image_safely(file_path)
            
            if pixmap and not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(preview_size, preview_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
                image_label.setAlignment(Qt.AlignCenter)
                image_label.setStyleSheet(f"background-color: {'#1a1a1a' if self.dark_mode else '#f9f9f9'}; padding: 10px; border-radius: 5px;")
            else:
                image_label.setText("⚠️ Cannot load image\n(Too large or corrupted)")
                image_label.setStyleSheet(f"color: {'#ff6b6b' if self.dark_mode else '#d32f2f'}; background-color: {'#3d1f1f' if self.dark_mode else '#ffebee'}; padding: 20px; font-weight: bold; border: 1px dashed {'#ff6b6b' if self.dark_mode else '#d32f2f'}; border-radius: 5px;")
                image_label.setAlignment(Qt.AlignCenter)
            
            image_layout.addWidget(image_label)
            
            # File info card
            info_card = QTextEdit()
            info_card.setReadOnly(True)
            info_card.setMaximumHeight(140)
            info_card.setStyleSheet(f"background-color: {'#262626' if self.dark_mode else '#fafafa'}; color: {'#e0e0e0' if self.dark_mode else '#333333'}; border: 1px solid {'#3d3d3d' if self.dark_mode else '#eee'}; border-radius: 5px; padding: 10px;")
            
            try:
                size = os.path.getsize(file_path)
                stat = os.stat(file_path)
                dimensions = f"{pixmap.width()} x {pixmap.height()} px" if pixmap and not pixmap.isNull() else "Unknown"
                
                info_text = f"""
<div style='line-height: 1.5;'>
<b style='color: {'#14a085' if self.dark_mode else '#4a90e2'};'>📁 File:</b> {os.path.basename(file_path)}<br>
<b style='color: {'#14a085' if self.dark_mode else '#4a90e2'};'>📏 Size:</b> {self.format_size(size)}<br>
<b style='color: {'#14a085' if self.dark_mode else '#4a90e2'};'>📐 Dimensions:</b> {dimensions}<br>
<b style='color: {'#14a085' if self.dark_mode else '#4a90e2'};'>🕒 Modified:</b> {self.format_time(stat.st_mtime)}<br>
<b style='color: {'#14a085' if self.dark_mode else '#4a90e2'};'>📂 Path:</b> <span style='font-size: 9px;'>{file_path}</span>
</div>
                """
                info_card.setHtml(info_text)
            except Exception as e:
                info_card.setPlainText(f"Error reading file info: {str(e)}")
            
            image_layout.addWidget(info_card)
            image_widget.setLayout(image_layout)
            grid.addWidget(image_widget, row, col)
        
        container.setLayout(grid)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
    
    def load_image_safely(self, file_path):
        """Safely load image with size limits"""
        try:
            max_size_mb = config.get_int('MAX_IMAGE_SIZE_MB', 100)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            if file_size_mb > max_size_mb:
                return None
            
            pixmap = QPixmap(file_path)
            if pixmap.isNull() or pixmap.width() > 10000 or pixmap.height() > 10000:
                return None
            
            return pixmap
        except:
            return None
    
    def create_generic_preview(self, main_layout):
        """Create generic file list preview"""
        table = QTableWidget(len(self.files), 5)
        table.setHorizontalHeaderLabels(["Select", "File Name", "Path", "Size", "Modified"])
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        table.setAlternatingRowColors(True)
        table.setStyleSheet(f"""
            QTableWidget {{ background-color: {'#2d2d2d' if self.dark_mode else 'white'}; color: {'#e0e0e0' if self.dark_mode else '#333333'}; }}
            QHeaderView::section {{ background-color: {'#262626' if self.dark_mode else '#f0f0f0'}; color: {'#e0e0e0' if self.dark_mode else '#333333'}; padding: 8px; font-weight: bold; }}
        """)
        
        self.checkboxes = []
        
        for idx, file_path in enumerate(self.files):
            checkbox = QCheckBox()
            self.checkboxes.append((checkbox, file_path))
            table.setCellWidget(idx, 0, checkbox)
            
            table.setItem(idx, 1, QTableWidgetItem(os.path.basename(file_path)))
            table.setItem(idx, 2, QTableWidgetItem(file_path))
            
            try:
                size = os.path.getsize(file_path)
                table.setItem(idx, 3, QTableWidgetItem(self.format_size(size)))
                stat = os.stat(file_path)
                table.setItem(idx, 4, QTableWidgetItem(self.format_time(stat.st_mtime)))
            except:
                table.setItem(idx, 3, QTableWidgetItem("N/A"))
                table.setItem(idx, 4, QTableWidgetItem("N/A"))
        
        main_layout.addWidget(table)
    
    def delete_selected_files(self):
        """Delete files that are checked"""
        files_to_delete = [path for checkbox, path in self.checkboxes if checkbox.isChecked()]
        
        if not files_to_delete:
            QMessageBox.warning(self, "No Selection", "Please select files to delete")
            return
        
        total_size = sum(os.path.getsize(f) for f in files_to_delete if os.path.exists(f))
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirm Deletion")
        msg.setText(f"Delete {len(files_to_delete)} file(s)?")
        msg.setInformativeText(f"Total size: {self.format_size(total_size)}")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        if msg.exec() == QMessageBox.Yes:
            deleted = 0
            for file_path in files_to_delete:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        deleted += 1
                        self.files.remove(file_path)
                except:
                    pass
            
            QMessageBox.information(self, "Success", f"Deleted {deleted} file(s)")
            self.file_deleted.emit()
            
            if len(self.files) < 2:
                self.close()
    
    def format_size(self, bytes_size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.2f} TB"
    
    def format_time(self, timestamp):
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')