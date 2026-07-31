import random
import queue
import keyboard
from src.config import (
    EXIT_SECRETS, DEFAULT_BACKGROUND_COLOR, DEFAULT_DISPLAY_TEXT,
    ALLOWED_CHARS, ALLOWED_KEY_NAMES, IMAGE_SCROLL_KEYS
)
from src.particles import ParticleManager
from src.media_manager import MediaManager
from src.image_scroller import ImageScroller

class KeyHandler:
    """キーフックおよびホワイトリスト方式による入力状態制御をスレッドセーフに管理するクラス"""
    def __init__(self, particle_manager: ParticleManager, media_manager: MediaManager = None,
                 image_scroller: ImageScroller = None):
        self.particle_manager = particle_manager
        self.media_manager = media_manager
        self.image_scroller = image_scroller
        self.pressed_history = ""
        self.currently_pressed = set()  # 現在押しっぱなしになっているキー
        self.event_queue = queue.Queue(maxsize=30)  # サブスレッドからメインスレッドへのキー渡し用スレッドセーフキュー
        self.is_exit_requested = False
        self.background_color = DEFAULT_BACKGROUND_COLOR
        self.display_text = DEFAULT_DISPLAY_TEXT
        self.pending_log_chars = []

    def pop_pending_log_chars(self) -> list:
        """蓄積されたログ用キー文字を取得してキューをクリア"""
        chars = list(self.pending_log_chars)
        self.pending_log_chars.clear()
        return chars

    def is_key_allowed(self, name: str) -> bool:
        """入力されたキーがホワイトリストに含まれるか判定"""
        if name in ALLOWED_CHARS or name in ALLOWED_KEY_NAMES:
            return True
        return False

    def process_pending_events(self):
        """メインスレッドから毎フレーム呼び出され、蓄積されたキーイベントを1つずつ安全に処理"""
        while not self.event_queue.empty():
            try:
                name = self.event_queue.get_nowait()
                self._handle_key_action(name)
            except queue.Empty:
                break

    def _handle_key_action(self, name: str):
        """メインスレッド上で安全に実行されるキーアクション処理"""
        # 1. 終了コマンドの判定
        self.pressed_history += name
        if len(self.pressed_history) > 50:
            self.pressed_history = self.pressed_history[-50:]

        for secret in EXIT_SECRETS:
            if self.pressed_history.endswith(secret):
                self.is_exit_requested = True
                return

        # 2. ホワイトリストによる制御
        if not self.is_exit_requested:
            if not self.is_key_allowed(name):
                return

            # 特定のキーに対応する音源・動画の再生を試みる (メインスレッドで実行されるため100%安全)
            if self.media_manager is not None:
                self.media_manager.play_media_for_key(name)

            # 画像スクロールキーの場合はスクロールをトリガー
            if self.image_scroller is not None and name in IMAGE_SCROLL_KEYS:
                self.image_scroller.trigger()

            # 背景色の変更
            self.background_color = (
                random.randint(20, 100),
                random.randint(20, 100),
                random.randint(50, 150)
            )

            # 表示テキストの整形
            display_name = "SPACE" if name == "space" else name.upper()
            self.display_text = f"KEY: {display_name}"

            # 背景履歴（キーログ）に記録する1文字を決定して追加
            log_char = " " if name == "space" else (display_name if len(display_name) == 1 else display_name[0])
            self.pending_log_chars.append(log_char)

            # パーティクル演出
            if name == 'a':
                self.particle_manager.add_alphabet_rain()
            elif name == 'u':
                self.particle_manager.add_uppercase_rain()
            elif name == 'h':
                self.particle_manager.add_hiragana_rain()
            elif name == 'k':
                self.particle_manager.add_katakana_rain()
            elif name == 'n' or name.isdigit():
                self.particle_manager.add_number_symbol_rain()
            else:
                self.particle_manager.add_normal_key_effect(display_name)

    def _on_keyboard_event(self, event):
        """キーフックスレッド（サブスレッド）から呼ばれる軽量ハンドラ"""
        name = event.name.lower()

        if event.event_type == keyboard.KEY_DOWN:
            if name in self.currently_pressed:
                # 長押しの連打イベントは無視
                return False
            self.currently_pressed.add(name)

            # Pygame/OpenCVは呼び出さず、スレッドセーフキューに文字を入れるだけ！
            try:
                self.event_queue.put_nowait(name)
            except queue.Full:
                pass
            return False

        elif event.event_type == keyboard.KEY_UP:
            self.currently_pressed.discard(name)

        return False

    def start_hook(self):
        """キーフックを開始"""
        keyboard.hook(self._on_keyboard_event, suppress=True)

    def stop_hook(self):
        """キーフックを解除"""
        keyboard.unhook_all()
        self.currently_pressed.clear()

