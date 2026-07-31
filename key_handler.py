import random
import keyboard
from config import (
    EXIT_SECRET, DEFAULT_BACKGROUND_COLOR, DEFAULT_DISPLAY_TEXT,
    ALLOWED_CHARS, ALLOWED_KEY_NAMES
)
from particles import ParticleManager
from media_manager import MediaManager

class KeyHandler:
    """キーフックおよびホワイトリスト方式による入力状態制御を管理するクラス"""
    def __init__(self, particle_manager: ParticleManager, media_manager: MediaManager = None):
        self.particle_manager = particle_manager
        self.media_manager = media_manager
        self.pressed_history = ""
        self.currently_pressed = set()
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

    def handle_key_event(self, event):
        """キーボードフックイベントのコールバック"""
        name = event.name.lower()

        # 1. 終了コマンドの判定
        self.pressed_history += name
        if len(self.pressed_history) > 50:
            self.pressed_history = self.pressed_history[-50:]

        for secret in EXIT_SECRETS:
            if self.pressed_history.endswith(secret):
                self.is_exit_requested = True
                break

        # 2. ホワイトリストによる制御
        if not self.is_exit_requested:
            # ホワイトリストに含まれないキーは無視
            if not self.is_key_allowed(name):
                return False

            # 特定のキーに対応する音源・動画の再生を試みる
            if self.media_manager is not None:
                self.media_manager.play_media_for_key(name)

            # ホワイトリストに合致したキーアクション
            self.background_color = (
                random.randint(20, 100),
                random.randint(20, 100),
                random.randint(50, 150)
            )

            # 表示テキストの整形
            display_name = "SPACE" if name == "space" else name.upper()
            self.display_text = f"KEY: {display_name}"

            # 背景履歴（キーログ）に記録する1文字を決定してキューに追加
            log_char = " " if name == "space" else (display_name if len(display_name) == 1 else display_name[0])
            self.pending_log_chars.append(log_char)

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

        return False

    def _on_keyboard_event(self, event):
        """キーイベントのハンドラ（KEY_DOWNの長押し連打を無効化）"""
        name = event.name.lower()

        if event.event_type == keyboard.KEY_DOWN:
            if name in self.currently_pressed:
                return False
            self.currently_pressed.add(name)
            return self.handle_key_event(event)
        elif event.event_type == keyboard.KEY_UP:
            self.currently_pressed.discard(name)

        return False

    def start_hook(self):
        """キーフックを開始（すべての入力を抑制し、ホワイトリストのみ受け付ける）"""
        keyboard.hook(self._on_keyboard_event, suppress=True)

    def stop_hook(self):
        """キーフックを解除"""
        keyboard.unhook_all()
        self.currently_pressed.clear()

