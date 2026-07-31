import random
import pygame

class Particle:
    """単一のパーティクル（文字エフェクト）を表すクラス"""
    def __init__(self, text, x, y, speed=0, life=None, color=None):
        self.text = text
        self.x = x
        self.y = y
        self.speed = speed
        self.life = life
        self.color = color or (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255)
        )

    def update(self, screen_height: int) -> bool:
        """パーティクルの状態を更新。消去対象になった場合は False を返す。"""
        self.y += self.speed
        if self.life is not None:
            self.life -= 1
            if self.life <= 0:
                return False
        elif self.y > screen_height:
            return False
        return True

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """パーティクルをサーフェスに描画"""
        text_surf = font.render(self.text, True, self.color)
        surface.blit(text_surf, (self.x, self.y))


class ParticleManager:
    """パーティクルのコレクションおよび生成・更新・描画を管理するクラス"""
    def __init__(self, width: int = 800, height: int = 600):
        self.particles = []
        self.width = width
        self.height = height

    def set_screen_size(self, width: int, height: int):
        """画面サイズを更新"""
        self.width = width
        self.height = height

    def add_normal_key_effect(self, char_name: str):
        """通常キー押下時のポップアップ文字を生成"""
        min_x = min(100, self.width // 4)
        max_x = max(min_x + 1, self.width - min_x)
        min_y = min(100, self.height // 4)
        max_y = max(min_y + 1, self.height - min_y)

        particle = Particle(
            text=char_name.upper(),
            x=random.randint(min_x, max_x),
            y=random.randint(min_y, max_y),
            speed=0,
            life=30,
            color=(255, 255, 255)
        )
        self.particles.append(particle)

    def add_alphabet_rain(self):
        """'a' キー押下時の小文字アルファベット下降エフェクトを生成"""
        self._add_rain_effect("abcdefghijklmnopqrstuvwxyz")

    def add_uppercase_rain(self):
        """大文字アルファベット下降エフェクトを生成"""
        self._add_rain_effect("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    def add_hiragana_rain(self):
        """ひらがな下降エフェクトを生成"""
        chars = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれをん"
        self._add_rain_effect(chars)

    def add_katakana_rain(self):
        """カタカナ下降エフェクトを生成"""
        chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレヲン"
        self._add_rain_effect(chars)

    def add_number_symbol_rain(self):
        """数字・記号下降エフェクトを生成"""
        chars = "0123456789!@#$%^&*()_+-=[]{}|;:,.<>/?"
        self._add_rain_effect(chars)

    def _add_rain_effect(self, chars: str, count: int = 35):
        """指定された文字群からパーティクルの雨を降らせる共通内部処理"""
        min_x = min(50, self.width // 10)
        max_x = max(min_x + 1, self.width - min_x)

        target_chars = [random.choice(chars) for _ in range(count)] if len(chars) > count else list(chars)
        for char in target_chars:
            particle = Particle(
                text=char,
                x=random.randint(min_x, max_x),
                y=random.randint(-200, 0),
                speed=random.randint(5, 12)
            )
            self.particles.append(particle)

    def update(self):
        """全パーティクルの状態を更新"""
        self.particles = [p for p in self.particles if p.update(self.height)]

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """全パーティクルを描画"""
        for p in self.particles:
            p.draw(surface, font)
