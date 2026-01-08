from PySide6.QtCore import QThread, Signal
from core.scanner import scan_folder, find_duplicate_groups

class ScanWorker(QThread):
    progress = Signal(int)
    finished = Signal(list)
    status = Signal(str)
    group_found = Signal(dict)
    error = Signal(str)

    def __init__(self, path, ignored_patterns=None, min_file_size=0):
        super().__init__()
        self.path = path
        self.ignored_patterns = ignored_patterns or []
        self.min_file_size = min_file_size * 1024  # Convert KB to bytes
        self._is_running = True
        self._error_occurred = False

    def stop(self):
        """Stop the scanning process gracefully"""
        self._is_running = False

    def is_running(self):
        """Check if worker should continue running"""
        return self._is_running

    def run(self):
        try:
            self.status.emit("Scanning files...")
            self.progress.emit(0)
            
            # Scan folder with cancellation support
            files = scan_folder(
                self.path, 
                lambda: self._is_running, 
                self.ignored_patterns,
                self.min_file_size
            )
            
            if not self._is_running:
                self.status.emit("Scan cancelled by user")
                self.finished.emit([])
                return
            
            if not files:
                self.status.emit("No files found matching criteria")
                self.finished.emit([])
                return
            
            self.status.emit(f"Found {len(files)} files. Analyzing duplicates...")
            self.progress.emit(10)
            
            # Find duplicates with progress updates
            results = find_duplicate_groups(
                files, 
                self.progress.emit, 
                self.status.emit, 
                lambda: self._is_running,
                self.emit_group
            )
            
            if not self._is_running:
                self.status.emit("Analysis cancelled by user")
                self.finished.emit([])
            else:
                self.status.emit(f"Scan complete! Found {len(results)} duplicate groups")
                self.progress.emit(100)
                self.finished.emit(results)
                
        except Exception as e:
            self._error_occurred = True
            error_msg = f"Error during scan: {str(e)}"
            self.error.emit(error_msg)
            self.status.emit("Scan failed - see error message")
            self.finished.emit([])
    
    def emit_group(self, group):
        """Emit a newly found group immediately for real-time display"""
        if self._is_running:
            self.group_found.emit(group)