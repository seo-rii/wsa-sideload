import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QProgressBar, QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIcon
import time
import subprocess
import os

CREATE_NO_WINDOW = 0x08000000

class ConnectADB(QThread):
    finished = pyqtSignal(bool)

    def run(self):
        print(os.path.join(sys._MEIPASS, "adb", "adb"))
        proc = subprocess.run([os.path.join(sys._MEIPASS, "adb", "adb"), "disconnect"], universal_newlines=False,
                              stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
        proc = subprocess.run([os.path.join(sys._MEIPASS, "adb", "adb"), "connect", "127.0.0.1:58526"], universal_newlines=False,
                              stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)

        if 'cannot' in str(proc.stdout):
            self.finished.emit(False)
        else:
            self.finished.emit(True)


class InstallThread(QThread):
    finished = pyqtSignal(list)

    def __init__(self, files, parent=None):
        QThread.__init__(self, parent)
        self.files = files

    def run(self):
        for idx, file in enumerate(self.files):
            proc = subprocess.run([os.path.join(sys._MEIPASS, "adb", "adb"), "install", file], universal_newlines=False,
                                  stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
            print(str(proc.stdout))
            self.finished.emit([idx, True])


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.worker = ConnectADB()
        self.worker.finished.connect(self.afterConnectADB)
        self.worker.start()

    def initUI(self):
        self.setWindowTitle('WSA sideload')
        self.setWindowIcon(QIcon(os.path.join(sys._MEIPASS, "adb", "logo.png")))
        self.label = QLabel('Connecting to adb...', self)
        self.label.move(20, 10)

        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(20, 40, 200, 25)
        self.pbar.setRange(0, 0)
        self.pbar.setTextVisible(False)

        self.resize(240, 100)
        self.show()

    def afterConnectADB(self, data):
        if data:
            self.pbar.hide()
            self.label.setText('Drop APK File Here!')
            self.setAcceptDrops(True)

        else:
            QMessageBox.critical(self, 'Error',
                                 'Cannot connect to ADB.\nTurn on WSA and enable developer mode on WSA setting.')
            self.destroy()
            app.exit()

    def dragEnterEvent(self, event):
        try:
            if event.mimeData().hasUrls():
                for i in [u.toLocalFile() for u in event.mimeData().urls()]:
                    if i.split('.')[-1] != 'apk':
                        event.ignore()
                        return
                event.accept()
            else:
                event.ignore()
        except:
            event.ignore()

    def dropEvent(self, event):
        self.files = [u.toLocalFile() for u in event.mimeData().urls()]
        self.pbar.show()
        self.pbar.setRange(0, len(self.files) * 10)
        self.worker2 = InstallThread(self.files)
        self.worker2.finished.connect(self.onInstall)
        self.worker2.start()
        self.label.setText('Installing...')
        self.pbar.setValue(3)

    def onInstall(self, info):
        if info[0] + 1 == len(self.files):
            self.label.setText('Install Finished!')
            self.pbar.setValue(info[0] * 10 + 10)
        else:
            self.label.setText('Installing...')
            self.pbar.setValue(info[0] * 10 + 13)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec())
