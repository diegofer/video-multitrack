import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from extract import TracksExtractThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video a Multitrack")
        self.setGeometry(100, 100, 600, 400)
        self.label = QLabel("Arrastra y suelta el archivo .mp4 aquí", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("QLabel { border: 4px dashed #aaa; }")
        
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.endswith(".mp4"):
                    self.load_video(file_path)
    
    def load_video(self, fileName=None):
        self.extract_thread = TracksExtractThread(fileName)
        self.extract_thread.result.connect(self.on_extracted)
        self.extract_thread.start()

    def on_extracted(self, msg):
        print(msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
