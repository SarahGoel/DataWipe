# zerotrace.py
# Paste this into a file and run: python zerotrace.py
import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QTabWidget, QFrame, QFileDialog, QListWidget, QListWidgetItem,
    QProgressBar, QMessageBox, QTextEdit, QDialog, QToolButton, QSizePolicy,
    QHBoxLayout, QSpacerItem
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve

# -------------------- Intro Dialog --------------------
class IntroDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to ZeroTrace")
        self.setModal(True)
        self.resize(560, 320)
        self.setStyleSheet("background-color: #0f1724; color: #e6f0ff;")
        layout = QVBoxLayout(self)

        title = QLabel("🔒 ZeroTrace — Secure Data Wiping")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:20px; font-weight:700; color:#00d4ff;")
        desc = QLabel(
            "ZeroTrace provides secure, auditable, and simulated data destruction.\n\n"
            "• Multi-level wiping (simulated)\n"
            "• Tamper-proof certificates\n"
            "• Clean, accessible UI"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #cfe9ff; font-size:14px;")
        desc.setAlignment(Qt.AlignLeft)

        footer = QLabel("Click anywhere or press Close to continue.")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color:#9fbecf; font-size:12px;")

        btn_close = QPushButton("Close")
        btn_close.setStyleSheet("padding:8px 16px;")
        btn_close.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addSpacing(6)
        layout.addWidget(desc)
        layout.addStretch()
        layout.addWidget(footer)
        layout.addWidget(btn_close, alignment=Qt.AlignCenter)

    # clicking outside should close the dialog normally only if you implement special behavior;
    # we keep default modal close via button for clarity.


# -------------------- Collapsible Box --------------------
class CollapsibleBox(QWidget):
    def __init__(self, title="", content=""):
        super().__init__()
        self.toggle_button = QToolButton(text=title, checkable=True, checked=False)
        self.toggle_button.setStyleSheet("""
            QToolButton { font-weight: 700; font-size: 13px; color: #0b63b5; border: none; }
            QToolButton:hover { color: #084a85; }
        """)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.clicked.connect(self.on_toggle)

        self.content_area = QWidget()
        self.content_area.setMaximumHeight(0)
        self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setStyleSheet("color: #333; font-size:13px;")
        inner_layout = QVBoxLayout(self.content_area)
        inner_layout.setContentsMargins(6, 6, 6, 6)
        inner_layout.addWidget(content_label)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.toggle_button)
        main_layout.addWidget(self.content_area)

    def on_toggle(self):
        if self.toggle_button.isChecked():
            self.toggle_button.setArrowType(Qt.DownArrow)
            self.content_area.setMaximumHeight(400)
        else:
            self.toggle_button.setArrowType(Qt.RightArrow)
            self.content_area.setMaximumHeight(0)


