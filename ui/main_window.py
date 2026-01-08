from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QSettings, QTimer
from PySide6.QtGui import QColor
from utils.worker import ScanWorker
from ui.preview_window import PreviewWindow
import os
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Similarity Pro - Fast Duplicate Finder")
        self.resize(1200, 750)
        
        # State management
        self.duplicate_groups = []
        self.all_groups = []
        self.worker = None
        self.group_counter = 0
        self.is_scanning = False
        
        # Load settings
        self.settings = QSettings("FileSimilarityPro", "DuplicateFinder")
        self.dark_mode = self.settings.value("dark_mode", False, type=bool)
        self.load_ignored_patterns()
        self.load_recent_paths()
        
        # UI setup
        self.setup_ui()
        self.apply_theme()
        
        # Auto-scroll timer for better UX
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.auto_scroll_table)
        self.scroll_timer.setInterval(500)

    def load_ignored_patterns(self):
        """Load ignored file patterns from settings"""
        default_patterns = [
            "*.tmp", "*.temp", "*.cache", "*.log",
            ".git/*", ".svn/*", ".hg/*",
            "__pycache__/*", "*.pyc", "*.pyo",
            "node_modules/*", "bower_components/*",
            ".DS_Store", "Thumbs.db", "desktop.ini",
            "$RECYCLE.BIN/*", "System Volume Information/*"
        ]
        patterns_str = self.settings.value("ignored_patterns", json.dumps(default_patterns))
        try:
            self.ignored_patterns = json.loads(patterns_str)
        except (json.JSONDecodeError, TypeError):
            self.ignored_patterns = default_patterns

    def save_ignored_patterns(self):
        """Save ignored file patterns to settings"""
        self.settings.setValue("ignored_patterns", json.dumps(self.ignored_patterns))

    def load_recent_paths(self):
        """Load recently scanned paths"""
        paths_str = self.settings.value("recent_paths", "[]")
        try:
            self.recent_paths = json.loads(paths_str)
            if not isinstance(self.recent_paths, list):
                self.recent_paths = []
        except (json.JSONDecodeError, TypeError):
            self.recent_paths = []

    def save_recent_path(self, path):
        """Save a recently scanned path"""
        if path in self.recent_paths:
            self.recent_paths.remove(path)
        self.recent_paths.insert(0, path)
        self.recent_paths = self.recent_paths[:10]  # Keep last 10
        self.settings.setValue("recent_paths", json.dumps(self.recent_paths))
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
        
        # Path input with recent paths
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
        
        self.ignore_btn = QPushButton("⚙️ Settings")
        self.ignore_btn.clicked.connect(self.show_settings_dialog)
        self.ignore_btn.setFixedWidth(100)
        
        toolbar.addWidget(path_label)
        toolbar.addWidget(self.path_input, 1)
        toolbar.addWidget(browse_btn)
        toolbar.addWidget(self.scan_btn)
        toolbar.addWidget(self.stop_btn)
        toolbar.addWidget(self.ignore_btn)
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
        
        table_label = QLabel("💡 Tip: Double-click a row to preview files, or select multiple rows to delete")
        table_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")

        # Action buttons
        button_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("👁️ Preview Group")
        self.preview_btn.clicked.connect(self.preview_selected_group)
        self.preview_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("🗑️ Delete Selected")
        self.delete_btn.clicked.connect(self.delete_selected)
        self.delete_btn.setEnabled(False)
        
        self.export_btn = QPushButton("📄 Export Results")
        self.export_btn.clicked.connect(self.export_results)
        self.export_btn.setEnabled(False)
        
        button_layout.addWidget(self.preview_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()

        # Main layout assembly
        main_layout = QVBoxLayout()
        main_layout.addLayout(toolbar)
        main_layout.addLayout(progress_layout)
        main_layout.addWidget(self.summary_label)
        main_layout.addWidget(filter_group)
        main_layout.addWidget(table_label)
        main_layout.addWidget(self.table, 1)
        main_layout.addLayout(button_layout)
        
        # Set margins for better spacing
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_filter_group(self):
        """Create the filter controls group"""
        filter_group = QGroupBox("🔍 Filter Results")
        filter_layout = QHBoxLayout()
        
        # File type filter
        filter_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["All Files", "Images Only", "Documents", "Videos", "Audio", "Archives", "Other"])
        self.type_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.type_combo)
        
        # Similarity filter
        filter_layout.addWidget(QLabel("Min Similarity:"))
        self.similarity_spin = QSpinBox()
        self.similarity_spin.setRange(50, 100)
        self.similarity_spin.setValue(70)
        self.similarity_spin.setSuffix("%")
        self.similarity_spin.valueChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.similarity_spin)
        
        # Min file size filter
        filter_layout.addWidget(QLabel("Min Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(0, 10000)
        self.size_spin.setValue(0)
        self.size_spin.setSuffix(" KB")
        self.size_spin.valueChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.size_spin)
        
        # Search box
        filter_layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Filename or path...")
        self.search_box.textChanged.connect(self.apply_filters)
        self.search_box.setClearButtonEnabled(True)
        filter_layout.addWidget(self.search_box, 1)
        
        filter_group.setLayout(filter_layout)
        return filter_group

    def show_settings_dialog(self):
        """Show comprehensive settings dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.resize(700, 500)
        
        layout = QVBoxLayout()
        
        # Tab widget for organized settings
        tabs = QTabWidget()
        
        # Ignore Patterns Tab
        ignore_tab = QWidget()
        ignore_layout = QVBoxLayout()
        
        info_label = QLabel(
            "<b>Ignore Patterns</b><br>"
            "Enter file patterns to ignore during scanning (one per line).<br>"
            "Use * as wildcard. Examples: *.tmp, .git/*, node_modules/*"
        )
        info_label.setWordWrap(True)
        ignore_layout.addWidget(info_label)
        
        text_edit = QTextEdit()
        text_edit.setPlainText("\n".join(self.ignored_patterns))
        text_edit.setFont(self.font())
        ignore_layout.addWidget(text_edit)
        
        # Reset button
        reset_btn = QPushButton("Reset to Defaults")
        def reset_defaults():
            default = [
                "*.tmp", "*.temp", "*.cache", "*.log",
                ".git/*", "__pycache__/*", "node_modules/*",
                ".DS_Store", "Thumbs.db"
            ]
            text_edit.setPlainText("\n".join(default))
        reset_btn.clicked.connect(reset_defaults)
        ignore_layout.addWidget(reset_btn)
        
        ignore_tab.setLayout(ignore_layout)
        tabs.addTab(ignore_tab, "Ignore Patterns")
        
        # Scan Settings Tab
        scan_tab = QWidget()
        scan_layout = QFormLayout()
        
        self.min_size_setting = QSpinBox()
        self.min_size_setting.setRange(0, 10000)
        self.min_size_setting.setValue(self.settings.value("min_file_size", 0, type=int))
        self.min_size_setting.setSuffix(" KB")
        scan_layout.addRow("Minimum File Size:", self.min_size_setting)
        
        scan_tab.setLayout(scan_layout)
        tabs.addTab(scan_tab, "Scan Settings")
        
        layout.addWidget(tabs)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save")
        def save_settings():
            patterns = [p.strip() for p in text_edit.toPlainText().split("\n") if p.strip()]
            self.ignored_patterns = patterns
            self.save_ignored_patterns()
            self.settings.setValue("min_file_size", self.min_size_setting.value())
            QMessageBox.information(dialog, "Success", "Settings saved successfully!")
            dialog.accept()
        save_btn.clicked.connect(save_settings)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        # Apply theme
        if self.dark_mode:
            dialog.setStyleSheet(self.get_dark_dialog_style())
        
        dialog.exec()

    def get_dark_dialog_style(self):
        return """
            QDialog { background-color: #1e1e1e; color: #e0e0e0; }
            QLabel { color: #e0e0e0; }
            QTextEdit { background-color: #2d2d2d; color: #e0e0e0; border: 1px solid #3d3d3d; }
            QTabWidget::pane { border: 1px solid #3d3d3d; background: #1e1e1e; }
            QTabBar::tab { background: #2d2d2d; color: #e0e0e0; padding: 8px 16px; border: 1px solid #3d3d3d; }
            QTabBar::tab:selected { background: #0d7377; }
            QSpinBox { background-color: #2d2d2d; color: #e0e0e0; border: 1px solid #3d3d3d; padding: 5px; }
            QPushButton { background-color: #0d7377; color: white; border: none; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #14a085; }
        """

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.settings.setValue("dark_mode", self.dark_mode)
        self.apply_theme()
        self.theme_btn.setText("☀️" if self.dark_mode else "🌙")

    def apply_theme(self):
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
                QPushButton:pressed { background-color: #0a5f63; }
                QPushButton:disabled { background-color: #3d3d3d; color: #777777; }
                QTableWidget { 
                    background-color: #2d2d2d; alternate-background-color: #262626; 
                    color: #e0e0e0; gridline-color: #3d3d3d; border: 1px solid #3d3d3d; 
                }
                QTableWidget::item:selected { background-color: #0d7377; color: white; }
                QHeaderView::section { 
                    background-color: #262626; color: #e0e0e0; padding: 8px; 
                    border: 1px solid #3d3d3d; font-weight: bold; 
                }
                QProgressBar { 
                    border: 1px solid #3d3d3d; border-radius: 4px; 
                    background-color: #2d2d2d; text-align: center; color: #e0e0e0; 
                    height: 22px;
                }
                QProgressBar::chunk { background-color: #0d7377; border-radius: 3px; }
                QGroupBox { 
                    color: #e0e0e0; border: 1px solid #3d3d3d; border-radius: 6px; 
                    margin-top: 12px; padding-top: 12px; font-weight: bold;
                }
                QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
            """)
            self.summary_label.setStyleSheet("font-weight: bold; color: #14a085; font-size: 14px; padding: 8px;")
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #ffffff; color: #333333; }
                QLineEdit, QSpinBox, QComboBox { 
                    background-color: white; border: 1px solid #cccccc; 
                    padding: 6px; color: #333333; border-radius: 4px; 
                }
                QPushButton { 
                    background-color: #4a90e2; color: white; border: none; 
                    padding: 8px 12px; border-radius: 4px; font-weight: bold; 
                }
                QPushButton:hover { background-color: #3a7bc8; }
                QPushButton:pressed { background-color: #2c6bb6; }
                QPushButton:disabled { background-color: #cccccc; color: #666666; }
                QTableWidget { 
                    background-color: white; alternate-background-color: #f9f9f9; 
                    color: #333333; gridline-color: #e0e0e0; border: 1px solid #cccccc; 
                }
                QTableWidget::item:selected { background-color: #4a90e2; color: white; }
                QHeaderView::section { 
                    background-color: #f0f0f0; color: #333333; padding: 8px; 
                    border: 1px solid #cccccc; font-weight: bold; 
                }
                QProgressBar { 
                    border: 1px solid #cccccc; border-radius: 4px; 
                    background-color: #f0f0f0; text-align: center; color: #333333; 
                    height: 22px;
                }
                QProgressBar::chunk { background-color: #4a90e2; border-radius: 3px; }
                QGroupBox { 
                    color: #333333; border: 1px solid #cccccc; border-radius: 6px; 
                    margin-top: 12px; padding-top: 12px; font-weight: bold;
                }
                QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
            """)
            self.summary_label.setStyleSheet("font-weight: bold; color: #0066cc; font-size: 14px; padding: 8px;")

    def browse(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder to Scan")
        if path:
            self.path_input.setText(path)

    def start_scan(self):
        path = self.path_input.text().strip()
        
        if not path:
            QMessageBox.warning(self, "No Folder Selected", "Please select a folder to scan")
            return
            
        if not os.path.isdir(path):
            QMessageBox.warning(self, "Invalid Folder", "The selected path is not a valid directory")
            return
        
        # Save to recent paths
        self.save_recent_path(path)
        
        # Reset UI
        self.table.setRowCount(0)
        self.table.setSortingEnabled(False)  # Disable during population
        self.scan_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.delete_btn.setEnabled(False)
        self.preview_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.summary_label.setText("🔍 Scanning in progress...")
        self.duplicate_groups = []
        self.all_groups = []
        self.group_counter = 0
        self.progress.setValue(0)
        self.is_scanning = True
        
        # Start background worker
        min_size = self.settings.value("min_file_size", 0, type=int)
        self.worker = ScanWorker(path, self.ignored_patterns, min_size)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.status.connect(self.status_label.setText)
        self.worker.group_found.connect(self.add_group_realtime)
        self.worker.finished.connect(self.scan_finished)
        self.worker.error.connect(self.scan_error)
        self.worker.start()
        
        # Start auto-scroll timer
        self.scroll_timer.start()

    def stop_scan(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.status_label.setText("⏹ Stopping scan...")
            self.stop_btn.setEnabled(False)
            self.scroll_timer.stop()

    def scan_error(self, error_msg):
        """Handle scan errors"""
        QMessageBox.critical(self, "Scan Error", error_msg)
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.is_scanning = False

    def add_group_realtime(self, group):
        """Add newly found group and apply current filters"""
        self.all_groups.append(group)
        
        # Apply filters in background to avoid UI lag
        QTimer.singleShot(100, self.apply_filters)

    def auto_scroll_table(self):
        """Auto-scroll table to show new results"""
        if self.is_scanning and self.table.rowCount() > 0:
            self.table.scrollToBottom()

    def apply_filters(self):
        """Apply all active filters and rebuild table"""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        self.duplicate_groups = []
        self.group_counter = 0
        
        # Get filter values
        file_type = self.type_combo.currentText()
        min_similarity = self.similarity_spin.value()
        min_size_kb = self.size_spin.value()
        search_text = self.search_box.text().lower()
        
        # Apply filters
        for group in self.all_groups:
            if group['similarity'] < min_similarity:
                continue
            
            # File type filter
            if not self.matches_file_type(group, file_type):
                continue
            
            # Size filter
            if group.get('size', 0) / 1024 < min_size_kb:
                continue
            
            # Search filter
            if search_text and not any(search_text in f.lower() for f in group['files']):
                continue
            
            self.add_group_to_table(group)
        
        # Re-enable sorting
        self.table.setSortingEnabled(True)
        
        # Update UI state
        self.update_summary()

    def matches_file_type(self, group, file_type):
        """Check if group matches the selected file type filter"""
        if file_type == "All Files":
            return True
        
        files = group['files']
        
        type_map = {
            "Images Only": ('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.gif', '.svg', '.ico'),
            "Documents": ('.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.md'),
            "Videos": ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'),
            "Audio": ('.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'),
            "Archives": ('.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'),
        }
        
        if file_type in type_map:
            extensions = type_map[file_type]
            return any(f.lower().endswith(extensions) for f in files)
        
        # "Other" - files that don't match any category
        all_extensions = set()
        for exts in type_map.values():
            all_extensions.update(exts)
        return not any(f.lower().endswith(tuple(all_extensions)) for f in files)

    def add_group_to_table(self, group):
        """Add a single group to the table with color coding"""
        self.duplicate_groups.append(group)
        group_idx = self.group_counter
        self.group_counter += 1
        
        # Color palette
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
            
            # Group column
            group_item = QTableWidgetItem(group_name)
            group_item.setData(Qt.UserRole, group_idx)
            group_item.setBackground(color)
            self.table.setItem(r, 0, group_item)
            
            # Path column
            path_item = QTableWidgetItem(file_path)
            path_item.setBackground(color)
            path_item.setToolTip(file_path)
            self.table.setItem(r, 1, path_item)
            
            # Size column
            try:
                size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                size_item = QTableWidgetItem(self.format_size(size))
                size_item.setData(Qt.UserRole, size)  # Store for sorting
                size_item.setBackground(color)
                self.table.setItem(r, 2, size_item)
            except:
                self.table.setItem(r, 2, QTableWidgetItem("N/A"))
            
            # Similarity column
            sim_text = f"{group['similarity']:.1f}%"
            if group['type'] == 'exact':
                sim_text = "100% ✓"
            sim_item = QTableWidgetItem(sim_text)
            sim_item.setData(Qt.UserRole, group['similarity'])
            sim_item.setBackground(color)
            self.table.setItem(r, 3, sim_item)

    def update_summary(self):
        """Update the summary statistics label"""
        if self.duplicate_groups:
            total_files = sum(len(g['files']) for g in self.duplicate_groups)
            total_wasted = sum(g['wasted_space'] for g in self.duplicate_groups)
            
            summary_text = (
                f"📊 Showing <b>{len(self.duplicate_groups)}</b> of <b>{len(self.all_groups)}</b> groups "
                f"with <b>{total_files}</b> files. "
                f"💾 Potential space savings: <b>{self.format_size(total_wasted)}</b>"
            )
            self.summary_label.setText(summary_text)
            self.delete_btn.setEnabled(True)
            self.preview_btn.setEnabled(True)
            self.export_btn.setEnabled(True)
        else:
            if self.all_groups:
                self.summary_label.setText("🔍 No results match current filters")
            else:
                self.summary_label.setText("✅ No duplicate files detected")
            self.delete_btn.setEnabled(False)
            self.preview_btn.setEnabled(False)
            self.export_btn.setEnabled(False)

    def scan_finished(self, groups):
        """Called when scan completes"""
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.is_scanning = False
        self.scroll_timer.stop()
        
        if not self.all_groups:
            self.status_label.setText("✅ Scan complete - No duplicates found")
            self.summary_label.setText("✅ No duplicate files detected")
        else:
            self.status_label.setText(f"✅ Scan complete! Found {len(self.all_groups)} duplicate groups")
            self.update_summary()

    def format_size(self, bytes_size):
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.2f} PB"
    
    def open_preview(self, index):
        """Open preview window when row is double-clicked"""
        row = index.row()
        group_idx = self.table.item(row, 0).data(Qt.UserRole)
        self.show_group_preview(group_idx)
    
    def preview_selected_group(self):
        """Preview currently selected group"""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a row to preview")
            return
        
        row = selected[0].row()
        group_idx = self.table.item(row, 0).data(Qt.UserRole)
        self.show_group_preview(group_idx)
    
    def show_group_preview(self, group_idx):
        """Show preview window for a specific group"""
        if group_idx >= len(self.duplicate_groups):
            return
        
        group = self.duplicate_groups[group_idx]
        preview = PreviewWindow(group, group_idx + 1, self.dark_mode, self)
        preview.file_deleted.connect(self.refresh_table)
        preview.show()
    
    def on_selection_changed(self):
        """Update button states based on selection"""
        has_selection = len(self.table.selectedItems()) > 0
        self.delete_btn.setEnabled(has_selection)
        self.preview_btn.setEnabled(has_selection)
    
    def refresh_table(self):
        """Refresh table after files are deleted"""
        # Remove groups with deleted files
        updated_all_groups = []
        for group in self.all_groups:
            existing_files = [f for f in group['files'] if os.path.exists(f)]
            if len(existing_files) >= 2:
                group['files'] = existing_files
                try:
                    size = os.path.getsize(existing_files[0])
                    group['wasted_space'] = size * (len(existing_files) - 1)
                    group['size'] = size
                    updated_all_groups.append(group)
                except:
                    pass
        
        self.all_groups = updated_all_groups
        self.apply_filters()
    
    def delete_selected(self):
        """Delete selected files with confirmation"""
        selected_rows = set(item.row() for item in self.table.selectedItems())
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select files to delete")
            return
        
        files_to_delete = []
        for row in selected_rows:
            file_path = self.table.item(row, 1).text()
            if os.path.exists(file_path):
                files_to_delete.append(file_path)
        
        if not files_to_delete:
            QMessageBox.warning(self, "No Valid Files", "Selected files no longer exist")
            return
        
        # Show confirmation with details
        total_size = sum(os.path.getsize(f) for f in files_to_delete)
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Confirm Deletion")
        msg.setText(f"Are you sure you want to delete {len(files_to_delete)} file(s)?")
        msg.setInformativeText(f"Total size: {self.format_size(total_size)}")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        
        if msg.exec() == QMessageBox.Yes:
            deleted = 0
            errors = []
            
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    deleted += 1
                except Exception as e:
                    errors.append(f"{os.path.basename(file_path)}: {str(e)}")
            
            # Show results
            if errors:
                result_msg = QMessageBox(self)
                result_msg.setIcon(QMessageBox.Warning)
                result_msg.setWindowTitle("Deletion Results")
                result_msg.setText(f"Deleted {deleted} of {len(files_to_delete)} file(s)")
                result_msg.setDetailedText("\n".join(errors))
                result_msg.exec()
            else:
                QMessageBox.information(self, "Success", f"Successfully deleted {deleted} file(s)")
            
            self.refresh_table()
    
    def export_results(self):
        """Export scan results to CSV file"""
        if not self.duplicate_groups:
            QMessageBox.warning(self, "No Results", "No duplicate groups to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "duplicate_files.csv", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Group', 'File Path', 'Size (Bytes)', 'Similarity (%)', 'Type'])
                
                for idx, group in enumerate(self.duplicate_groups, 1):
                    for file in group['files']:
                        try:
                            size = os.path.getsize(file)
                        except:
                            size = 0
                        writer.writerow([
                            f"Group {idx}",
                            file,
                            size,
                            f"{group['similarity']:.1f}",
                            group['type']
                        ])
            
            QMessageBox.information(self, "Export Success", f"Results exported to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export results:\n{str(e)}")
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, 
                "Scan in Progress",
                "A scan is currently running. Do you want to stop it and exit?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.worker.stop()
                self.worker.wait(3000)  # Wait up to 3 seconds
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()