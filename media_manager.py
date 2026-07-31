import os
import random
import cv2
import pygame
from config import (
    KEY_MEDIA_MAP,
    VIDEO_WINDOW_WIDTH,
    VIDEO_WINDOW_HEIGHT,
    MAX_VIDEO_WINDOWS,
    WIDTH,
    HEIGHT
)

class ActiveVideo:
    """再生中の各動画ウィンドウを管理するクラス"""
    def __init__(self, filepath: str, x: int, y: int):
        self.filepath = filepath
        self.x = x
        self.y = y
        self.cap = cv2.VideoCapture(filepath)
        self.is_finished = not self.cap.isOpened()
        self.surface = None

    def update(self) -> bool:
        """次の動画フレームを取得してリサイズ Pygame Surface に変換"""
        if self.is_finished or self.cap is None:
            return False

        ret, frame = self.cap.read()
        if not ret:
            self.stop()
            return False

        # OpenCV (BGR) -> Pygame (RGB) 変換
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame_rgb.shape
        surf = pygame.image.frombuffer(frame_rgb.tobytes(), (w, h), "RGB")

        # 指定サイズにアスペクト比維持でスケール
        scale = min(VIDEO_WINDOW_WIDTH / w, VIDEO_WINDOW_HEIGHT / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        self.surface = pygame.transform.smoothscale(surf, (new_w, new_h))
        return True

    def draw(self, screen: pygame.Surface):
        """動画と可愛い角丸枠を自らの (x, y) 座標に描画"""
        if self.surface is None:
            return

        vw, vh = self.surface.get_width(), self.surface.get_height()
        padding = 8
        frame_w = vw + (padding * 2)
        frame_h = vh + (padding * 2)

        # 1. 影（ドロップシャドウ）
        shadow_rect = pygame.Rect(self.x + 4, self.y + 4, frame_w, frame_h)
        pygame.draw.rect(screen, (15, 15, 25, 100), shadow_rect, border_radius=16)

        # 2. フレーム枠の背景（丸みのあるポップな枠）
        frame_rect = pygame.Rect(self.x, self.y, frame_w, frame_h)
        pygame.draw.rect(screen, (35, 40, 55), frame_rect, border_radius=16)
        pygame.draw.rect(screen, (140, 200, 255), frame_rect, width=3, border_radius=16)

        # 3. 動画本体の描画
        vid_x = self.x + padding
        vid_y = self.y + padding
        screen.blit(self.surface, (vid_x, vid_y))


    def stop(self):
        """キャプチャのリソース解放"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_finished = True


class MediaManager:
    """効果音(assets/se)および複数動画(assets/vid)の再生管理クラス"""
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.sounds = {}
        self.active_videos = []
        self.screen_width = WIDTH
        self.screen_height = HEIGHT

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
                # 最大同時表示数 (MAX_VIDEO_WINDOWS) を超えていたら、一番古い動画を破棄
                if len(self.active_videos) >= MAX_VIDEO_WINDOWS:
                    oldest_vid = self.active_videos.pop(0)
                    oldest_vid.stop()

                # 画面枠に収まるランダム座標を計算
                frame_w = VIDEO_WINDOW_WIDTH + 20
                frame_h = VIDEO_WINDOW_HEIGHT + 34
                max_x = max(20, self.screen_width - frame_w - 20)
                max_y = max(20, self.screen_height - frame_h - 20)

                x = random.randint(20, max_x)
                y = random.randint(20, max_y)

                # 新しい動画ウィンドウを生成して追加
                new_vid = ActiveVideo(filepath, x, y)
                if not new_vid.is_finished:
                    self.active_videos.append(new_vid)
                    return True

        return False

    def update_video(self, target_width: int, target_height: int):
        """すべてのアクティブな動画ウィンドウのフレームを更新"""
        self.screen_width = target_width
        self.screen_height = target_height

        still_active = []
        for vid in self.active_videos:
            if vid.update():
                still_active.append(vid)
            else:
                vid.stop()

        self.active_videos = still_active

    def draw_video(self, screen: pygame.Surface):
        """すべてのアクティブな動画ウィンドウを画面に描画"""
        for vid in self.active_videos:
            vid.draw(screen)

    def stop_video(self):
        """全動画の再生を停止しリソースを解放"""
        for vid in self.active_videos:
            vid.stop()
        self.active_videos.clear()


