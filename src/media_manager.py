import os
import random
import time
import cv2
import pygame
from src.config import (
    KEY_MEDIA_MAP,
    VIDEO_WINDOW_WIDTH,
    VIDEO_WINDOW_HEIGHT,
    MAX_VIDEO_WINDOWS,
    VIDEO_FRAME_SKIP,
    WIDTH,
    HEIGHT,
    SE_DIR,
    VID_DIR
)

class ActiveVideo:
    """再生中の各動画ウィンドウを管理するクラス"""
    def __init__(self, filepath: str, x: int, y: int):
        self.filepath = filepath
        self.x = x
        self.y = y
        self.cap = cv2.VideoCapture(str(filepath))
        self.is_finished = not self.cap.isOpened()
        self.surface = None
        self._frame_counter = 0  # フレームスキップ用カウンタ

    def update(self) -> bool:
        """フレームスキップ付きで次のフレームを取得し Pygame Surface に変換"""
        if self.is_finished or self.cap is None:
            return False

        try:
            self._frame_counter += 1

            # フレームスキップ: VIDEO_FRAME_SKIP フレームに1回だけデコード
            if self._frame_counter % VIDEO_FRAME_SKIP != 0:
                # フレームを読み進めるだけでデコードはスキップ
                self.cap.grab()
                return True

            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.stop()
                return False

            # OpenCV BGR -> RGB 変換 (リサイズ先を先に決めてからデコード)
            h, w = frame.shape[:2]
            scale = min(VIDEO_WINDOW_WIDTH / w, VIDEO_WINDOW_HEIGHT / h)
            new_w = max(1, int(w * scale))
            new_h = max(1, int(h * scale))

            # OpenCV側で先にリサイズしてからPygameに渡す（負荷が低い）
            small_frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            frame_rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            self.surface = pygame.image.frombuffer(frame_rgb.tobytes(), (new_w, new_h), "RGB").copy()
            return True
        except Exception as e:
            print(f"動画デコード処理エラー: {e}")
            self.stop()
            return False

    def restart(self):
        """動画を先頭フレームに巻き戻して即座に再スタート（開き直し負荷ゼロ）"""
        if self.cap is not None and self.cap.isOpened():
            try:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.is_finished = False
                self._frame_counter = 0
            except Exception:
                pass

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
    def __init__(self):
        self.sounds = {}
        self.active_videos = []
        self.screen_width = WIDTH
        self.screen_height = HEIGHT
        self.last_video_trigger_time = 0.0  # 連打保護用タイムスタンプ

        # pygame.mixer の初期化チェック
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # 音声ファイルの事前ロード
        self._load_sounds()

    def _load_sounds(self):
        """KEY_MEDIA_MAP に登録されているSEファイルを事前に読み込む"""
        if not SE_DIR.exists():
            return

        for key, (media_type, filename) in KEY_MEDIA_MAP.items():
            if media_type == 'se':
                filepath = SE_DIR / filename
                if filepath.exists():
                    try:
                        self.sounds[filename] = pygame.mixer.Sound(str(filepath))
                    except Exception as e:
                        print(f"音源ロードエラー ({filename}): {e}")

    def play_media_for_key(self, key_name: str) -> bool:
        """キーに対応するメディア（音源または動画）が存在すれば再生を開始"""
        key_name = key_name.lower()
        if key_name not in KEY_MEDIA_MAP:
            return False

        media_type, filename = KEY_MEDIA_MAP[key_name]

        if media_type == 'se':
            filepath = SE_DIR / filename
            if filename in self.sounds:
                self.sounds[filename].play()
                return True
            elif filepath.exists():
                try:
                    sound = pygame.mixer.Sound(str(filepath))
                    sound.play()
                    return True
                except Exception as e:
                    print(f"音源再生エラー: {e}")

        elif media_type == 'vid':
            filepath = VID_DIR / filename
            if filepath.exists():
                str_path = str(filepath)

                # 既存の動画を停止・消去してリセット
                self.stop_video()

                # 改めて画面内のランダムな別座標（x, y）を計算
                frame_w = VIDEO_WINDOW_WIDTH + 16
                frame_h = VIDEO_WINDOW_HEIGHT + 16
                max_x = max(20, self.screen_width - frame_w - 20)
                max_y = max(20, self.screen_height - frame_h - 20)

                x = random.randint(20, max_x)
                y = random.randint(20, max_y)

                try:
                    # 改めて別座標で新しい動画ウィンドウを生成して再生開始
                    new_vid = ActiveVideo(str_path, x, y)
                    if not new_vid.is_finished:
                        self.active_videos.append(new_vid)
                        return True
                except Exception as e:
                    print(f"動画再生起動エラー ({filename}): {e}")

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
