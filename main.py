import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QProgressBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QMovie
from extract import TracksExtractThread
import qtawesome as qta

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video a Multitrack")
        self.setGeometry(100, 100, 600, 400)
        self.label = QLabel("Arrastra y suelta el archivo .mp4 aquí", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("QLabel { border: 4px dashed #aaa; }")
        
        self.spinner = QLabel(self)
        self.spinner.setAlignment(Qt.AlignCenter)
        self.icon = qta.icon("fa5s.spinner", color="blue", animation=qta.Spin(self.spinner))
        self.label.setPixmap(self.icon.pixmap(48))
        self.spinner.hide()
        
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.spinner)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and self.isEnabled():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls() and self.isEnabled():
            event.acceptProposedAction()
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.endswith(".mp4"):
                    self.load_video(file_path)
    
    def load_video(self, fileName=None):
        self.setAcceptDrops(False)
        self.spinner.show()
        self.extract_thread = TracksExtractThread(fileName)
        self.extract_thread.result.connect(self.on_extracted)
        self.extract_thread.start()

    def on_extracted(self, msg):
        self.spinner.hide()
        self.setAcceptDrops(True)
        print(msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
