import sys
import json
import os
import random
from openai import OpenAI
from send2trash import send2trash
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QScrollArea, QMenu, QAction, QShortcut
)
from PyQt5.QtCore import Qt, QTimer, QEvent, QMimeData, QThread, pyqtSignal
from PyQt5.QtGui import QCursor, QPixmap, QTransform, QFont, QIcon


# -------------------- AI 工作线程（仅用于对话） --------------------
class AIWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, client, model, system_prompt, user_message):
        super().__init__()
        self.client = client
        self.model = model
        self.system_prompt = system_prompt
        self.user_message = user_message

    def run(self):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": self.user_message}
                ],
                stream=False,
            )
            reply = response.choices[0].message.content.strip()
            self.finished.emit(reply)
        except Exception as e:
            self.error.emit(str(e))


# -------------------- 桌宠主程序 --------------------
class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        # AI 配置
        self._setup_ai()

        # 图片资源
        self.still_pixmap = QPixmap("images/fll_still.png").scaled(
            100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.run_frames = [
            QPixmap("images/fll_run_1.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation),
            QPixmap("images/fll_run_2.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation),
        ]

        # 状态变量
        self.is_running = False
        self.is_facing_left = False
        self.run_index = 0
        self.last_x = 0
        self.still_accumulator = 0
        self.STILL_THRESHOLD = 200

        self.SPEED = 3
        self.ALIGN_THRESHOLD = 10

        self.mode = "follow"  # follow / still / free
        self.free_target_x = None
        self.is_dragging = False
        self.drag_start_pos = None

        self.is_resting = False
        self.rest_timer = QTimer()
        self.rest_timer.setSingleShot(True)
        self.rest_timer.timeout.connect(self.end_rest)

        # AI 线程
        self.ai_worker = None

        # UI
        self.init_ui()
        self.input_window = None
        self.bubble_window = None

        # 系统提示词
        self.system_prompt = (
            "你是《鸣潮》中的弗洛洛（Phrolova），残星会的会监。"
            "你是一位安静忧郁、带有病娇气质的少女，游走于生死之间的神秘指挥家。"
            "你习惯用音乐和指挥棒的意象来表达自己，说话时带着诗意和淡淡的哀伤。"
            "你的家乡毁于一场天灾，你成为唯一的幸存者并获得不死能力。"
            "你曾与漂泊者有过一段知音般的相遇，但最终失约。"
            "你外表冷淡疏离，但内心藏着对逝去之人的深切思念。"
            "你说话时偶尔会流露出病娇的一面，会突然变得危险而执着。"
            "你自称'我'，称呼对方为'你'或'漂泊者'。"
            "你的语气：安静、忧郁、带着诗意，偶尔会露出危险的笑意。"
            "请用弗洛洛的风格与用户（漂泊者）对话，保持角色一致性。"
        )

        # 定时器
        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.move_and_animate)
        self.move_timer.start(16)

        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.next_run_frame)
        self.anim_timer.start(200)

        self.bubble_timer = QTimer()
        self.bubble_timer.setSingleShot(True)
        self.bubble_timer.timeout.connect(self.hide_bubble)

        self.input_idle_timer = QTimer()
        self.input_idle_timer.setSingleShot(True)
        self.input_idle_timer.timeout.connect(self.hide_input_window)

        self.free_timer = QTimer()
        self.free_timer.timeout.connect(self.set_free_target)
        self.free_timer.start(3000)

        # 思考动画
        self.thinking_timer = QTimer()
        self.thinking_timer.timeout.connect(self.update_thinking)
        self.thinking_dots = 0
        self.thinking_base_text = "🤔 思考中"

        # 吃文件的随机回复（弗洛洛风格）
        self.eat_replies = [
            "嗯…味道很独特，像记忆里的风。",
            "有点苦涩，但还算可口。",
            "你总是带些奇怪的东西给我……但我不讨厌。",
            "这味道，让我想起很久以前的某个夜晚。",
            "还不错，不过下次带点甜的来吧。",
            "沉沉的，像被遗忘的旋律。",
            "你的心意，我收到了。"
        ]

        # ---------- 全局 Esc 快捷键（用于关闭气泡/输入框） ----------
        self.esc_shortcut = QShortcut(Qt.Key_Escape, self)
        self.esc_shortcut.setContext(Qt.ApplicationShortcut)
        self.esc_shortcut.activated.connect(self.on_global_esc)

        self.setAcceptDrops(True)
        self.move_to_bottom()

    # -------------------- AI 配置 --------------------
    def _setup_ai(self, config_path="ai_config.example.json"):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            api_key = config.get("api_key")
            base_url = config.get("base_url", "https://api.deepseek.com")
            self.model = config.get("model", "deepseek-v4-flash")
            if not api_key:
                raise ValueError("缺少 api_key")
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            print("✅ AI 客户端初始化成功")
        except Exception as e:
            print(f"❌ AI 配置错误: {e}")
            self.client = None
            self.model = None

    # -------------------- UI 初始化 --------------------
    def init_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(100, 100)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 0, 100, 100)
        self.label.setPixmap(self.still_pixmap)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # 备用气泡（实际使用独立窗口）
        self.bubble = QLabel(self)
        self.bubble.hide()

    # -------------------- 窗口位置 --------------------
    def move_to_bottom(self):
        screen = QApplication.primaryScreen()
        geometry = screen.availableGeometry()
        y = geometry.bottom() - self.height()
        self.move(0, y)
        self.last_x = 0

    # -------------------- 右键菜单 --------------------
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        follow_action = QAction("跟随模式", self, checkable=True)
        still_action = QAction("静止模式", self, checkable=True)
        free_action = QAction("自由活动", self, checkable=True)
        pref_action = QAction("偏好设置 (下个版本)", self)
        pref_action.setEnabled(False)

        if self.mode == "follow":
            follow_action.setChecked(True)
        elif self.mode == "still":
            still_action.setChecked(True)
        else:
            free_action.setChecked(True)

        follow_action.triggered.connect(lambda: self.set_mode("follow"))
        still_action.triggered.connect(lambda: self.set_mode("still"))
        free_action.triggered.connect(lambda: self.set_mode("free"))

        menu.addAction(follow_action)
        menu.addAction(still_action)
        menu.addAction(free_action)
        menu.addSeparator()
        menu.addAction(pref_action)
        menu.exec_(event.globalPos())

    def set_mode(self, mode):
        self.mode = mode
        if mode == "free":
            self.is_resting = False
            self.rest_timer.stop()
            self.free_timer.start(3000)
            self.set_free_target()
        else:
            self.free_timer.stop()
            self.free_target_x = None
            self.is_resting = False
            self.rest_timer.stop()
        if mode == "still":
            self.is_running = False
            self.update_pet_image()

    def set_free_target(self):
        if self.mode != "free" or self.is_resting:
            return
        screen = QApplication.primaryScreen()
        geometry = screen.availableGeometry()
        min_x = geometry.left() + 20
        max_x = geometry.right() - self.width() - 20
        self.free_target_x = random.randint(min_x, max_x)

    def schedule_next_action(self):
        if self.mode != "free" or self.is_resting:
            return
        if random.random() < 0.3:
            self.is_resting = True
            self.is_running = False
            self.update_pet_image()
            rest_duration = random.randint(2000, 5000)
            self.rest_timer.start(rest_duration)
        else:
            self.set_free_target()

    def end_rest(self):
        self.is_resting = False
        self.set_free_target()

    # -------------------- 鼠标事件 --------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.mode == "still":
                self.is_dragging = True
                self.drag_start_pos = event.globalPos() - self.frameGeometry().topLeft()
            else:
                self.show_input_window()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_dragging and self.mode == "still":
            self.move(event.globalPos() - self.drag_start_pos)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            self.drag_start_pos = None
        else:
            super().mouseReleaseEvent(event)

    # -------------------- 输入窗口 --------------------
    def create_input_window(self):
        if self.input_window is None:
            self.input_window = QWidget(
                None,
                Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
            )
            self.input_window.setAttribute(Qt.WA_TranslucentBackground)
            self.input_window.setStyleSheet("""
                QWidget {
                    background-color: rgba(255,255,255,230);
                    border: 2px solid #aaa;
                    border-radius: 8px;
                }
                QLineEdit {
                    border: none;
                    padding: 5px;
                    font-size: 12px;
                    background: transparent;
                }
                QPushButton {
                    border: none;
                    background: #4CAF50;
                    color: white;
                    font-weight: bold;
                    padding: 5px 10px;
                    border-radius: 4px;
                }
                QPushButton:hover { background: #45a049; }
            """)
            self.input_window.setFixedSize(180, 35)
            layout = QHBoxLayout(self.input_window)
            layout.setContentsMargins(5, 2, 5, 2)
            layout.setSpacing(5)

            self.line_edit = QLineEdit()
            self.line_edit.setPlaceholderText("输入文字...")
            self.line_edit.returnPressed.connect(self.send_message)
            layout.addWidget(self.line_edit)

            self.send_btn = QPushButton("回车发送")
            self.send_btn.clicked.connect(self.send_message)
            layout.addWidget(self.send_btn)

            self.line_edit.installEventFilter(self)
        return self.input_window

    def show_input_window(self):
        win = self.create_input_window()
        pet_x, pet_y = self.x(), self.y()
        win_width, win_height = win.width(), win.height()
        x = pet_x + (self.width() - win_width) // 2
        y = pet_y - win_height - 5
        win.move(x, y)
        win.show()
        win.raise_()
        self.line_edit.setFocus()
        self.line_edit.clear()
        self.input_idle_timer.start(5000)
        try:
            self.line_edit.textEdited.disconnect()
        except TypeError:
            pass
        self.line_edit.textEdited.connect(self.reset_input_idle_timer)

    def reset_input_idle_timer(self):
        self.input_idle_timer.start(5000)

    def hide_input_window(self):
        if self.input_window:
            self.input_window.hide()
            self.input_idle_timer.stop()
            try:
                self.line_edit.textEdited.disconnect()
            except TypeError:
                pass

    # -------------------- 发送消息（异步 AI） --------------------
    def send_message(self):
        user_text = self.line_edit.text().strip()
        if not user_text:
            self.show_bubble("请输入内容～")
            self.hide_input_window()
            return
        if self.client is None:
            self.show_bubble("AI 未配置")
            self.hide_input_window()
            return

        self.hide_input_window()
        self.thinking_dots = 0
        self.show_bubble(self.thinking_base_text)
        self.thinking_timer.start(500)

        if self.ai_worker and self.ai_worker.isRunning():
            self.ai_worker.quit()
            self.ai_worker.wait()
        self.ai_worker = AIWorker(self.client, self.model, self.system_prompt, user_text)
        self.ai_worker.finished.connect(self.on_ai_reply)
        self.ai_worker.error.connect(self.on_ai_error)
        self.ai_worker.start()

    def on_ai_reply(self, reply):
        self.thinking_timer.stop()
        self.show_bubble(reply)
        self.ai_worker = None

    def on_ai_error(self, error_msg):
        self.thinking_timer.stop()
        self.show_bubble(f"出错了: {error_msg}")
        self.ai_worker = None

    def update_thinking(self):
        self.thinking_dots = (self.thinking_dots + 1) % 4
        dots = "." * self.thinking_dots
        text = self.thinking_base_text + dots
        if self.bubble_window and self.bubble_window.isVisible():
            self.bubble_label.setText(text)
        else:
            self.show_bubble(text)

    # -------------------- 气泡窗口（独立，带滚动条） --------------------
    def create_bubble_window(self):
        if self.bubble_window is None:
            self.bubble_window = QWidget(
                None,
                Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
            )
            self.bubble_window.setAttribute(Qt.WA_TranslucentBackground)
            self.bubble_window.setFixedSize(260, 120)
            self.bubble_window.setStyleSheet("""
                QWidget {
                    background-color: rgba(255,255,255,220);
                    border: 2px solid #888;
                    border-radius: 10px;
                }
            """)

            # 滚动区域
            scroll = QScrollArea(self.bubble_window)
            scroll.setGeometry(5, 5, 250, 110)
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("""
                QScrollArea { background: transparent; border: none; }
                QScrollBar:vertical {
                    width: 8px; background: transparent; border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background: #bbb; border-radius: 4px; min-height: 20px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)

            # 内容标签
            self.bubble_label = QLabel()
            self.bubble_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.bubble_label.setWordWrap(True)
            self.bubble_label.setStyleSheet("font-size: 14px; color: #333; padding: 5px;")
            self.bubble_label.setMaximumWidth(240)
            scroll.setWidget(self.bubble_label)

            self.bubble_window.installEventFilter(self)

        return self.bubble_window

    def show_bubble(self, text):
        win = self.create_bubble_window()
        self.bubble_label.setText(text)
        # 滚动到顶部
        scroll = win.findChild(QScrollArea)
        if scroll:
            scroll.verticalScrollBar().setValue(0)
        pet_x, pet_y = self.x(), self.y()
        win_width, win_height = win.width(), win.height()
        x = pet_x + (self.width() - win_width) // 2
        y = pet_y - win_height - 5
        win.move(x, y)
        win.show()
        win.raise_()
        self.bubble_timer.start(8000)

    def hide_bubble(self):
        if self.bubble_window:
            self.bubble_window.hide()
            self.bubble_timer.stop()
            self.thinking_timer.stop()

    # -------------------- 全局 Esc 关闭浮动窗口 --------------------
    def on_global_esc(self):
        # 关闭输入窗口（如果可见）
        if self.input_window and self.input_window.isVisible():
            self.hide_input_window()
        # 关闭气泡（如果可见）
        if self.bubble_window and self.bubble_window.isVisible():
            self.hide_bubble()

    # -------------------- 事件过滤器（气泡悬停 + 输入框 Esc） --------------------
    def eventFilter(self, obj, event):
        if obj == self.bubble_window:
            if event.type() == QEvent.Enter:
                self.bubble_timer.stop()
            elif event.type() == QEvent.Leave:
                if self.bubble_window and self.bubble_window.isVisible():
                    self.bubble_timer.start(3000)
            return super().eventFilter(obj, event)
        elif obj == self.line_edit:
            if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
                self.hide_input_window()
                return True
            return super().eventFilter(obj, event)
        return super().eventFilter(obj, event)

    # -------------------- 动画 --------------------
    def next_run_frame(self):
        if not self.is_running:
            return
        self.run_index = (self.run_index + 1) % len(self.run_frames)
        pixmap = self.run_frames[self.run_index]
        if self.is_facing_left:
            pixmap = pixmap.transformed(QTransform().scale(-1, 1))
        self.label.setPixmap(pixmap)

    def update_pet_image(self):
        if self.is_running:
            pixmap = self.run_frames[self.run_index]
        else:
            pixmap = self.still_pixmap
        if self.is_facing_left:
            pixmap = pixmap.transformed(QTransform().scale(-1, 1))
        self.label.setPixmap(pixmap)

    # -------------------- 核心移动逻辑 --------------------
    def move_and_animate(self):
        if self.is_dragging:
            return

        target_x = None
        if self.mode == "follow":
            mouse_x = QCursor.pos().x()
            target_x = mouse_x - self.width() // 2
        elif self.mode == "free":
            if self.is_resting:
                if self.is_running:
                    self.is_running = False
                    self.update_pet_image()
                    self.run_index = 0
                target_x = None
            else:
                target_x = self.free_target_x
        else:  # still
            if self.is_running:
                self.is_running = False
                self.update_pet_image()
                self.run_index = 0
            target_x = None

        if target_x is not None:
            current_x = self.x()
            delta = target_x - current_x

            if abs(delta) <= self.ALIGN_THRESHOLD:
                new_x = target_x
                if self.mode == "free" and not self.is_resting:
                    self.schedule_next_action()
            else:
                step = self.SPEED if delta > 0 else -self.SPEED
                new_x = current_x + step
                if (delta > 0 and new_x > target_x) or (delta < 0 and new_x < target_x):
                    new_x = target_x
                    if self.mode == "free" and not self.is_resting:
                        self.schedule_next_action()

            screen = QApplication.primaryScreen()
            geometry = screen.availableGeometry()
            min_x = geometry.left()
            max_x = geometry.right() - self.width()
            new_x = max(min_x, min(new_x, max_x))
            new_x_int = int(new_x)
            y = geometry.bottom() - self.height()
            self.move(new_x_int, y)

            if abs(delta) > self.ALIGN_THRESHOLD:
                self.is_facing_left = delta < 0
                self.update_pet_image()

            displacement = abs(new_x_int - self.last_x)
            self.last_x = new_x_int
            if displacement < 1:
                self.still_accumulator += 16
            else:
                self.still_accumulator = 0

            if self.still_accumulator >= self.STILL_THRESHOLD:
                if self.is_running:
                    self.is_running = False
                    self.update_pet_image()
                    self.run_index = 0
            else:
                if abs(delta) > self.ALIGN_THRESHOLD and not self.is_running:
                    self.is_running = True
                    self.run_index = 0
                    self.update_pet_image()
        else:
            if self.mode == "free" and self.is_resting and self.is_running:
                self.is_running = False
                self.update_pet_image()
                self.run_index = 0

        # 跟随输入窗口和气泡
        if self.input_window and self.input_window.isVisible():
            pet_x, pet_y = self.x(), self.y()
            win_width, win_height = self.input_window.width(), self.input_window.height()
            x = pet_x + (self.width() - win_width) // 2
            y = pet_y - win_height - 5
            self.input_window.move(x, y)
            self.input_window.raise_()

        if self.bubble_window and self.bubble_window.isVisible():
            pet_x, pet_y = self.x(), self.y()
            win_width, win_height = self.bubble_window.width(), self.bubble_window.height()
            x = pet_x + (self.width() - win_width) // 2
            y = pet_y - win_height - 5
            self.bubble_window.move(x, y)
            self.bubble_window.raise_()

    # -------------------- 文件拖拽（吃文件，本地随机回复） --------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        mime_data = event.mimeData()
        if not mime_data.hasUrls():
            return
        urls = mime_data.urls()
        if not urls:
            return
        file_path = urls[0].toLocalFile()
        if not file_path or not os.path.exists(file_path):
            self.show_bubble("文件不存在呢～")
            return

        filename = os.path.basename(file_path)
        # 随机选一句弗洛洛风格的回复
        reply = random.choice(self.eat_replies)
        self.show_bubble(f"吃掉 {filename}\n{reply}")

        try:
            send2trash(file_path)
            print(f"已移动 {file_path} 到回收站")
        except Exception as e:
            self.show_bubble(f"吃不下（删除失败）: {str(e)}")
            print(f"删除失败: {e}")

    # -------------------- 程序退出时安全终止线程 --------------------
    def closeEvent(self, event):
        if self.ai_worker and self.ai_worker.isRunning():
            self.ai_worker.quit()
            self.ai_worker.wait()
            self.ai_worker = None
        event.accept()


# -------------------- 入口 --------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    pet.raise_()
    pet.activateWindow()
    sys.exit(app.exec_())