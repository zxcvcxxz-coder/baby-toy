"""
アプリケーションの設定値、パス定数、および定数定義
"""
import string
from pathlib import Path

# パス設定（絶対パス基準）
SRC_DIR = Path(__file__).resolve().parent
BASE_DIR = SRC_DIR.parent
ASSETS_DIR = BASE_DIR / "assets"
SE_DIR = ASSETS_DIR / "se"
VID_DIR = ASSETS_DIR / "vid"
IMAGE_DIR = ASSETS_DIR / "Image"

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
EXIT_SECRETS = ['mamadaisuki', 'ilovemother', '20251102']

# ホワイトリスト（反応を許可するキー・文字セット）
ALLOWED_CHARS = set(string.ascii_lowercase + string.digits + string.punctuation + " ")
ALLOWED_KEY_NAMES = {'space', 'enter', 'return'}

# 特定キーとメディア（assets/se, assets/vid）の紐付け設定
KEY_MEDIA_MAP = {
    'c': ('se', 'cat01.mp3'),
    'd': ('se', 'dog.mp3'),
    'e': ('se', 'elephant.mp3'),
    'g': ('vid', 'Cute-ghost01.mp4'),
    't': ('se', 'train.mp3'),
    'p': ('se', 'phone.mp3'),
    'r': ('se', 'robot01.mp3'),
    'w': ('se', 'wolf.mp3'),
    's': ('se', 'seagull.mp3'),
    'h': ('se', 'helicopter.mp3'),
    'm': ('se', 'camera.mp3'),
}

# 動画ウィンドウ表示設定（3回り大きく拡大）
VIDEO_WINDOW_WIDTH = 480   # 240 -> 480 に拡大
VIDEO_WINDOW_HEIGHT = 320  # 160 -> 320 に拡大
VIDEO_WINDOW_POSITION = "bottom_right"
MAX_VIDEO_WINDOWS = 3      # 同時再生数を減らして負荷軽減
VIDEO_FRAME_SKIP = 2       # N フレームごとに1枚だけデコード（大きいほど軽い）

# 画像スクロール設定
# 押すとランダムな画像がランダムな方向から流れてくるキー
IMAGE_SCROLL_KEYS = {'f', 'j', 'k', 'n'}
IMAGE_SCROLL_SPEED = 10          # 1フレームあたりの移動ピクセル数
IMAGE_SCROLL_SIZE = 200          # 画像の表示サイズ (短辺基準 px)
IMAGE_SCROLL_DIRECTIONS = ['left', 'right', 'up', 'down']  # ランダム抽選対象

# キーログ表示設定（左上の薄い文字蓄積）
KEY_LOG_MAX_CHARS = 100          # 特大文字用に適切な最大蓄積数
KEY_LOG_FONT_SIZE = 140          # キーログの文字サイズ（特大サイズ）
KEY_LOG_COLOR = (220, 220, 220)  # キーログの文字色
KEY_LOG_ALPHA = 50               # 透明度 (0=透明, 255=不透明)
KEY_LOG_MARGIN = 20              # 画面端からの余白 px
KEY_LOG_LINE_WIDTH = 12          # 1行あたりの文字数（折り返し）
