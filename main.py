import sys
import warnings
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.main_window import MainWindow

def main():
    # Suppress specific warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="PIL.Image")
    
    # Set image allocation limit (for large images)
    os.environ['QT_IMAGEIO_MAXALLOC'] = '512'  # 512 MB limit
    
    app = QApplication(sys.argv)
    app.setApplicationName("File Similarity Pro")
    app.setOrganizationName("FileSimilarityPro")
    
    # High DPI scaling is automatic in Qt6, no need to set attributes
    # The deprecated attributes are only needed in Qt5
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()