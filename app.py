import sys
import pygame
from config import (
    WIDTH, HEIGHT, TITLE, FPS, IS_FULLSCREEN,
    FONT_SIZE_LARGE, FONT_SIZE_SMALL, TEXT_COLOR_WHITE
)
from particles import ParticleManager
from key_handler import KeyHandler

class BabyToyApp:
    """アプリケーションのメインウィンドウと描画ループを管理するクラス"""
    def __init__(self):
        pygame.init()

        if IS_FULLSCREEN:
            info = pygame.display.Info()
            self.width, self.height = info.current_w, info.current_h
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        else:
            self.width, self.height = WIDTH, HEIGHT
            self.screen = pygame.display.set_mode((self.width, self.height))

        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.font_large = pygame.font.SysFont(None, FONT_SIZE_LARGE)
        self.font_small = pygame.font.SysFont(None, FONT_SIZE_SMALL)

        self.particle_manager = ParticleManager(self.width, self.height)
        self.key_handler = KeyHandler(self.particle_manager)

    def run(self):
        """アプリケーションを開始してメインループを実行"""
        self.key_handler.start_hook()
        running = True

        try:
            while running:
                if self.key_handler.is_exit_requested:
                    break

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        # ESCキーでも全画面を安全に終了できるように補助
                        running = False

                # 画面更新
                self.particle_manager.update()

                # 背景色塗りつぶし
                self.screen.fill(self.key_handler.background_color)

                # 中央テキスト描画
                text_surf = self.font_large.render(
                    self.key_handler.display_text, True, TEXT_COLOR_WHITE
                )
                text_rect = text_surf.get_rect(center=(self.width // 2, self.height // 2))
                self.screen.blit(text_surf, text_rect)

                # パーティクル描画
                self.particle_manager.draw(self.screen, self.font_small)

                pygame.display.flip()
                self.clock.tick(FPS)

        except Exception as e:
            print(f"エラーが発生しました: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """リソースの解放および終了処理"""
        self.key_handler.stop_hook()
        pygame.quit()
        sys.exit(0)
