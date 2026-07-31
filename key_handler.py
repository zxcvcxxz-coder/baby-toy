import random
import keyboard
from config import (
    EXIT_SECRET, DEFAULT_BACKGROUND_COLOR, DEFAULT_DISPLAY_TEXT,
    ALLOWED_CHARS, ALLOWED_KEY_NAMES
)
from particles import ParticleManager

class KeyHandler:
    """キーフックおよびホワイトリスト方式による入力状態制御を管理するクラス"""
    def __init__(self, particle_manager: ParticleManager):
        self.particle_manager = particle_manager
        self.pressed_keys = []
        self.is_exit_requested = False
        self.background_color = DEFAULT_BACKGROUND_COLOR
        self.display_text = DEFAULT_DISPLAY_TEXT

    def is_key_allowed(self, name: str) -> bool:
        """入力されたキーがホワイトリストに含まれるか判定"""
        if name in ALLOWED_CHARS or name in ALLOWED_KEY_NAMES:
            return True
        return False

    def handle_key_event(self, event):
        """キーボードフックイベントのコールバック"""
        name = event.name.lower()

        # 1. 終了コマンドの判定
        if name == EXIT_SECRET[len(self.pressed_keys)]:
            self.pressed_keys.append(name)
            if self.pressed_keys == EXIT_SECRET:
                self.is_exit_requested = True
        else:
            if name == EXIT_SECRET[0]:
                self.pressed_keys = [name]
            else:
                self.pressed_keys = []

        # 2. ホワイトリストによる制御
        if not self.is_exit_requested:
            # ホワイトリストに含まれないキー（MyASUSキー、各種Fキー、特殊ベンダーキー等）は一切無視
            if not self.is_key_allowed(name):
                return False

            # ホワイトリストに合致したキーのみアクションを実行
            self.background_color = (
                random.randint(20, 100),
                random.randint(20, 100),
                random.randint(50, 150)
            )

            # 表示テキストの整形
            display_name = "SPACE" if name == "space" else name.upper()
            self.display_text = f"KEY: {display_name}"

            if name == 'a':
                self.particle_manager.add_alphabet_rain()
            else:
                self.particle_manager.add_normal_key_effect(display_name)

        return False

    def start_hook(self):
        """キーフックを開始（すべての入力を抑制し、ホワイトリストのみ受け付ける）"""
        keyboard.hook(
            lambda e: self.handle_key_event(e) if e.event_type == keyboard.KEY_DOWN else None,
            suppress=True
        )

    def stop_hook(self):
        """キーフックを解除"""
        keyboard.unhook_all()
