"""
アプリケーションの設定値および定数定義
"""
import string

# 画面設定
WIDTH = 800
HEIGHT = 600
TITLE = "赤ちゃん用おもちゃアプリ"
FPS = 60
IS_FULLSCREEN = True  # 全画面モードフラグ

# 初期表示設定
DEFAULT_BACKGROUND_COLOR = (30, 30, 40)
DEFAULT_DISPLAY_TEXT = "キーを押してね！"
TEXT_COLOR_WHITE = (255, 255, 255)

# フォントサイズ
FONT_SIZE_LARGE = 80
FONT_SIZE_SMALL = 40

# 隠し終了コマンド
EXIT_SECRET = ['q', 'u', 'i', 't']

# ホワイトリスト（反応を許可するキー・文字セット）
ALLOWED_CHARS = set(string.ascii_lowercase + string.digits + string.punctuation + " ")
ALLOWED_KEY_NAMES = {'space', 'enter', 'return'}
