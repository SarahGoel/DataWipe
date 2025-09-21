#!/usr/bin/env python3
import sys, time, threading
import requests
import qtawesome as qta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QListWidget, QStackedWidget,
                             QProgressBar, QTextEdit, QHBoxLayout, QCheckBox,
                             QMessageBox)
from PyQt5 import QtCore
from config import API_URL, APP_THEME_COLOR

def http_get(path):
    try:
        r = requests.get(API_URL.rstrip('/')+path, timeout=2)
        r.raise_for_status()
        return r.json()
    except: return None

def http_post(path, body):
    try:
        r = requests.post(API_URL.rstrip('/')+path, json=body, timeout=3)
        r.raise_for_status()
        return r.json()
    except: return None

class StyledButton(QPushButton):
    def __init__(self, text, icon=None):
        super().__init__(text)
        if icon: self.setIcon(qta.icon(icon, color="white"))
        self.setStyleSheet(f"background:{APP_THEME_COLOR}; color:white; padding:8px 12px; border-radius:6px;")

class Landing(QWidget):
    def __init__(self, parent): 
        super().__init__()
        l=QVBoxLayout(); l.addStretch()
        l.addWidget(QLabel("<h1>🔒 Secure Data Wiper</h1>"))
        l.addWidget(QLabel("Select device → Wipe → Verify → Certificate"))
        btn=StyledButton("Start Wiping", "fa5s.play")
        btn.clicked.connect(lambda: parent.nav("devices"))
        l.addWidget(btn); l.addStretch(); self.setLayout(l)

class Devices(QWidget):
    def __init__(self, parent):
        super().__init__(); self.parent=parent
        l=QVBoxLayout(); self.listw=QListWidget()
        l.addWidget(QLabel("<b>Detected Drives</b>")); l.addWidget(self.listw)
        hb=QHBoxLayout()
        hb.addWidget(StyledButton("Refresh", "fa5s.sync"))
        nxt=StyledButton("Next →", "fa5s.arrow-right")
        nxt.clicked.connect(lambda: parent.nav("options")); hb.addStretch(); hb.addWidget(nxt)
        l.addLayout(hb); self.setLayout(l); self.refresh()

    def refresh(self):
        self.listw.clear()
        data=http_get("/api/drives") or []
        if not data: data=[{"name":"C: (SSD 256GB)"},{"name":"D: (HDD 1TB)"}]
        for d in data:
            it=QListWidgetItem(d.get("name","drive")); it.setCheckState(QtCore.Qt.Unchecked); self.listw.addItem(it)

    def selected(self): return [self.listw.item(i).text() for i in range(self.listw.count()) if self.listw.item(i).checkState()==QtCore.Qt.Checked]

class Options(QWidget):
    def __init__(self, parent):
        super().__init__(); self.parent=parent
        l=QVBoxLayout(); l.addWidget(QLabel("<b>Wipe Method</b>"))
        self.methods=QListWidget()
        for m in ["Quick","NIST 800-88","DoD 5220.22-M","Gutmann","Crypto-Erase"]: self.methods.addItem(m)
        l.addWidget(self.methods); self.hash=QCheckBox("Generate SHA-256 Report"); l.addWidget(self.hash)
        hb=QHBoxLayout();         hb.addWidget(StyledButton("← Back","fa5s.arrow-left"))
        start=StyledButton("Start Wipe","fa5s.play"); start.clicked.connect(self.start); hb.addStretch(); hb.addWidget(start)
        l.addLayout(hb); self.setLayout(l)
    def start(self):
        self.parent.nav("progress"); self.parent.widgets["progress"].simulate()

class Progress(QWidget):
    def __init__(self,parent):
        super().__init__(); self.parent=parent
        l=QVBoxLayout(); l.addWidget(QLabel("<b>Progress</b>"))
        self.bar=QProgressBar(); l.addWidget(self.bar)
        self.log=QTextEdit(); self.log.setReadOnly(True); l.addWidget(self.log)
        cancel=StyledButton("Cancel","fa5s.times"); cancel.clicked.connect(self.cancel); l.addWidget(cancel); self.setLayout(l)
    def simulate(self):
        self.bar.setValue(0); self.log.clear()
        def run():
            for i in range(0,101,10):
                time.sleep(0.5); self.bar.setValue(i); self.log.append(f"{i}% done")
            self.parent.nav("complete")
        threading.Thread(target=run,daemon=True).start()
    def cancel(self): QMessageBox.information(self,"Cancel","Wipe cancelled (demo).")

class Complete(QWidget):
    def __init__(self,parent):
        super().__init__(); l=QVBoxLayout()
        l.addWidget(QLabel("<h2>✅ Wipe Complete</h2>"))
        dl=StyledButton("Download Report","fa5s.file-pdf"); l.addWidget(dl)
        home=StyledButton("Back Home","fa5s.home"); home.clicked.connect(lambda: parent.nav("home")); l.addWidget(home)
        self.setLayout(l)

class Reports(QWidget):
    def __init__(self):
        super().__init__(); l=QVBoxLayout()
        l.addWidget(QLabel("<b>Reports</b>"))
        box=QTextEdit(); box.setText("Report logs will appear here..."); l.addWidget(box); self.setLayout(l)

class Main(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Secure Data Wiper Desktop")
        self.stack=QStackedWidget(); self.widgets={}
        self.widgets["home"]=Landing(self); self.widgets["devices"]=Devices(self); self.widgets["options"]=Options(self)
        self.widgets["progress"]=Progress(self); self.widgets["complete"]=Complete(self); self.widgets["reports"]=Reports()
        for w in self.widgets.values(): self.stack.addWidget(w)
        self.setCentralWidget(self.stack); self.nav("home")
    def nav(self,name): self.stack.setCurrentWidget(self.widgets[name])

if __name__=="__main__":
    app=QApplication(sys.argv); win=Main(); win.resize(900,600); win.show(); sys.exit(app.exec_())
