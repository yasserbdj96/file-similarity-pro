import sys
import warnings
import os
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from config import config

def main():
    # Suppress specific warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="PIL.Image")
    
    # Set image allocation limit from config
    max_alloc = config.get_int('MAX_IMAGE_SIZE_MB', 512)
    os.environ['QT_IMAGEIO_MAXALLOC'] = str(max_alloc)
    
    app = QApplication(sys.argv)
    app.setApplicationName("File Similarity Pro")
    app.setOrganizationName("FileSimilarityPro")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()