from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QSettings, QTimer
from PySide6.QtGui import QColor
from utils.worker import ScanWorker
from ui.preview_window import PreviewWindow
from config import config
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Similarity Pro - Fast Duplicate Finder")
        
        width = config.get_int('WINDOW_WIDTH', 1200)
        height = config.get_int('WINDOW_HEIGHT', 750)
        self.resize(width, height)
        
        # State management
        self.duplicate_groups = []
        self.all_groups = []
        self.worker = None
        self.group_counter = 0
        self.is_scanning = False
        
        # Load settings from config
        self.settings = QSettings("FileSimilarityPro", "DuplicateFinder")
        self.dark_mode = config.get_bool('DARK_MODE', False)
        self.load_recent_paths()
        
        # UI setup
        self.setup_ui()
        self.apply_theme()
        
        # Auto-scroll timer
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.auto_scroll_table)
        self.scroll_timer.setInterval(500)

    def load_recent_paths(self):
        """Load recently scanned paths"""
        recent = self.settings.value("recent_paths", [])
        self.recent_paths = recent if isinstance(recent, list) else []

    def save_recent_path(self, path):
        """Save a recently scanned path"""
        if path in self.recent_paths:
            self.recent_paths.remove(path)
        self.recent_paths.insert(0, path)
        max_recent = config.get_int('MAX_RECENT_PATHS', 10)
        self.recent_paths = self.recent_paths[:max_recent]
        self.settings.setValue("recent_paths", self.recent_paths)
        self.update_path_completer()

    def update_path_completer(self):
        """Update path input auto-complete"""
        if self.recent_paths:
            completer = QCompleter(self.recent_paths)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.path_input.setCompleter(completer)

    def setup_ui(self):
        # Top toolbar
        toolbar = QHBoxLayout()
        
        # Theme toggle
        self.theme_btn = QPushButton("☀️" if self.dark_mode else "🌙")
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.setFixedSize(45, 35)
        self.theme_btn.setToolTip("Toggle Dark/Light Theme")
        
        # Path input
        path_label = QLabel("Folder:")
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select or paste folder path...")
        self.update_path_completer()
        
        browse_btn = QPushButton("📁 Browse")
        browse_btn.clicked.connect(self.browse)
        browse_btn.setFixedWidth(100)
        
        # Action buttons
        self.scan_btn = QPushButton("🔍 Scan")
        self.scan_btn.clicked.connect(self.start_scan)
        self.scan_btn.setFixedWidth(100)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.clicked.connect(self.stop_scan)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setFixedWidth(100)
        
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.clicked.connect(self.show_settings_dialog)
        self.settings_btn.setFixedWidth(100)
        
        toolbar.addWidget(path_label)
        toolbar.addWidget(self.path_input, 1)
        toolbar.addWidget(browse_btn)
        toolbar.addWidget(self.scan_btn)
        toolbar.addWidget(self.stop_btn)
        toolbar.addWidget(self.settings_btn)
        toolbar.addWidget(self.theme_btn)

        # Progress section
        progress_layout = QVBoxLayout()
        self.status_label = QLabel("Ready to scan")
        self.status_label.setStyleSheet("font-size: 13px;")
        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setFormat("%p% - %v/%m")
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress)

        # Summary stats
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 8px;")
        self.summary_label.setWordWrap(True)

        # Filter controls
        filter_group = self.create_filter_group()

        # Results table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Group", "File Path", "Size", "Similarity"])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.table.doubleClicked.connect(self.open_preview)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        table_label = QLabel("💡 Double-click to preview • Select rows to delete • Right-click for options")
        table_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")

        # Action buttons
        button_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("👁️ Preview")
        self.preview_btn.clicked.connect(self.preview_selected_group)
        self.preview_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("🗑️ Delete Selected")
        self.delete_btn.clicked.connect(self.delete_selected)
        self.delete_btn.setEnabled(False)
        
        self.export_btn = QPushButton("📄 Export")
        self.export_btn.clicked.connect(self.export_results)
        self.export_btn.setEnabled(False)
        
        button_layout.addWidget(self.preview_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(toolbar)
        main_layout.addLayout(progress_layout)
        main_layout.addWidget(self.summary_label)
        main_layout.addWidget(filter_group)
        main_layout.addWidget(table_label)
        main_layout.addWidget(self.table, 1)
        main_layout.addLayout(button_layout)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_filter_group(self):
        """Create filter controls"""
        filter_group = QGroupBox("🔍 Filter Results")
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["All Files", "Images", "Documents", "Videos", "Audio", "Archives", "Code", "Other"])
        self.type_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.type_combo)
        
        filter_layout.addWidget(QLabel("Min Similarity:"))
        self.similarity_spin = QSpinBox()
        self.similarity_spin.setRange(50, 100)
        self.similarity_spin.setValue(config.get_int('DEFAULT_MIN_SIMILARITY', 70))
        self.similarity_spin.setSuffix("%")
        self.similarity_spin.valueChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.similarity_spin)
        
        filter_layout.addWidget(QLabel("Min Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(0, 10000)
        self.size_spin.setValue(0)
        self.size_spin.setSuffix(" KB")
        self.size_spin.valueChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.size_spin)
        
        filter_layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Filename or path...")
        self.search_box.textChanged.connect(self.apply_filters)
        self.search_box.setClearButtonEnabled(True)
        filter_layout.addWidget(self.search_box, 1)
        
        filter_group.setLayout(filter_layout)
        return filter_group

    def show_settings_dialog(self):
        """Show settings dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout()
        tabs = QTabWidget()
        
        # Ignore Patterns Tab
        ignore_tab = self.create_ignore_patterns_tab()
        tabs.addTab(ignore_tab, "Ignore Patterns")
        
        # Scan Settings Tab
        scan_tab = self.create_scan_settings_tab()
        tabs.addTab(scan_tab, "Scan Settings")
        
        # Performance Tab
        perf_tab = self.create_performance_tab()
        tabs.addTab(perf_tab, "Performance")
        
        # UI Settings Tab
        ui_tab = self.create_ui_settings_tab()
        tabs.addTab(ui_tab, "UI Settings")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(lambda: self.save_settings(dialog))
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.clicked.connect(self.reset_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        if self.dark_mode:
            dialog.setStyleSheet(self.get_dark_dialog_style())
        
        dialog.exec()

    def create_ignore_patterns_tab(self):
        """Create ignore patterns settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        info = QLabel("<b>Ignore Patterns</b><br>Enter file patterns to ignore (one per line). Use * as wildcard.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        self.patterns_edit = QTextEdit()
        patterns = config.get_list('IGNORE_PATTERNS')
        self.patterns_edit.setPlainText("\n".join(patterns))
        layout.addWidget(self.patterns_edit)
        
        tab.setLayout(layout)
        return tab

    def create_scan_settings_tab(self):
        """Create scan settings tab"""
        tab = QWidget()
        layout = QFormLayout()
        
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setRange(0, 100000)
        self.min_size_spin.setValue(config.get_int('MIN_FILE_SIZE', 0))
        self.min_size_spin.setSuffix(" KB")
        layout.addRow("Minimum File Size:", self.min_size_spin)
        
        self.min_similarity_spin = QSpinBox()
        self.min_similarity_spin.setRange(50, 100)
        self.min_similarity_spin.setValue(config.get_int('DEFAULT_MIN_SIMILARITY', 70))
        self.min_similarity_spin.setSuffix("%")
        layout.addRow("Default Min Similarity:", self.min_similarity_spin)
        
        self.image_sim_check = QCheckBox("Enable image similarity detection")
        self.image_sim_check.setChecked(config.get_bool('ENABLE_IMAGE_SIMILARITY', True))
        layout.addRow("", self.image_sim_check)
        
        tab.setLayout(layout)
        return tab

    def create_performance_tab(self):
        """Create performance settings tab"""
        tab = QWidget()
        layout = QFormLayout()
        
        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(1, 16)
        self.workers_spin.setValue(config.get_int('MAX_WORKERS', 4))
        layout.addRow("Max Worker Threads:", self.workers_spin)
        
        self.batch_spin = QSpinBox()
        self.batch_spin.setRange(5, 100)
        self.batch_spin.setValue(config.get_int('BATCH_SIZE', 10))
        layout.addRow("Batch Size:", self.batch_spin)
        
        self.parallel_check = QCheckBox("Enable parallel processing")
        self.parallel_check.setChecked(config.get_bool('ENABLE_PARALLEL_PROCESSING', True))
        layout.addRow("", self.parallel_check)
        
        tab.setLayout(layout)
        return tab

    def create_ui_settings_tab(self):
        """Create UI settings tab"""
        tab = QWidget()
        layout = QFormLayout()
        
        self.preview_size_spin = QSpinBox()
        self.preview_size_spin.setRange(200, 1000)
        self.preview_size_spin.setValue(config.get_int('IMAGE_PREVIEW_SIZE', 400))
        self.preview_size_spin.setSuffix(" px")
        layout.addRow("Image Preview Size:", self.preview_size_spin)
        
        self.text_font_spin = QSpinBox()
        self.text_font_spin.setRange(8, 20)
        self.text_font_spin.setValue(config.get_int('TEXT_FONT_SIZE', 10))
        layout.addRow("Text Editor Font Size:", self.text_font_spin)
        
        self.auto_scroll_check = QCheckBox("Auto-scroll during scan")
        self.auto_scroll_check.setChecked(config.get_bool('AUTO_SCROLL', True))
        layout.addRow("", self.auto_scroll_check)
        
        tab.setLayout(layout)
        return tab

    def save_settings(self, dialog):
        """Save all settings to config"""
        # Ignore patterns
        patterns = [p.strip() for p in self.patterns_edit.toPlainText().split("\n") if p.strip()]
        config.set_list('IGNORE_PATTERNS', patterns)
        
        # Scan settings
        config.set('MIN_FILE_SIZE', self.min_size_spin.value())
        config.set('DEFAULT_MIN_SIMILARITY', self.min_similarity_spin.value())
        config.set('ENABLE_IMAGE_SIMILARITY', self.image_sim_check.isChecked())
        
        # Performance
        config.set('MAX_WORKERS', self.workers_spin.value())
        config.set('BATCH_SIZE', self.batch_spin.value())
        config.set('ENABLE_PARALLEL_PROCESSING', self.parallel_check.isChecked())
        
        # UI
        config.set('IMAGE_PREVIEW_SIZE', self.preview_size_spin.value())
        config.set('TEXT_FONT_SIZE', self.text_font_spin.value())
        config.set('AUTO_SCROLL', self.auto_scroll_check.isChecked())
        
        config.save()
        QMessageBox.information(dialog, "Success", "Settings saved successfully!")
        dialog.accept()

    def reset_settings(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(self, "Reset Settings", 
                                     "Reset all settings to defaults?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            config.config = config.defaults.copy()
            config.save()
            QMessageBox.information(self, "Success", "Settings reset. Please restart the application.")

    def get_dark_dialog_style(self):
        return """
            QDialog, QWidget { background-color: #1e1e1e; color: #e0e0e0; }
            QLabel { color: #e0e0e0; }
            QTextEdit { background-color: #2d2d2d; color: #e0e0e0; border: 1px solid #3d3d3d; }
            QTabWidget::pane { border: 1px solid #3d3d3d; background: #1e1e1e; }
            QTabBar::tab { background: #2d2d2d; color: #e0e0e0; padding: 8px 16px; }
            QTabBar::tab:selected { background: #0d7377; }
            QSpinBox, QLineEdit { background-color: #2d2d2d; color: #e0e0e0; border: 1px solid #3d3d3d; padding: 5px; }
            QCheckBox { color: #e0e0e0; }
            QPushButton { background-color: #0d7377; color: white; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #14a085; }
        """
    
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        self.dark_mode = not self.dark_mode
        config.set('DARK_MODE', self.dark_mode)
        config.save()
        self.apply_theme()
        self.theme_btn.setText("☀️" if self.dark_mode else "🌙")

    def apply_theme(self):
        """Apply current theme to UI"""
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #1e1e1e; color: #e0e0e0; }
                QLineEdit, QSpinBox, QComboBox { 
                    background-color: #2d2d2d; border: 1px solid #3d3d3d; 
                    padding: 6px; color: #e0e0e0; border-radius: 4px; 
                }
                QPushButton { 
                    background-color: #0d7377; color: white; border: none; 
                    padding: 8px 12px; border-radius: 4px; font-weight: bold; 
                }
                QPushButton:hover { background-color: #14a085; }
                QPushButton:disabled { background-color: #3d3d3d; color: #777; }
                QTableWidget { 
                    background-color: #2d2d2d; alternate-background-color: #262626; 
                    color: #e0e0e0; gridline-color: #3d3d3d; 
                }
                QTableWidget::item:selected { background-color: #0d7377; color: white; }
                QHeaderView::section { 
                    background-color: #262626; color: #e0e0e0; padding: 8px; 
                    border: 1px solid #3d3d3d; font-weight: bold; 
                }
                QProgressBar { 
                    border: 1px solid #3d3d3d; border-radius: 4px; 
                    background-color: #2d2d2d; text-align: center; color: #e0e0e0; 
                }
                QProgressBar::chunk { background-color: #0d7377; }
                QGroupBox { 
                    color: #e0e0e0; border: 1px solid #3d3d3d; border-radius: 6px; 
                    margin-top: 12px; padding-top: 12px; font-weight: bold;
                }
            """)
            self.summary_label.setStyleSheet("font-weight: bold; color: #14a085; font-size: 14px; padding: 8px;")
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #f5f5f5; color: #333333; }
                QLineEdit, QSpinBox, QComboBox { 
                    background-color: white; border: 1px solid #ccc; 
                    padding: 6px; border-radius: 4px; 
                }
                QPushButton { 
                    background-color: #4a90e2; color: white; border: none; 
                    padding: 8px 12px; border-radius: 4px; font-weight: bold; 
                }
                QPushButton:hover { background-color: #3a7bc8; }
                QPushButton:disabled { background-color: #ccc; color: #666; }
                QTableWidget { 
                    background-color: white; alternate-background-color: #f9f9f9; 
                    color: #333333; gridline-color: #e0e0e0; 
                }
                QTableWidget::item:selected { background-color: #4a90e2; color: white; }
                QHeaderView::section { 
                    background-color: #f0f0f0; color: #333333; padding: 8px; font-weight: bold; 
                }
                QProgressBar { 
                    border: 1px solid #ccc; border-radius: 4px; 
                    background-color: #f0f0f0; text-align: center; color: #333333; 
                }
                QProgressBar::chunk { background-color: #4a90e2; }
                QGroupBox { 
                    color: #333333; border: 1px solid #ccc; border-radius: 6px; 
                    margin-top: 12px; padding-top: 12px; font-weight: bold;
                }
                QLabel { color: #333333; }
                QTabWidget::pane { border: 1px solid #ccc; background: #f5f5f5; }
                QTabBar::tab { background: #f0f0f0; color: #333333; padding: 8px 16px; }
                QTabBar::tab:selected { background: #4a90e2; color: white; }
                QTextEdit { background-color: white; color: #333333; border: 1px solid #ccc; }
            """)
            self.summary_label.setStyleSheet("font-weight: bold; color: #0066cc; font-size: 14px; padding: 8px;")

    def browse(self):
        """Browse for folder"""
        path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if path:
            self.path_input.setText(path)

    def start_scan(self):
        """Start scanning for duplicates"""
        path = self.path_input.text().strip()
        
        if not path or not os.path.isdir(path):
            QMessageBox.warning(self, "Invalid Path", "Please select a valid folder")
            return
        
        self.save_recent_path(path)
        
        # Reset UI
        self.table.setRowCount(0)
        self.table.setSortingEnabled(False)
        self.scan_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.delete_btn.setEnabled(False)
        self.preview_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.summary_label.setText("🔎 Scanning...")
        self.duplicate_groups = []
        self.all_groups = []
        self.group_counter = 0
        self.progress.setValue(0)
        self.is_scanning = True
        
        # Get settings
        patterns = config.get_list('IGNORE_PATTERNS')
        min_size = config.get_int('MIN_FILE_SIZE', 0)
        
        # Start worker
        self.worker = ScanWorker(path, patterns, min_size)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.status.connect(self.status_label.setText)
        self.worker.group_found.connect(self.add_group_realtime)
        self.worker.finished.connect(self.scan_finished)
        self.worker.error.connect(self.scan_error)
        self.worker.start()
        
        if config.get_bool('AUTO_SCROLL', True):
            self.scroll_timer.start()

    def stop_scan(self):
        """Stop current scan"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.status_label.setText("⏹ Stopping...")
            self.stop_btn.setEnabled(False)
            self.scroll_timer.stop()

    def scan_error(self, error_msg):
        """Handle scan error"""
        QMessageBox.critical(self, "Error", error_msg)
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.is_scanning = False

    def add_group_realtime(self, group):
        """Add newly found group"""
        self.all_groups.append(group)
        QTimer.singleShot(100, self.apply_filters)

    def auto_scroll_table(self):
        """Auto-scroll to show new results"""
        if self.is_scanning and self.table.rowCount() > 0:
            self.table.scrollToBottom()

    def apply_filters(self):
        """Apply active filters"""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        self.duplicate_groups = []
        self.group_counter = 0
        
        file_type = self.type_combo.currentText()
        min_similarity = self.similarity_spin.value()
        min_size_kb = self.size_spin.value()
        search_text = self.search_box.text().lower()
        
        for group in self.all_groups:
            if group['similarity'] < min_similarity:
                continue
            if not self.matches_file_type(group, file_type):
                continue
            if group.get('size', 0) / 1024 < min_size_kb:
                continue
            if search_text and not any(search_text in f.lower() for f in group['files']):
                continue
            
            self.add_group_to_table(group)
        
        self.table.setSortingEnabled(True)
        self.update_summary()

    def matches_file_type(self, group, file_type):
        """Check if group matches file type filter"""
        if file_type == "All Files":
            return True
        
        files = group['files']
        type_map = {
            "Images": ('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.gif', '.svg'),
            "Documents": ('.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.md'),
            "Videos": ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.webm'),
            "Audio": ('.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'),
            "Archives": ('.zip', '.rar', '.7z', '.tar', '.gz'),
            "Code": ('.py', '.js', '.java', '.cpp', '.c', '.html', '.css', '.json'),
        }
        
        if file_type in type_map:
            return any(f.lower().endswith(type_map[file_type]) for f in files)
        
        # Other
        all_ext = set()
        for exts in type_map.values():
            all_ext.update(exts)
        return not any(f.lower().endswith(tuple(all_ext)) for f in files)

    def add_group_to_table(self, group):
        """Add group to results table"""
        self.duplicate_groups.append(group)
        group_idx = self.group_counter
        self.group_counter += 1
        
        colors = [
            QColor(255, 200, 200), QColor(200, 255, 200), QColor(200, 200, 255),
            QColor(255, 255, 200), QColor(255, 200, 255), QColor(200, 255, 255),
        ] if not self.dark_mode else [
            QColor(180, 100, 100), QColor(100, 180, 100), QColor(100, 100, 180),
            QColor(180, 180, 100), QColor(180, 100, 180), QColor(100, 180, 180),
        ]
        
        color = colors[group_idx % len(colors)]
        group_name = f"Group {group_idx + 1}"
        
        for file_path in group['files']:
            r = self.table.rowCount()
            self.table.insertRow(r)
            
            group_item = QTableWidgetItem(group_name)
            group_item.setData(Qt.UserRole, group_idx)
            group_item.setBackground(color)
            self.table.setItem(r, 0, group_item)
            
            path_item = QTableWidgetItem(file_path)
            path_item.setBackground(color)
            path_item.setToolTip(file_path)
            self.table.setItem(r, 1, path_item)
            
            try:
                size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                size_item = QTableWidgetItem(self.format_size(size))
                size_item.setData(Qt.UserRole, size)
                size_item.setBackground(color)
                self.table.setItem(r, 2, size_item)
            except:
                self.table.setItem(r, 2, QTableWidgetItem("N/A"))
            
            sim_text = f"{group['similarity']:.1f}%"
            if group['type'] == 'exact':
                sim_text = "100% ✓"
            sim_item = QTableWidgetItem(sim_text)
            sim_item.setData(Qt.UserRole, group['similarity'])
            sim_item.setBackground(color)
            self.table.setItem(r, 3, sim_item)

    def update_summary(self):
        """Update summary label"""
        if self.duplicate_groups:
            total_files = sum(len(g['files']) for g in self.duplicate_groups)
            total_wasted = sum(g['wasted_space'] for g in self.duplicate_groups)
            self.summary_label.setText(
                f"📊 <b>{len(self.duplicate_groups)}</b> of <b>{len(self.all_groups)}</b> groups • "
                f"<b>{total_files}</b> files • 💾 <b>{self.format_size(total_wasted)}</b> recoverable"
            )
            self.delete_btn.setEnabled(True)
            self.preview_btn.setEnabled(True)
            self.export_btn.setEnabled(True)
        else:
            self.summary_label.setText("✅ No matches" if self.all_groups else "✅ No duplicates")
            self.delete_btn.setEnabled(False)
            self.preview_btn.setEnabled(False)
            self.export_btn.setEnabled(False)

    def scan_finished(self, groups):
        """Handle scan completion"""
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.is_scanning = False
        self.scroll_timer.stop()
        
        if not self.all_groups:
            self.status_label.setText("✅ Complete - No duplicates")
        else:
            self.status_label.setText(f"✅ Found {len(self.all_groups)} groups")

    def format_size(self, bytes_size):
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.2f} PB"
    
    def open_preview(self, index):
        """Open preview on double-click"""
        row = index.row()
        group_idx = self.table.item(row, 0).data(Qt.UserRole)
        self.show_group_preview(group_idx)
    
    def preview_selected_group(self):
        """Preview selected group"""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            group_idx = self.table.item(row, 0).data(Qt.UserRole)
            self.show_group_preview(group_idx)
    
    def show_group_preview(self, group_idx):
        """Show preview window"""
        if group_idx < len(self.duplicate_groups):
            group = self.duplicate_groups[group_idx]
            preview = PreviewWindow(group, group_idx + 1, self.dark_mode, self)
            preview.file_deleted.connect(self.refresh_table)
            preview.show()
    
    def on_selection_changed(self):
        """Update buttons on selection change"""
        has_selection = len(self.table.selectedItems()) > 0
        self.delete_btn.setEnabled(has_selection)
        self.preview_btn.setEnabled(has_selection)
    
    def refresh_table(self):
        """Refresh table after deletion"""
        updated = []
        for group in self.all_groups:
            existing = [f for f in group['files'] if os.path.exists(f)]
            if len(existing) >= 2:
                group['files'] = existing
                try:
                    size = os.path.getsize(existing[0])
                    group['wasted_space'] = size * (len(existing) - 1)
                    group['size'] = size
                    updated.append(group)
                except:
                    pass
        
        self.all_groups = updated
        self.apply_filters()
    
    def delete_selected(self):
        """Delete selected files"""
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Select files to delete")
            return
        
        files_to_delete = []
        for row in selected_rows:
            path = self.table.item(row, 1).text()
            if os.path.exists(path):
                files_to_delete.append(path)
        
        if not files_to_delete:
            return
        
        total_size = sum(os.path.getsize(f) for f in files_to_delete)
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirm Deletion")
        msg.setText(f"Delete {len(files_to_delete)} file(s)?")
        msg.setInformativeText(f"Size: {self.format_size(total_size)}")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        if msg.exec() == QMessageBox.Yes:
            deleted = 0
            for path in files_to_delete:
                try:
                    os.remove(path)
                    deleted += 1
                except:
                    pass
            
            QMessageBox.information(self, "Success", f"Deleted {deleted} file(s)")
            self.refresh_table()
    
    def export_results(self):
        """Export results to CSV"""
        if not self.duplicate_groups:
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "Export", "duplicates.csv", "CSV (*.csv)")
        if not path:
            return
        
        try:
            import csv
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Group', 'Path', 'Size', 'Similarity', 'Type'])
                
                for idx, group in enumerate(self.duplicate_groups, 1):
                    for file in group['files']:
                        try:
                            size = os.path.getsize(file)
                        except:
                            size = 0
                        writer.writerow([f"Group {idx}", file, size, 
                                       f"{group['similarity']:.1f}", group['type']])
            
            QMessageBox.information(self, "Success", f"Exported to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")
    
    def closeEvent(self, event):
        """Handle window close"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(self, "Scan Running", 
                                        "Stop scan and exit?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.worker.stop()
                self.worker.wait(3000)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()