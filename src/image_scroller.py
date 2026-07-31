"""
assets/Image/ 内の画像をランダムな方向から流すスクロールエフェクト管理
"""
import random
import pygame
from pathlib import Path
from src.config import (
    IMAGE_DIR,
    IMAGE_SCROLL_SPEED,
    IMAGE_SCROLL_SIZE,
    IMAGE_SCROLL_DIRECTIONS,
)

SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp'}


class ScrollImage:
    """画面をスクロールする1枚の画像を管理するクラス"""

    def __init__(self, surface: pygame.Surface, direction: str, screen_w: int, screen_h: int):
        """
        direction: 'left'  → 右端から出現し左に移動
                   'right' → 左端から出現し右に移動
                   'up'    → 下端から出現し上に移動
                   'down'  → 上端から出現し下に移動
        """
        self.surface = surface
        self.direction = direction
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.finished = False

        sw, sh = surface.get_size()

        # ランダムな垂直/水平オフセット（進行方向に垂直な軸）
        if direction in ('left', 'right'):
            self.y = random.randint(0, max(0, screen_h - sh))
        else:
            self.x = random.randint(0, max(0, screen_w - sw))

        # 方向に応じた初期位置
        if direction == 'left':
            self.x = screen_w
            self.vx, self.vy = -IMAGE_SCROLL_SPEED, 0
        elif direction == 'right':
            self.x = -sw
            self.vx, self.vy = IMAGE_SCROLL_SPEED, 0
        elif direction == 'up':
            self.y = screen_h
            self.vx, self.vy = 0, -IMAGE_SCROLL_SPEED
        elif direction == 'down':
            self.y = -sh
            self.vx, self.vy = 0, IMAGE_SCROLL_SPEED

    def update(self) -> bool:
        """位置を更新。画面外に出たら False を返す"""
        self.x += self.vx
        self.y += self.vy

        sw, sh = self.surface.get_size()
        if self.direction == 'left' and self.x + sw < 0:
            return False
        if self.direction == 'right' and self.x > self.screen_w:
            return False
        if self.direction == 'up' and self.y + sh < 0:
            return False
        if self.direction == 'down' and self.y > self.screen_h:
            return False
        return True

    def draw(self, screen: pygame.Surface):
        """画像を画面に描画"""
        screen.blit(self.surface, (int(self.x), int(self.y)))


class ImageScroller:
    """assets/Image/ の画像をランダムに選びスクロールエフェクトを管理するクラス"""

    def __init__(self):
        self.images: list[pygame.Surface] = []
        self.active: list[ScrollImage] = []
        self.screen_w = 800
        self.screen_h = 600
        self._load_images()

    def _load_images(self):
        """IMAGE_DIR 内のサポート画像を全てロード・リサイズ"""
        if not IMAGE_DIR.exists():
            print(f"[ImageScroller] 画像ディレクトリが見つかりません: {IMAGE_DIR}")
            return

        for path in IMAGE_DIR.iterdir():
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                try:
                    surf = pygame.image.load(str(path)).convert_alpha()
                    # IMAGE_SCROLL_SIZE を短辺基準にリサイズ
                    w, h = surf.get_size()
                    scale = IMAGE_SCROLL_SIZE / min(w, h)
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    surf = pygame.transform.smoothscale(surf, (new_w, new_h))
                    self.images.append(surf)
                except Exception as e:
                    print(f"[ImageScroller] 画像ロードエラー ({path.name}): {e}")

        print(f"[ImageScroller] {len(self.images)} 枚の画像をロードしました。")

    def trigger(self):
        """ランダムな画像をランダムな方向でスクロール開始"""
        if not self.images:
            return

        surf = random.choice(self.images)
        direction = random.choice(IMAGE_SCROLL_DIRECTIONS)
        scroll_img = ScrollImage(surf, direction, self.screen_w, self.screen_h)
        self.active.append(scroll_img)

    def update(self, screen_w: int, screen_h: int):
        """全アクティブ画像の位置を更新し、画面外に出たものを削除"""
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.active = [img for img in self.active if img.update()]

    def draw(self, screen: pygame.Surface):
        """全アクティブ画像を描画"""
        for img in self.active:
            img.draw(screen)
