import sys
import textwrap
import pygame
from src.config import (
    WIDTH, HEIGHT, TITLE, FPS, IS_FULLSCREEN,
    FONT_SIZE_LARGE, FONT_SIZE_SMALL, TEXT_COLOR_WHITE,
    KEY_LOG_MAX_CHARS, KEY_LOG_FONT_SIZE, KEY_LOG_COLOR,
    KEY_LOG_ALPHA, KEY_LOG_MARGIN, KEY_LOG_LINE_WIDTH,
)
from src.particles import ParticleManager
from src.key_handler import KeyHandler
from src.media_manager import MediaManager
from src.image_scroller import ImageScroller


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
        self.font_log = pygame.font.SysFont(None, KEY_LOG_FONT_SIZE)

        self.particle_manager = ParticleManager(self.width, self.height)
        self.media_manager = MediaManager()
        self.image_scroller = ImageScroller()
        self.key_handler = KeyHandler(
            self.particle_manager,
            self.media_manager,
            self.image_scroller
        )

        # キーログ（左上に薄く表示する押下履歴文字列）
        self._key_log = ""

    def _push_key_log(self, char: str):
        """キーログに1文字追加。上限を超えたらクリア"""
        self._key_log += char
        if len(self._key_log) > KEY_LOG_MAX_CHARS:
            self._key_log = ""

    def _draw_key_log(self):
        """キーログを左上に薄い文字で描画"""
        if not self._key_log:
            return

        lines = textwrap.wrap(self._key_log, KEY_LOG_LINE_WIDTH) or [""]
        y = KEY_LOG_MARGIN
        for line in lines:
            surf = self.font_log.render(line, True, KEY_LOG_COLOR)
            surf.set_alpha(KEY_LOG_ALPHA)
            self.screen.blit(surf, (KEY_LOG_MARGIN, y))
            y += self.font_log.get_height() + 2

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
                        running = False

                # キーログ更新（display_text が変わったらその文字を追記）
                last_char = self.key_handler.display_text.replace("KEY: ", "")
                if last_char and last_char != "キーを押してね！":
                    self._push_key_log(last_char if last_char != "SPACE" else " ")

                # 状態更新
                self.particle_manager.update()
                self.media_manager.update_video(self.width, self.height)
                self.image_scroller.update(self.width, self.height)

                # 背景色塗りつぶし
                self.screen.fill(self.key_handler.background_color)

                # キーログ描画（背景の直後・最背面）
                self._draw_key_log()

                # 中央テキスト描画
                text_surf = self.font_large.render(
                    self.key_handler.display_text, True, TEXT_COLOR_WHITE
                )
                text_rect = text_surf.get_rect(center=(self.width // 2, self.height // 2))
                self.screen.blit(text_surf, text_rect)

                # パーティクル描画
                self.particle_manager.draw(self.screen, self.font_small)

                # スクロール画像描画
                self.image_scroller.draw(self.screen)

                # 再生中の動画描画
                self.media_manager.draw_video(self.screen)

                pygame.display.flip()
                self.clock.tick(FPS)

        except Exception as e:
            print(f"エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()

    def cleanup(self):
        """リソースの解放および終了処理"""
        self.key_handler.stop_hook()
        self.media_manager.stop_video()
        pygame.quit()
        sys.exit(0)

