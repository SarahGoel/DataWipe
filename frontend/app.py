import sys, string, os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QTabWidget, QFrame, QFileDialog, QListWidget, QListWidgetItem,
    QProgressBar, QMessageBox, QTextEdit, QDialog, QToolButton, QSizePolicy
)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPainter, QColor
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtMultimedia import QSoundEffect

# ---------- Intro Popup ----------
class IntroDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome to ZeroTrace")
        self.setGeometry(500, 250, 480, 320)
        self.setStyleSheet("background-color: #1e1e2f; color: white; font-size: 14px;")
        layout = QVBoxLayout()
        title = QLabel("🔒 ZeroTrace - Secure Data Wiping")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00e5ff;")
        title.setAlignment(Qt.AlignCenter)
        desc = QLabel(
            "\nZeroTrace ensures irrecoverable data wiping for files & drives.\n\n"
            "✨ Features:\n"
            "  ✅ Multi-level wiping\n"
            "  ✅ Tamper-proof certificates\n"
            "  ✅ Simple & safe interface\n"
        )
        desc.setAlignment(Qt.AlignLeft)
        desc.setWordWrap(True)
        note = QLabel("\nClick ❌ or outside to continue.")
        note.setStyleSheet("color: #aaa; font-size: 12px;")
        note.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addWidget(note)
        self.setLayout(layout)

# ---------- Collapsible Q&A ----------
class CollapsibleBox(QWidget):
    def __init__(self, title="", content=""):
        super().__init__()
        self.toggle_button = QToolButton(text=title, checkable=True, checked=False)
        self.toggle_button.setStyleSheet("""
            QToolButton { font-weight: bold; font-size: 14px; color: #0078d7; }
            QToolButton:hover { color: #005a9e; }
        """)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.clicked.connect(self.on_toggle)
        self.content_area = QWidget()
        self.content_area.setMaximumHeight(0)
        self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        content_label = QLabel(content)
        content_label.setStyleSheet("color: #444; font-size: 13px;")
        content_label.setWordWrap(True)
        lay = QVBoxLayout(self.content_area)
        lay.addWidget(content_label)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.toggle_button)
        main_layout.addWidget(self.content_area)

    def on_toggle(self):
        if self.toggle_button.isChecked():
            self.toggle_button.setArrowType(Qt.DownArrow)
            self.content_area.setMaximumHeight(400)
        else:
            self.toggle_button.setArrowType(Qt.RightArrow)
            self.content_area.setMaximumHeight(0)

