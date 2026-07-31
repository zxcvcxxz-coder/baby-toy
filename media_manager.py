import os
import cv2
import pygame
from config import KEY_MEDIA_MAP

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

        # 音声ファイルの事前ロード（エラー回避のため）
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
        """動画が再生中の場合、フレームを更新して Pygame Surface に変換"""
        if not self.is_video_playing or self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            # 動画再生終了
            self.stop_video()
            return

        # OpenCV (BGR) -> Pygame (RGB) 変換
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Pygame Surface に変換 (OpenCV の shape は (height, width, channels))
        h, w, c = frame_rgb.shape
        surf = pygame.image.frombuffer(frame_rgb.tobytes(), (w, h), "RGB")

        # 画面サイズに合わせてスケール（アスペクト比維持）
        scale = min(target_width / w, target_height / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        self.video_surface = pygame.transform.smoothscale(surf, (new_w, new_h))

    def draw_video(self, screen: pygame.Surface):
        """再生中の動画フレームを画面中央に描画"""
        if self.is_video_playing and self.video_surface is not None:
            rect = self.video_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(self.video_surface, rect)

    def stop_video(self):
        """動画再生を停止しリソースを解放"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_video_playing = False
        self.video_surface = None
