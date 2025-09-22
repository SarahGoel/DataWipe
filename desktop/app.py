#!/usr/bin/env python3
import os
import sys
import hashlib
import threading
import time
from datetime import datetime

from PyQt5 import QtWidgets, QtCore, QtGui

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from services.wipe_methods import WipeMethods
from utils.report import generate_pdf_report, generate_json_report


class WipeWorker(QtCore.QObject):
    progress_changed = QtCore.pyqtSignal(int, str)
    finished = QtCore.pyqtSignal(bool, str, str)

    def __init__(self, path: str, passes: int = 1):
        super().__init__()
        self.path = path
        self.passes = passes
        self._cancel = False

    def cancel(self):
        self._cancel = True

    @QtCore.pyqtSlot()
    def run(self):
        try:
            methods = WipeMethods(os.name)
            start_ts = time.time()

            sha_before = None
            try:
                with open(self.path, 'rb') as f:
                    sha_before = hashlib.sha256(f.read(1024 * 1024)).hexdigest()
            except Exception:
                sha_before = None

            def cb(pct: int, msg: str):
                self.progress_changed.emit(int(pct), msg)

            methods.wipe_file_clear(self.path, max(1, min(self.passes, 3)), cb)

            end_ts = time.time()
            # file deleted; sha_after None
            pdf = generate_pdf_report("file:" + self.path, "nist_800_88", max(1, min(self.passes, 3)), sha_before, None, "completed", start_ts, end_ts)
            json_path = generate_json_report("file:" + self.path, "nist_800_88", max(1, min(self.passes, 3)), sha_before, None, "completed", start_ts, end_ts)
            self.finished.emit(True, pdf, json_path or "")
        except Exception as e:
            self.finished.emit(False, str(e), "")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZeroTrace Desktop - Secure Wipe")
        self.setMinimumSize(720, 520)
        self._init_ui()
        self.thread = None
        self.worker = None

    def _init_ui(self):
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)

        title = QtWidgets.QLabel("ZeroTrace - Secure File Wipe")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        form = QtWidgets.QFormLayout()
        self.path_edit = QtWidgets.QLineEdit()
        browse_btn = QtWidgets.QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_file)
        hb = QtWidgets.QHBoxLayout()
        hb.addWidget(self.path_edit)
        hb.addWidget(browse_btn)
        path_widget = QtWidgets.QWidget()
        path_widget.setLayout(hb)
        form.addRow("File to wipe:", path_widget)

        self.passes_combo = QtWidgets.QComboBox()
        self.passes_combo.addItems(["1", "3"])
        form.addRow("Passes:", self.passes_combo)

        self.confirm_cb = QtWidgets.QCheckBox("I understand this will permanently destroy data")
        form.addRow("", self.confirm_cb)

        layout.addLayout(form)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.status_label = QtWidgets.QLabel("")
        layout.addWidget(self.status_label)

        btns = QtWidgets.QHBoxLayout()
        self.start_btn = QtWidgets.QPushButton("Start Secure Wipe")
        self.start_btn.clicked.connect(self._start)
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel)
        btns.addWidget(self.start_btn)
        btns.addWidget(self.cancel_btn)
        layout.addLayout(btns)

        self.setCentralWidget(central)

    def _browse_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select file to securely wipe")
        if path:
            self.path_edit.setText(path)

    def _start(self):
        path = self.path_edit.text().strip()
        if not path or not os.path.isfile(path):
            QtWidgets.QMessageBox.warning(self, "Invalid Path", "Please select a valid file.")
            return
        if not self.confirm_cb.isChecked():
            QtWidgets.QMessageBox.warning(self, "Confirmation Required", "Please confirm you understand this is destructive.")
            return
        passes = int(self.passes_combo.currentText())

        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress.setValue(0)
        self.status_label.setText("Starting...")

        self.thread = QtCore.QThread()
        self.worker = WipeWorker(path, passes)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress_changed.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def _cancel(self):
        if self.worker:
            self.worker.cancel()
        self.cancel_btn.setEnabled(False)

    def _on_progress(self, pct: int, msg: str):
        self.progress.setValue(pct)
        self.status_label.setText(msg)

    def _on_finished(self, success: bool, info: str, json_path: str):
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        if success:
            self.progress.setValue(100)
            self.status_label.setText("Wipe completed. Certificate generated.")
            QtWidgets.QMessageBox.information(self, "Success", f"Wipe complete. Certificate saved to:\n{info}")
        else:
            QtWidgets.QMessageBox.critical(self, "Failed", f"Wipe failed: {info}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