# ---------- Main App ----------
class ZeroTraceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZeroTrace - Secure Data Wiping")
        self.setGeometry(100, 50, 1100, 700)

        # Play startup sound
        QApplication.beep()

        self.setStyleSheet("""
            QMainWindow { background-color: #f5f7fa; }
            QLabel#Title { font-size: 20px; font-weight: bold; color: #0078d7; }
            QPushButton {
                background-color: #0078d7; color: white;
                padding: 12px; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #005a9e; }
            QTextEdit {
                background-color: #ffffff; color: #222; font-family: 'Times New Roman';
                border: 2px solid #0078d7; border-radius: 10px;
                padding: 10px; font-size: 13px;
            }
            QListWidget {
                background-color: #fff; border: 1px solid #ccc;
                border-radius: 6px; padding: 6px;
            }
            QProgressBar {
                border: 1px solid #ccc; border-radius: 6px; text-align: center;
            }
            QProgressBar::chunk { background-color: #0078d7; }
        """)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Unique emoji icons
        self.tabs.addTab(self.home_tab(), "🏠 Home")
        self.tabs.addTab(self.file_wipe_tab(), "📂 File Wipe")
        self.tabs.addTab(self.drive_wipe_tab(), "💽 Drive Wipe")
        self.tabs.addTab(self.certificates_tab(), "📜 Certificates")
        self.tabs.addTab(self.help_tab(), "❓ Help")

        self.statusBar().showMessage("Ready")
        QTimer.singleShot(900, self.show_intro)

    def show_intro(self):
        intro = IntroDialog()
        intro.exec_()

    def separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #bbb;")
        return line

    # ---------- Home ----------
    def home_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        banner = QLabel()
        banner.setStyleSheet("background-color: #0a58ca; color: white;")
        banner.setFixedHeight(220)
        banner.setAlignment(Qt.AlignCenter)
        banner.setText("🚀 ZeroTrace — Secure Data Wiping")
        banner.setFont(QFont("Arial", 24, QFont.Bold))

        about = QLabel(
            "\nℹ️ About ZeroTrace:\n\n"
            "ZeroTrace is a next-generation **data destruction platform** designed to ensure "
            "your sensitive data is gone for good — whether from files, folders, or entire drives.\n\n"
            "🔒 **Industry Standards**\n"
            "   • NIST 800-88\n"
            "   • DoD 5220.22-M\n"
            "   • Gutmann (35-pass overwrite)\n"
            "   • Crypto-Erase for modern SSDs\n\n"
            "📜 **Digital Certificates**\n"
            "   • Tamper-proof logs with hash signatures\n"
            "   • Proof of compliance for audits & enterprises\n\n"
            "🌱 **Eco-Friendly Design**\n"
            "   • Supports e-waste recycling policies\n"
            "   • Encourages sustainable IT disposal\n\n"
            "⚡ **Technology**\n"
            "   • Built in Python (lightweight, cross-platform)\n"
            "   • Intuitive, modern interface\n"
            "   • Simulation mode for safe demos\n"
        )
        about.setWordWrap(True)
        about.setFont(QFont("Arial", 12))

        layout.addWidget(banner)
        layout.addWidget(about)
        layout.addWidget(self.separator())

        for name, idx, emoji in [
            ("File Wipe", 1, "📂"),
            ("Drive Wipe", 2, "💽"),
            ("Certificates", 3, "📜"),
            ("Help", 4, "❓")
        ]:
            btn = QPushButton(f"{emoji} {name}")
            btn.clicked.connect(lambda _, x=idx: self.tabs.setCurrentIndex(x))
            layout.addWidget(btn)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    # ---------- File Wipe ----------
    def file_wipe_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        title = QLabel("📂 File Wipe - Securely Erase Files & Folders")
        title.setObjectName("Title")
        layout.addWidget(title)
        layout.addWidget(self.separator())

        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        btn_select_files = QPushButton("➕ Add Files")
        btn_select_files.clicked.connect(self.select_files)
        layout.addWidget(btn_select_files)

        btn_select_folder = QPushButton("📁 Add Folder")
        btn_select_folder.clicked.connect(self.select_folder)
        layout.addWidget(btn_select_folder)

        btn_wipe = QPushButton("⚡ Start Wipe")
        btn_wipe.clicked.connect(self.start_file_wipe)
        layout.addWidget(btn_wipe)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        btn_delete_all = QPushButton("🧨 DELETE EVERYTHING (Dangerous)")
        btn_delete_all.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold;")
        btn_delete_all.clicked.connect(self.delete_all)
        layout.addWidget(btn_delete_all)

        tab.setLayout(layout)
        return tab

    # ---------- Drive Wipe ----------
    def drive_wipe_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        label = QLabel("💽 Drive Wipe Section (Coming Soon)\n\nWill support ATA/NVMe sanitize and SED crypto-erase.")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        tab.setLayout(layout)
        return tab

    # ---------- Certificates ----------
    def certificates_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        header = QLabel("📜 Certificate Preview")
        header.setObjectName("Title")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        self.cert_log = QTextEdit()
        self.cert_log.setReadOnly(False)
        self.cert_log.setText(
            "═══════════════════════════════════════════════════\n"
            "            🏅 ZeroTrace Certificate of Data Destruction 🏅\n"
            "═══════════════════════════════════════════════════\n\n"
            "This certificate confirms that the listed files/folders were\n"
            "securely wiped using ZeroTrace secure erase procedures.\n\n"
            f"Issued on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "Files/Folders:\n   ---\n\n"
            "═══════════════════════════════════════════════════\n"
            "Authorized by: ______________________\n"
            "                ZeroTrace Authority\n"
            "═══════════════════════════════════════════════════\n"
            "🔒 Watermark: ZeroTrace Secure Wipe (Simulated)\n")
        layout.addWidget(self.cert_log)

        btn_export = QPushButton("📤 Export Certificates as PDF")
        layout.addWidget(btn_export)

        tab.setLayout(layout)
        return tab

    # ---------- Help ----------
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
            ("What are Certificates?", "Proof of erasure with timestamp, file names, and method."),
            ("Is Delete Everything safe?", "⚠️ No. It simulates permanent full wipe."),
            ("Can data be recovered?", "No. With proper methods, recovery is not feasible."),
        ]
        for q, a in qa_data:
            box = CollapsibleBox(title=f"Q: {q}", content=f"A: {a}")
            layout.addWidget(box)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    # ---------- File Selection ----------
    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Wipe")
        for f in files:
            self.file_list.addItem(QListWidgetItem(f))

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Wipe")
        if folder:
            self.file_list.addItem(QListWidgetItem(f"[FOLDER] {folder}"))

    # ---------- File Wipe Simulation ----------
    def start_file_wipe(self):
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "No Files", "Please select files or folders first!")
            return
        self.log_box.append("🔄 Starting wipe...\n")
        self.progress.setValue(0)
        self.current_step = 0
        self.steps = ["Overwriting...", "Verifying...", "Finalizing..."]
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(800)

    def update_progress(self):
        if self.current_step < 100:
            step_text = self.steps[(self.current_step // 40) % len(self.steps)]
            self.log_box.append(step_text)
            self.current_step += 40
            self.progress.setValue(self.current_step)
        else:
            self.timer.stop()
            self.log_box.append("✅ Wipe Complete!\n")

    # ---------- Delete Everything ----------
    def delete_all(self):
        reply = QMessageBox.critical(
            self, "⚠️ DELETE EVERYTHING",
            "This will ERASE ALL DATA from your system (Simulated).\n\nAre you sure?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QApplication.beep()  # Dramatic alert
            self.log_box.append("🧨 Delete Everything Triggered!\n")
            self.progress.setValue(0)
            self.current_step = 0
            self.delete_steps = ["Scanning...", "Wiping C:\\...", "Wiping D:\\...", "Finalizing..."]
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_delete_progress)
            self.timer.start(1000)

    def update_delete_progress(self):
        if self.current_step < 100:
            step_text = self.delete_steps[(self.current_step // 25) % len(self.delete_steps)]
            self.log_box.append(step_text)
            self.current_step += 25
            self.progress.setValue(self.current_step)
        else:
            self.timer.stop()
            self.log_box.append("✅ DELETE EVERYTHING Complete! (Simulated)\n")

# ---------- Run ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ZeroTraceApp()
    window.show()
    sys.exit(app.exec_())

