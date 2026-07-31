import os
import cv2
import pygame
from config import (
    KEY_MEDIA_MAP,
    VIDEO_WINDOW_WIDTH,
    VIDEO_WINDOW_HEIGHT,
    VIDEO_WINDOW_POSITION
)

class MediaManager:
    """効果音(assets/se)および動画(assets/vid)の再生管理クラス"""
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.sounds = {}
        self.cap = None
        self.is_video_playing = False
        self.video_surface = None

        # pygame.mixer の初期化チェック
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # 音声ファイルの事前ロード
        self._load_sounds()

    def _load_sounds(self):
        """KEY_MEDIA_MAP に登録されているSEファイルを事前に読み込む"""
        se_dir = os.path.join(self.base_dir, "assets", "se")
        if not os.path.exists(se_dir):
            return

        for key, (media_type, filename) in KEY_MEDIA_MAP.items():
            if media_type == 'se':
                filepath = os.path.join(se_dir, filename)
                if os.path.exists(filepath):
                    try:
                        self.sounds[filename] = pygame.mixer.Sound(filepath)
                    except Exception as e:
                        print(f"音源ロードエラー ({filename}): {e}")

    def play_media_for_key(self, key_name: str) -> bool:
        """キーに対応するメディア（音源または動画）が存在すれば再生を開始"""
        key_name = key_name.lower()
        if key_name not in KEY_MEDIA_MAP:
            return False

        media_type, filename = KEY_MEDIA_MAP[key_name]

        if media_type == 'se':
            filepath = os.path.join(self.base_dir, "assets", "se", filename)
            if filename in self.sounds:
                self.sounds[filename].play()
                return True
            elif os.path.exists(filepath):
                try:
                    sound = pygame.mixer.Sound(filepath)
                    sound.play()
                    return True
                except Exception as e:
                    print(f"音源再生エラー: {e}")

        elif media_type == 'vid':
            filepath = os.path.join(self.base_dir, "assets", "vid", filename)
            if os.path.exists(filepath):
                self.stop_video()
                self.cap = cv2.VideoCapture(filepath)
                if self.cap.isOpened():
                    self.is_video_playing = True
                    return True

        return False

    def update_video(self, target_width: int, target_height: int):
        """動画が再生中の場合、フレームを更新して指定小窓サイズにリサイズ"""
        if not self.is_video_playing or self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            # 動画再生終了
            self.stop_video()
            return

        # OpenCV (BGR) -> Pygame (RGB) 変換
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        h, w, c = frame_rgb.shape
        surf = pygame.image.frombuffer(frame_rgb.tobytes(), (w, h), "RGB")

        # 設定された小窓サイズにアスペクト比維持でスケール
        scale = min(VIDEO_WINDOW_WIDTH / w, VIDEO_WINDOW_HEIGHT / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        self.video_surface = pygame.transform.smoothscale(surf, (new_w, new_h))

    def draw_video(self, screen: pygame.Surface):
        """再生中の動画フレームをウィンドウ枠(ポップアップ風)で指定位置に描画"""
        if not self.is_video_playing or self.video_surface is None:
            return

        sw, sh = screen.get_width(), screen.get_height()
        vw, vh = self.video_surface.get_width(), self.video_surface.get_height()

        # ウィンドウ枠のサイズ（余白・ヘッダー部分を含む）
        padding = 10
        header_height = 24
        frame_w = vw + (padding * 2)
        frame_h = vh + padding + header_height

        margin = 25  # 画面端からのマージン
        pos = VIDEO_WINDOW_POSITION.lower()

        # 表示位置の計算
        if pos == "bottom_right":
            x = sw - frame_w - margin
            y = sh - frame_h - margin
        elif pos == "top_right":
            x = sw - frame_w - margin
            y = margin
        elif pos == "bottom_left":
            x = margin
            y = sh - frame_h - margin
        elif pos == "top_left":
            x = margin
            y = margin
        else:  # center
            x = (sw - frame_w) // 2
            y = (sh - frame_h) // 2

        # 1. 影（ドロップシャドウ）
        shadow_rect = pygame.Rect(x + 5, y + 5, frame_w, frame_h)
        pygame.draw.rect(screen, (10, 10, 15, 120), shadow_rect, border_radius=12)

        # 2. ウィンドウ枠の背景
        frame_rect = pygame.Rect(x, y, frame_w, frame_h)
        pygame.draw.rect(screen, (40, 45, 60), frame_rect, border_radius=12)
        pygame.draw.rect(screen, (100, 180, 255), frame_rect, width=3, border_radius=12)

        # 3. ヘッダー部の装飾ボタン（赤・黄・緑のドット）
        dot_colors = [(255, 95, 86), (255, 189, 46), (39, 201, 63)]
        for i, color in enumerate(dot_colors):
            dot_x = x + 15 + (i * 16)
            dot_y = y + (header_height // 2) + 2
            pygame.draw.circle(screen, color, (dot_x, dot_y), 5)

        # 4. 動画本体の描画
        vid_x = x + padding
        vid_y = y + header_height
        screen.blit(self.video_surface, (vid_x, vid_y))

    def stop_video(self):
        """動画再生を停止しリソースを解放"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_video_playing = False
        self.video_surface = None