# -------------------- Main Application --------------------
class ZeroTraceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZeroTrace - Secure Data Wiping")
        self.setGeometry(80, 40, 1100, 720)

        # Basic fonts
        self.base_font = QFont("Segoe UI", 10)
        QApplication.instance() and QApplication.instance().setFont(self.base_font)

        # Light theme default
        self.light_stylesheet = """
            QMainWindow { background-color: #f5f7fb; }
            QLabel#Title { font-size: 18px; font-weight: 700; color: #0b63b5; }
            QPushButton { background-color: #0b63b5; color: white; padding: 10px; border-radius:8px; }
            QPushButton:hover { background-color: #084a85; }
            QTextEdit, QListWidget { background-color: #ffffff; border: 1px solid #d0d7e6; border-radius:6px; padding:6px; }
            QProgressBar { border: 1px solid #d0d7e6; border-radius:6px; text-align:center; background:#fff; }
            QProgressBar::chunk { background-color: #0b63b5; border-radius:6px; }
        """
        self.dark_stylesheet = """
            QMainWindow { background-color: #0b1117; color: #dbe9ff; }
            QLabel#Title { font-size: 18px; font-weight: 700; color: #00d4ff; }
            QPushButton { background-color: #0086c9; color: white; padding: 10px; border-radius:8px; }
            QPushButton:hover { background-color: #006f9f; }
            QTextEdit, QListWidget { background-color: #081018; border: 1px solid #11303f; border-radius:6px; padding:6px; color: #dbe9ff; }
            QProgressBar { border: 1px solid #11303f; border-radius:6px; text-align:center; background:#081018; }
            QProgressBar::chunk { background-color: #00d4ff; border-radius:6px; }
        """
        self.setStyleSheet(self.light_stylesheet)
        self.is_dark = False

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add tabs
        self.tabs.addTab(self.home_tab(), "🏠 Home")
        self.tabs.addTab(self.file_wipe_tab(), "📂 File Wipe")
        self.tabs.addTab(self.drive_wipe_tab(), "💽 Drive Wipe")
        self.tabs.addTab(self.certificates_tab(), "📜 Certificates")
        self.tabs.addTab(self.help_tab(), "❓ Help")

        self.statusBar().showMessage("Ready")

        # Intro after small delay
        QTimer.singleShot(600, self.show_intro)

    # ---------------- Intro & Banner Animation ----------------
    def show_intro(self):
        intro = IntroDialog(self)
        # Animate top banner growth in the home tab for a polished effect
        home_tab = self.tabs.widget(0)
        banner = home_tab.findChild(QLabel, "TopBanner")
        if banner:
            banner.setMaximumHeight(0)
            anim = QPropertyAnimation(banner, b"maximumHeight", self)
            anim.setDuration(600)
            anim.setStartValue(0)
            anim.setEndValue(220)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.start()
            # keep ref
            self._banner_anim = anim
        intro.exec_()

    def separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #cfd9e9;")
        return line

    # ---------------- Home Tab ----------------
    def home_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        # Banner (animated)
        banner = QLabel("🚀 ZeroTrace — Secure Data Wiping")
        banner.setObjectName("TopBanner")
        banner.setAlignment(Qt.AlignCenter)
        banner.setStyleSheet("background-color: #0b63b5; color: white; font-size:22px; font-weight:700;")
        banner.setFixedHeight(220)
        layout.addWidget(banner)

        about = QLabel(
            "ZeroTrace is a modern data destruction tool intended for secure, auditable, and simulated wiping.\n\n"
            "Key highlights:\n  • Simulated multi-pass methods\n  • Exportable certificates\n  • Clean UX for demos and training\n"
        )
        about.setWordWrap(True)
        about.setStyleSheet("font-size:13px; color:#1f334a;")
        layout.addWidget(about)
        layout.addWidget(self.separator())

        # Action buttons row
        row = QHBoxLayout()
        btn_fw = QPushButton("📂 File Wipe")
        btn_dw = QPushButton("💽 Drive Wipe")
        btn_cert = QPushButton("📜 Certificates")
        btn_help = QPushButton("❓ Help")
        for b in (btn_fw, btn_dw, btn_cert, btn_help):
            b.setCursor(Qt.PointingHandCursor)
            row.addWidget(b)
        row.addItem(QSpacerItem(24, 10))  # spacing
        # Theme toggle
        btn_theme = QPushButton("Toggle Theme")
        btn_theme.clicked.connect(self.toggle_theme)
        row.addWidget(btn_theme)

        # Connect actions
        btn_fw.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        btn_dw.clicked.connect(lambda: self.tabs.setCurrentIndex(2))
        btn_cert.clicked.connect(lambda: self.tabs.setCurrentIndex(3))
        btn_help.clicked.connect(lambda: self.tabs.setCurrentIndex(4))

        layout.addLayout(row)
        layout.addStretch()
        tab.setLayout(layout)
        return tab

    # ---------------- File Wipe Tab ----------------
    def file_wipe_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)

        title = QLabel("📂 File Wipe - Securely Erase Files & Folders")
        title.setObjectName("Title")
        title.setStyleSheet("font-size:16px;")
        layout.addWidget(title)
        layout.addWidget(self.separator())

        self.file_list = QListWidget()
        layout.addWidget(self.file_list, stretch=1)

        row = QHBoxLayout()
        btn_select_files = QPushButton("➕ Add Files")
        btn_select_files.clicked.connect(self.select_files)
        btn_select_folder = QPushButton("📁 Add Folder")
        btn_select_folder.clicked.connect(self.select_folder)
        row.addWidget(btn_select_files)
        row.addWidget(btn_select_folder)
        layout.addLayout(row)

        row2 = QHBoxLayout()
        btn_wipe = QPushButton("⚡ Start Wipe")
        btn_wipe.clicked.connect(self.start_file_wipe)
        btn_cancel = QPushButton("⏹ Cancel")
        btn_cancel.clicked.connect(self.cancel_wipe)
        row2.addWidget(btn_wipe)
        row2.addWidget(btn_cancel)
        layout.addLayout(row2)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box, stretch=1)

        btn_delete_all = QPushButton("🧨 DELETE EVERYTHING (Simulated)")
        btn_delete_all.setStyleSheet("background-color: #d32f2f; color: white; font-weight:700;")
        btn_delete_all.clicked.connect(self.delete_all)
        layout.addWidget(btn_delete_all)

        tab.setLayout(layout)
        # state vars
        self.wipe_timer = None
        self.wipe_in_progress = False
        return tab

    # ---------------- Drive Wipe Tab ----------------
    def drive_wipe_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        info = QLabel(
            "💽 Drive Wipe — Coming Soon\n\n"
            "This area will later support drive-level operations like ATA Secure Erase, NVMe sanitize,\n"
            "and crypto-erase for SEDs. For now this is a placeholder."
        )
        info.setAlignment(Qt.AlignTop)
        info.setWordWrap(True)
        layout.addWidget(info)
        layout.addStretch()
        tab.setLayout(layout)
        return tab

    # ---------------- Certificates Tab ----------------
    def certificates_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        header = QLabel("📜 Certificate Preview")
        header.setObjectName("Title")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        self.cert_log = QTextEdit()
        self.cert_log.setReadOnly(False)
        self.refresh_certificate_text()
        layout.addWidget(self.cert_log, stretch=1)

        row = QHBoxLayout()
        btn_export = QPushButton("📤 Export Certificate")
        btn_export.clicked.connect(self.export_certificate)
        btn_copy = QPushButton("📋 Copy to Clipboard")
        btn_copy.clicked.connect(self.copy_certificate)
        row.addWidget(btn_export)
        row.addWidget(btn_copy)
        layout.addLayout(row)

        tab.setLayout(layout)
        return tab

    def refresh_certificate_text(self):
        self.cert_text = (
            "═══════════════════════════════════════════════════\n"
            "            🏅 ZeroTrace Certificate of Data Destruction 🏅\n"
            "═══════════════════════════════════════════════════\n\n"
            "This certificate confirms that the listed files/folders were\n"
            "securely wiped using ZeroTrace secure erase procedures (simulated).\n\n"
            f"Issued on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "Files/Folders:\n"
        )
        # include file list items
        if hasattr(self, "file_list") and self.file_list.count() > 0:
            for i in range(self.file_list.count()):
                self.cert_text += f"   • {self.file_list.item(i).text()}\n"
        else:
            self.cert_text += "   • (none selected)\n"

        self.cert_text += (
            "\n═══════════════════════════════════════════════════\n"
            "Authorized by: ______________________\n"
            "                ZeroTrace Authority\n"
            "═══════════════════════════════════════════════════\n"
            "🔒 Watermark: ZeroTrace Secure Wipe (Simulated)\n"
        )
        if hasattr(self, "cert_log"):
            self.cert_log.setPlainText(self.cert_text)

    def export_certificate(self):
        # Save as text file (simulated PDF export)
        self.refresh_certificate_text()
        fn, _ = QFileDialog.getSaveFileName(self, "Export Certificate", f"zerotrace_certificate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "Text Files (*.txt);;All Files (*)")
        if fn:
            try:
                with open(fn, "w", encoding="utf-8") as f:
                    f.write(self.cert_text)
                QMessageBox.information(self, "Exported", f"Certificate saved to:\n{fn}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")

    def copy_certificate(self):
        self.refresh_certificate_text()
        QApplication.clipboard().setText(self.cert_text)
        QMessageBox.information(self, "Copied", "Certificate copied to clipboard.")

    # ---------------- Help Tab ----------------
    def help_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        title = QLabel("❓ Help - Frequently Asked Questions")
        title.setObjectName("Title")
        layout.addWidget(title)
        layout.addWidget(self.separator())

        qa_data = [
            ("How do I wipe files?", "Go to File Wipe → Add Files or Add Folder → Start Wipe."),
            ("What is Drive Wipe?", "Feature to securely erase entire drives (coming soon)."),
            ("What are Certificates?", "Proof of erasure with timestamp, file names, and method (simulated)."),
            ("Is Delete Everything safe?", "⚠️ This is a simulation only. Do not use on production drives."),
            ("Can data be recovered?", "With proper wipe methods, recovery is extremely difficult; this is a demo."),
        ]
        for q, a in qa_data:
            box = CollapsibleBox(title=f"Q: {q}", content=f"A: {a}")
            layout.addWidget(box)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    # ---------------- File Selection ----------------
    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Wipe")
        for f in files:
            if f:
                self.file_list.addItem(QListWidgetItem(f))
        self.refresh_certificate_text()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Wipe")
        if folder:
            self.file_list.addItem(QListWidgetItem(f"[FOLDER] {folder}"))
        self.refresh_certificate_text()

    # ---------------- Wipe Simulation ----------------
    def start_file_wipe(self):
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "No Files", "Please select files or folders to wipe first.")
            return
        if self.wipe_in_progress:
            QMessageBox.information(self, "Already Running", "A wipe is already in progress.")
            return

        self.log_box.append(f"🔄 [Simulated] Starting wipe ({self.file_list.count()} items)")
        self.progress.setValue(0)
        self.wipe_in_progress = True
        self.current_progress = 0
        # simulate a multi-step sequence with small increments for better UX
        self.wipe_step_texts = ["Overwriting (pass 1)...", "Overwriting (pass 2)...", "Verifying...", "Finalizing..."]
        self.wipe_timer = QTimer(self)
        self.wipe_timer.timeout.connect(self._wipe_tick)
        self.wipe_timer.start(450)

    def _wipe_tick(self):
        # increment progress smoother
        if self.current_progress < 100:
            self.current_progress += 8  # small increments
            self.progress.setValue(min(self.current_progress, 100))
            stage = (self.current_progress // 30) if self.current_progress < 100 else len(self.wipe_step_texts)-1
            stage = min(stage, len(self.wipe_step_texts)-1)
            self.log_box.append(self.wipe_step_texts[stage])
        else:
            self._finish_wipe()

    def _finish_wipe(self):
        if self.wipe_timer:
            self.wipe_timer.stop()
        self.wipe_in_progress = False
        self.progress.setValue(100)
        self.log_box.append("✅ [Simulated] Wipe Complete!\n")
        self.refresh_certificate_text()

    def cancel_wipe(self):
        if self.wipe_in_progress and self.wipe_timer:
            self.wipe_timer.stop()
            self.wipe_in_progress = False
            self.progress.setValue(0)
            self.log_box.append("⛔ Wipe cancelled by user.\n")
        else:
            self.log_box.append("ℹ️ No active wipe to cancel.\n")

    # ---------------- Delete Everything (Simulated) ----------------
    def delete_all(self):
        reply = QMessageBox.critical(
            self, "⚠️ DELETE EVERYTHING (SIMULATED)",
            "This will SIMULATE erasing many files from your system.\n\nDo you want to continue?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.log_box.append("🧨 [Simulated] Delete Everything started.")
            self.progress.setValue(0)
            self.wipe_in_progress = True
            self.current_progress = 0
            self.delete_steps = ["Scanning...", "Wiping C:\\...", "Wiping D:\\...", "Finalizing..."]
            self.wipe_timer = QTimer(self)
            self.wipe_timer.timeout.connect(self._delete_tick)
            self.wipe_timer.start(700)

    def _delete_tick(self):
        if self.current_progress < 100:
            self.current_progress += 20
            self.progress.setValue(min(self.current_progress, 100))
            idx = min(self.current_progress // 25, len(self.delete_steps)-1)
            self.log_box.append(self.delete_steps[idx])
        else:
            if self.wipe_timer:
                self.wipe_timer.stop()
            self.wipe_in_progress = False
            self.log_box.append("✅ [Simulated] DELETE EVERYTHING complete.\n")
            self.progress.setValue(100)

    # ---------------- Theme Toggle ----------------
    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.setStyleSheet(self.dark_stylesheet if self.is_dark else self.light_stylesheet)

# -------------------- Run --------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Ensure a consistent app name on macOS/Linux for window managers
    app.setApplicationName("ZeroTrace")
    window = ZeroTraceApp()
    window.show()
    sys.exit(app.exec_())


