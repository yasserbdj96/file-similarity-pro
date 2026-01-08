from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont
import os
import warnings

# Suppress PIL warnings
warnings.filterwarnings("ignore", category=UserWarning, module="PIL.Image")

IMAGE_EXT = (".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif", ".svg", ".ico")
TEXT_EXT = (".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".xml", ".log", ".csv")

class PreviewWindow(QDialog):
    file_deleted = Signal()
    
    def __init__(self, group, group_number, dark_mode=False, parent=None):
        super().__init__(parent)
        self.group = group
        self.files = [f for f in group['files'] if os.path.exists(f)]
        self.dark_mode = dark_mode
        self.setWindowTitle(f"Preview Group {group_number} - {len(self.files)} Files")
        self.resize(1400, 900)
        
        # Increase Qt image allocation limit
        os.environ['QT_IMAGEIO_MAXALLOC'] = '512'
        
        self.apply_theme()
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Info section
        info_text = f"<b>Group {group_number}</b> - Similarity: {group['similarity']:.1f}% - Type: {group['type']}"
        info_label = QLabel(info_text)
        info_label.setMaximumHeight(40)
        info_label.setStyleSheet(self.get_info_style())
        main_layout.addWidget(info_label)
        
        # Determine file type and create appropriate preview
        if self.files and self.files[0].lower().endswith(IMAGE_EXT):
            self.create_image_preview(main_layout)
        elif self.files and self.files[0].lower().endswith(TEXT_EXT):
            self.create_text_preview(main_layout)
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
                QDialog {
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                }
                QLabel {
                    color: #e0e0e0;
                }
                QTextEdit {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    border: 1px solid #3d3d3d;
                }
                QTableWidget {
                    background-color: #2d2d2d;
                    alternate-background-color: #262626;
                    color: #e0e0e0;
                    gridline-color: #3d3d3d;
                }
                QTableWidget::item {
                    padding: 5px;
                    border-bottom: 1px solid #3d3d3d;
                }
                QTableWidget::item:selected {
                    background-color: #0d7377;
                    color: white;
                }
                QHeaderView::section {
                    background-color: #262626;
                    color: #e0e0e0;
                    padding: 8px;
                    border: 1px solid #3d3d3d;
                    font-weight: bold;
                }
                QCheckBox {
                    color: #e0e0e0;
                    padding: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    background-color: #2d2d2d;
                    border: 1px solid #3d3d3d;
                }
                QCheckBox::indicator:checked {
                    background-color: #0d7377;
                    border: 1px solid #14a085;
                }
                QPushButton {
                    background-color: #0d7377;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #14a085;
                }
                QPushButton:pressed {
                    background-color: #0a5f63;
                }
                QPushButton:disabled {
                    background-color: #3d3d3d;
                    color: #777777;
                }
                QScrollArea {
                    background-color: #1e1e1e;
                    border: none;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #f5f5f5;
                    color: #333333;
                }
                QLabel {
                    color: #333333;
                }
                QTextEdit {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #cccccc;
                }
                QTableWidget {
                    background-color: white;
                    alternate-background-color: #f9f9f9;
                    color: #333333;
                    gridline-color: #dddddd;
                }
                QTableWidget::item {
                    padding: 5px;
                    border-bottom: 1px solid #eeeeee;
                }
                QTableWidget::item:selected {
                    background-color: #4a90e2;
                    color: white;
                }
                QHeaderView::section {
                    background-color: #e9e9e9;
                    color: #333333;
                    padding: 8px;
                    border: 1px solid #dddddd;
                    font-weight: bold;
                }
                QCheckBox {
                    color: #333333;
                    padding: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QPushButton {
                    background-color: #4a90e2;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3a7bc8;
                }
                QPushButton:pressed {
                    background-color: #2c6bb6;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #666666;
                }
                QScrollArea {
                    background-color: #f0f0f0;
                    border: none;
                }
            """)
    
    def get_info_style(self):
        if self.dark_mode:
            return """
                font-size: 14px; 
                padding: 8px 12px;
                background: #0d4d4f; 
                color: #14a085; 
                border-radius: 5px; 
                border: 1px solid #14a085;
            """
        else:
            return """
                font-size: 14px; 
                padding: 8px 12px;
                background: #e3f2fd; 
                color: #1565c0; 
                border-radius: 5px; 
                border: 1px solid #bbdefb;
            """
    
    def get_delete_button_style(self):
        if self.dark_mode:
            return """
                QPushButton {
                    background-color: #d32f2f;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #f44336;
                }
                QPushButton:pressed {
                    background-color: #b71c1c;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #f44336;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
                QPushButton:pressed {
                    background-color: #b71c1c;
                }
            """
    
    def create_image_preview(self, main_layout):
        """Create side-by-side image comparison with large image handling"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        container.setStyleSheet(f"background-color: {'#1e1e1e' if self.dark_mode else '#f0f0f0'};")
        grid = QGridLayout()
        
        cols = min(3, len(self.files))  # Max 3 images per row
        self.checkboxes = []
        
        for idx, file_path in enumerate(self.files):
            row = idx // cols
            col = idx % cols
            
            # Container for each image
            image_widget = QWidget()
            image_layout = QVBoxLayout()
            
            # Checkbox
            checkbox = QCheckBox(f"Select for deletion")
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {'#e0e0e0' if self.dark_mode else '#333333'};
                    background-color: {'#2d2d2d' if self.dark_mode else 'white'};
                    padding: 8px;
                    border-radius: 3px;
                    border: 1px solid {'#3d3d3d' if self.dark_mode else '#ddd'};
                }}
            """)
            self.checkboxes.append((checkbox, file_path))
            image_layout.addWidget(checkbox)
            
            # Image label
            image_label = QLabel()
            pixmap = self.load_image_safely(file_path)
            
            if pixmap and not pixmap.isNull():
                # Scale to reasonable preview size
                scaled_pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
                image_label.setAlignment(Qt.AlignCenter)
                image_label.setStyleSheet(f"background-color: {'#1a1a1a' if self.dark_mode else '#2c2c2c'}; padding: 5px;")
            else:
                image_label.setText("⚠️ Cannot load image\n(Too large or corrupted)")
                image_label.setStyleSheet(f"""
                    color: {'#ff6b6b' if self.dark_mode else '#d32f2f'};
                    background-color: {'#3d1f1f' if self.dark_mode else '#ffebee'};
                    padding: 20px;
                    font-weight: bold;
                    border: 1px solid {'#5d2f2f' if self.dark_mode else '#ffcdd2'};
                    border-radius: 3px;
                """)
                image_label.setAlignment(Qt.AlignCenter)
            
            image_layout.addWidget(image_label)
            
            # File info
            file_info = QTextEdit()
            file_info.setReadOnly(True)
            file_info.setMaximumHeight(120)
            file_info.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {'#2d2d2d' if self.dark_mode else '#ffffff'};
                    color: {'#e0e0e0' if self.dark_mode else '#333333'};
                    border: 1px solid {'#3d3d3d' if self.dark_mode else '#ddd'};
                    border-radius: 3px;
                    padding: 8px;
                }}
            """)
            
            try:
                size = os.path.getsize(file_path)
                stat = os.stat(file_path)
                
                # Get image dimensions if possible
                if pixmap and not pixmap.isNull():
                    dimensions = f"{pixmap.width()} x {pixmap.height()} px"
                else:
                    dimensions = "Unknown"
                
                info_text = f"""
<b>File:</b> {os.path.basename(file_path)}<br>
<b>Path:</b> {file_path}<br>
<b>Size:</b> {self.format_size(size)}<br>
<b>Modified:</b> {self.format_time(stat.st_mtime)}<br>
<b>Dimensions:</b> {dimensions}
                """
                file_info.setHtml(info_text)
            except Exception as e:
                file_info.setPlainText(f"Error reading file info: {str(e)}")
            
            image_layout.addWidget(file_info)
            
            image_widget.setLayout(image_layout)
            image_widget.setStyleSheet(f"""
                border: 2px solid {'#3d3d3d' if self.dark_mode else '#ddd'};
                border-radius: 5px;
                padding: 10px;
                background: {'#2d2d2d' if self.dark_mode else 'white'};
            """)
            
            grid.addWidget(image_widget, row, col)
        
        container.setLayout(grid)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
    
    def load_image_safely(self, file_path):
        """Safely load image with size limits"""
        try:
            # Check file size first
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            # Skip very large files
            if file_size_mb > 100:  # 100 MB limit
                return None
            
            pixmap = QPixmap(file_path)
            
            # If pixmap is null or too large, return None
            if pixmap.isNull() or pixmap.width() > 10000 or pixmap.height() > 10000:
                return None
            
            return pixmap
            
        except Exception as e:
            return None
    
    def create_text_preview(self, main_layout):
        """Create side-by-side text comparison"""
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet(f"QSplitter::handle {{ background-color: {'#3d3d3d' if self.dark_mode else '#cccccc'}; }}")
        self.checkboxes = []
        
        for file_path in self.files:
            # Container for each text file
            file_widget = QWidget()
            file_layout = QVBoxLayout()
            file_widget.setStyleSheet(f"""
                background-color: {'#2d2d2d' if self.dark_mode else '#f9f9f9'};
                border: 1px solid {'#3d3d3d' if self.dark_mode else '#ddd'};
                border-radius: 3px;
                margin: 2px;
            """)
            
            # Checkbox
            checkbox = QCheckBox(f"Select for deletion")
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {'#e0e0e0' if self.dark_mode else '#333333'};
                    background-color: {'#262626' if self.dark_mode else 'white'};
                    padding: 8px;
                    border-bottom: 1px solid {'#3d3d3d' if self.dark_mode else '#eee'};
                }}
            """)
            self.checkboxes.append((checkbox, file_path))
            file_layout.addWidget(checkbox)
            
            # File name label
            name_label = QLabel(f"<b>{os.path.basename(file_path)}</b>")
            name_label.setStyleSheet(f"""
                background: {'#0d4d4f' if self.dark_mode else '#e8f4fd'};
                color: {'#14a085' if self.dark_mode else '#0d47a1'};
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
                border-bottom: 1px solid {'#14a085' if self.dark_mode else '#bbdefb'};
            """)
            file_layout.addWidget(name_label)
            
            # Text content
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setFont(QFont("Consolas", 10))
            text_edit.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {'#1e1e1e' if self.dark_mode else 'white'};
                    color: {'#e0e0e0' if self.dark_mode else '#333333'};
                    border: none;
                    padding: 8px;
                }}
            """)
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(50000)
                    if len(content) >= 50000:
                        content += "\n\n... (file truncated for preview)"
                    text_edit.setPlainText(content)
            except Exception as e:
                text_edit.setPlainText(f"Error reading file: {str(e)}")
                text_edit.setStyleSheet(f"""
                    QTextEdit {{
                        background-color: {'#3d1f1f' if self.dark_mode else '#ffebee'};
                        color: {'#ff6b6b' if self.dark_mode else '#c62828'};
                        border: none;
                        padding: 8px;
                    }}
                """)
            
            file_layout.addWidget(text_edit)
            
            # File info
            try:
                size = os.path.getsize(file_path)
                stat = os.stat(file_path)
                info_text = f"Path: {file_path} | Size: {self.format_size(size)} | Modified: {self.format_time(stat.st_mtime)}"
            except:
                info_text = f"Path: {file_path}"
            
            info_label = QLabel(info_text)
            info_label.setStyleSheet(f"""
                font-size: 10px;
                color: {'#999' if self.dark_mode else '#666'};
                padding: 8px;
                background-color: {'#262626' if self.dark_mode else '#f5f5f5'};
                border-top: 1px solid {'#3d3d3d' if self.dark_mode else '#eee'};
            """)
            file_layout.addWidget(info_label)
            
            file_widget.setLayout(file_layout)
            splitter.addWidget(file_widget)
        
        main_layout.addWidget(splitter)
    
    def create_generic_preview(self, main_layout):
        """Create generic file list preview"""
        table = QTableWidget(len(self.files), 5)
        table.setHorizontalHeaderLabels(["Select", "File Name", "Path", "Size", "Modified"])
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        table.setAlternatingRowColors(True)
        
        self.checkboxes = []
        
        for idx, file_path in enumerate(self.files):
            # Checkbox
            checkbox = QCheckBox()
            self.checkboxes.append((checkbox, file_path))
            table.setCellWidget(idx, 0, checkbox)
            
            # File info
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
        
        table.verticalHeader().setDefaultSectionSize(40)
        main_layout.addWidget(table)
    
    def delete_selected_files(self):
        """Delete files that are checked"""
        files_to_delete = [path for checkbox, path in self.checkboxes if checkbox.isChecked()]
        
        if not files_to_delete:
            QMessageBox.warning(self, "No Selection", "Please select files to delete")
            return
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Deletion")
        msg_box.setText(f"Are you sure you want to delete {len(files_to_delete)} file(s)?")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        if msg_box.exec() == QMessageBox.Yes:
            deleted = 0
            errors = []
            
            for file_path in files_to_delete:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        deleted += 1
                        self.files.remove(file_path)
                except Exception as e:
                    errors.append(f"{os.path.basename(file_path)}: {str(e)}")
            
            if errors:
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Errors")
                error_msg.setText(f"Deleted {deleted} file(s). Errors occurred:")
                error_msg.setDetailedText("\n".join(errors))
                error_msg.setIcon(QMessageBox.Warning)
                error_msg.exec()
            else:
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Success")
                success_msg.setText(f"Successfully deleted {deleted} file(s)")
                success_msg.setIcon(QMessageBox.Information)
                success_msg.exec()
            
            self.file_deleted.emit()
            
            if len(self.files) < 2:
                QMessageBox.information(self, "Group Empty", "This group now has less than 2 files. Closing preview.")
                self.close()
            else:
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