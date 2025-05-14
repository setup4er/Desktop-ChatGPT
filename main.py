from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut
from g4f.client import Client
import re
import html
from PyQt5.QtGui import QTextCursor

# Константа с именами моделей
MODELS_NAME = ["gpt-3.5-turbo",  "gpt-4o-mini"]


class Worker(QtCore.QThread):
    responseReady = QtCore.pyqtSignal(str)

    def __init__(self, messages, chosing_model):
        super().__init__()
        self.messages = messages
        self.chosing_model = chosing_model

    def run(self):
        try:
            client = Client()
            response = client.chat.completions.create(
                model=self.chosing_model,
                messages=self.messages,
                timeout=15,
            )
            content = response.choices[0].message.content
            self.responseReady.emit(content)
        except Exception as e:
            self.responseReady.emit(f"Error: {str(e)}")


class SettingsWindow(QtWidgets.QDialog):
    modelSelected = QtCore.pyqtSignal(str)

    def __init__(self, current_model):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setFixedSize(300, 150)

        # Убираем системные кнопки "Закрыть" и "Свернуть"
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.CustomizeWindowHint)

        self.layout = QtWidgets.QVBoxLayout(self)

        self.setStyleSheet("""
                    QDialog {
                        background-color: #f4f4f4;
                        font-family: "Segoe UI", Arial, sans-serif;
                        font-size: 12pt;
                        border: 1px solid #dcdcdc;
                        border-radius: 10px;
                    }
                    QLabel {
                        font-size: 14pt;
                        color: #333333;
                    }
                    QComboBox {
                        background-color: #ffffff;
                        border: 1px solid #dcdcdc;
                        border-radius: 5px;
                        padding: 5px;
                    }
                    QComboBox::drop-down {
                        border-left: 1px solid #dcdcdc;
                    }
                    QComboBox::down-arrow {
                        image: url(down-arrow.png); /* Замените на иконку, если нужно */
                        width: 10px;
                        height: 10px;
                    }
                    QPushButton {
                        background-color: #5c9ded;
                        color: white;
                        border-radius: 8px;
                        padding: 8px 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #3b78c3;
                    }
                    QPushButton:pressed {
                        background-color: #2b5c92;
                    }
                """)

        # Надпись выбора модели
        self.label = QtWidgets.QLabel("Select ChatGPT Model:")
        self.layout.addWidget(self.label)

        # Выпадающий список для выбора модели
        self.modelComboBox = QtWidgets.QComboBox()
        self.modelComboBox.addItems(MODELS_NAME)
        self.modelComboBox.setCurrentText(current_model)
        self.layout.addWidget(self.modelComboBox)

        # Кнопки подтверждения и отмены
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.okButton = QtWidgets.QPushButton("OK")
        self.cancelButton = QtWidgets.QPushButton("Cancel")
        self.buttonLayout.addWidget(self.okButton)
        self.buttonLayout.addWidget(self.cancelButton)

        self.layout.addLayout(self.buttonLayout)

        # Подключение сигналов
        self.okButton.clicked.connect(self.save_settings)
        self.cancelButton.clicked.connect(self.reject)

    def save_settings(self):
        selected_model = self.modelComboBox.currentText()
        self.modelSelected.emit(selected_model)
        self.accept()



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(799, 608)
        MainWindow.setMinimumSize(500, 500)
        MainWindow.setWindowTitle("Pocket ChatGPT")

        # Применяем стиль
        self.apply_stylesheet(MainWindow)

        # Центральный виджет
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.layout = QtWidgets.QVBoxLayout(self.centralwidget)

        # Splitter для разделения чата и ввода текста
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)

        # Выбранная модель
        self.chosing_model = "gpt-3.5-turbo"

        self.model_label = QtWidgets.QLabel(MainWindow)
        self.model_label.setText(f"Model: {self.chosing_model}")
        self.model_label.setGeometry(QtCore.QRect(20, 20, 150, 20))
        self.model_label.setStyleSheet('''
        color:rgb(169, 169, 169);
        font-style: oblique;
        ''')

        # Поле чата
        self.chatDisplay = QtWidgets.QTextBrowser(self.splitter)
        self.chatDisplay.setMinimumHeight(200)
        self.chatDisplay.setStyleSheet("padding-top: 50px;")
        # Поле ввода
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.splitter)
        self.plainTextEdit.setMinimumHeight(100)
        self.plainTextEdit.setPlaceholderText("Tell to ChatGPT...")

        self.splitter.setSizes([400, 150])
        self.layout.addWidget(self.splitter)

        # Горизонтальный компоновщик для кнопок
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.pushButton = QtWidgets.QPushButton("Send")
        self.clearButton = QtWidgets.QPushButton("Clear")
        self.buttonLayout.addWidget(self.pushButton)
        self.buttonLayout.addWidget(self.clearButton)
        self.layout.addLayout(self.buttonLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        # Кнопка настроек, всегда на одном месте
        self.settings_button = QtWidgets.QPushButton(MainWindow)
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.setText("⚙")
        self.settings_button.setFixedSize(50, 50)
        self.settings_button.setStyleSheet('''
        #settingsButton{
        font-size: 20pt; 
        background-color: #5c9ded; 
        color: white; 
        border-radius: 25px;
        }
        #settingsButton:hover{
        background-color: #3b78c3;
        }
        ''')
        self.settings_button.clicked.connect(self.open_settings)

        # Подключаем событие изменения размера окна
        MainWindow.resizeEvent = self.resize_event

        # Горячие клавиши
        self.enterShortcut = QShortcut(QKeySequence("Return"), MainWindow)
        self.enterShortcut.activated.connect(self.handle_enter_key)

        # Подключаем кнопки
        self.pushButton.clicked.connect(self.send_message)
        self.clearButton.clicked.connect(self.clear_chat)

        # История сообщений для контекста
        self.messages = []

        # Анимация ожидания ответа
        self.loading_timer = QtCore.QTimer()
        self.loading_timer.timeout.connect(self.update_loading_animation)
        self.loading_dots = ""
        self.loading_label = None

    def resize_event(self, event):
        self.settings_button.move(event.size().width() - 85, 12)

    def apply_stylesheet(self, MainWindow):
        style = """
            * {
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 12pt;
            }
            QMainWindow {
                background-color: #f4f4f4;
            }
            QTextBrowser {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 8px;
                padding: 8px;
            }
            QPlainTextEdit {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton {
                background-color: #5c9ded;
                color: white;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3b78c3;
            }
            QPushButton:pressed {
                background-color: #2b5c92;
            }
            QPushButton:disabled {
                background-color: #a5bcd9;
                color: #eeeeee;
            }
            QSplitter::handle {
                background: #dcdcdc;
            }
        """
        MainWindow.setStyleSheet(style)

    def handle_enter_key(self):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            self.plainTextEdit.insertPlainText("\n")
        else:
            self.send_message()

    def send_message(self):
        text = self.plainTextEdit.toPlainText().strip()
        if not text:
            self.chatDisplay.append("<b>Error:</b> Input is empty. Please enter a message.")
            return

        self.messages.append({"role": "user", "content": "С имитируй злость человека, отвечай агрессивно и будь токсичным: " + text})
        formatted_text = self.format_message(text)
        self.chatDisplay.append(f"""
            <div style="margin-bottom: 15px;">
                <b>You:</b><br>{formatted_text}
            </div>
        """)
        self.chatDisplay.moveCursor(QTextCursor.End)
        self.plainTextEdit.setPlainText("")
        self.loading_dots = ""
        if not self.loading_label:
            self.loading_label = QtWidgets.QLabel("<b>ChatGPT is typing</b>", self.centralwidget)
            self.layout.addWidget(self.loading_label)
        self.loading_timer.start(500)  # Старт анимации
        
        # Отключаем кнопку отправки
        self.pushButton.setEnabled(False)
        self.start_worker()


    def update_loading_animation(self):
        self.loading_dots = "." * ((len(self.loading_dots) % 3) + 1)
        self.loading_label.setText(f"<b>ChatGPT is typing{self.loading_dots}</b>")

    def start_worker(self):
        self.worker = Worker(self.messages, self.chosing_model)
        self.worker.responseReady.connect(self.display_response)
        self.worker.start()

    def display_response(self, response):
        self.loading_timer.stop()  # Останавливаем анимацию ожидания
        if self.loading_label:
            self.loading_label.setParent(None)  # Убираем текст анимации
            self.loading_label = None

        # Включаем кнопку отправки
        self.pushButton.setEnabled(True)

        self.messages.append({"role": "assistant", "content": response})
        formatted_response = self.format_message(response)
        self.chatDisplay.append(f"""
            <div style="margin-bottom: 20px;">
                <b>ChatGPT:</b><br>{formatted_response}
            </div>
        """)
        self.chatDisplay.moveCursor(QTextCursor.End)

    def clear_chat(self):
        self.chatDisplay.clear()  # Очищаем интерфейс
        dialog = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                       "Очистка",
                                       "Чат был очищен",
                                       buttons=QtWidgets.QMessageBox.Ok)
        result = dialog.exec()

        self.messages = []  # Очищаем историю сообщений

    def format_message(self, message):
        def code_replacer(match):
            # Язык программирования и сам код
            language = match.group(1)  # Язык кода
            code = match.group(2)  # Сам код

            # Оформляем блок кода с <pre>
            return f"""<div style="background-color:#f5f5f5; 
                                   border:1px solid #ccc; 
                                   border-radius:8px; 
                                   padding:8px; 
                                   margin:8px 0; 
                                   font-family:Courier,monospace; 
                                   font-size:11pt;">
                            <b style="color:#3b78c3;">{language}</b><br>
                            <pre style="margin:0; white-space:pre-wrap; font-size:14px;">{html.escape(code)}</pre>
                       </div>"""

        # Шаг 1: Заменяем блоки кода
        pattern = re.compile(r'```(\w+)\n(.*?)```', re.DOTALL)
        message_with_code = re.sub(pattern, code_replacer, message)

        # Шаг 2: Обрабатываем переносы строк
        return message_with_code.replace("\n", "<br>")

    def open_settings(self):
        self.settings_window = SettingsWindow(self.chosing_model)
        self.settings_window.modelSelected.connect(self.update_model)
        self.settings_window.exec_()

    def update_model(self, new_model):
        self.chosing_model = new_model
        self.model_label.setText(f"Model: {self.chosing_model}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
