import os
os.environ["SDL_VIDEO_CENTERED"] = "1"

import datetime
import pygame
import sys
import math
import random
from .localization import (
    GAME_SUBTITLES, contains_chinese, get_chinese_font, is_chinese, translate,
)

pygame.init()
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
except pygame.error:
    # The game remains playable on systems without an available audio device.
    pass

# ============================================================
#  Constants (board-size-independent)
# ============================================================
BOARD_PX = 504  # Fixed board pixel width for all sizes

# ============================================================
#  16:9 handheld-style symmetric layout
# ============================================================

WINDOW_W = 1280
WINDOW_H = 720

# 瀹革缚鏅剁粩鏍ф倻閺嶅洭顣介弽?
LEFT_BAR_X = 54
LEFT_BAR_Y = 84
LEFT_BAR_W = 120
LEFT_BAR_H = 552

# 濡娲忛崠鍝勭厵
BOARD_X = 214
BOARD_Y = 108

# 閸欏厖鏅剁粩鏍ф倻閻樿埖鈧焦鐖?
RIGHT_BAR_X = 778
RIGHT_BAR_Y = 84
RIGHT_BAR_W = 448
RIGHT_BAR_H = 592

# 娑撶儤妫禒锝囩垳閸忕厧顔愭穱婵堟殌
MARGIN = 36
UI_HEIGHT = 80

# ============================================================
#  Animation tuning
# ============================================================

# 姒х姵鐖ｉ棃鐘虹箮娴溿倕寮堕悙鐟邦樋鐏忔垵鍎氱槐鐘插敶閿涘奔绱扮憴锕€褰傜壕浣告儧妫板嫯顫?
MAGNET_RADIUS = 28

# 妫板嫯顫嶅Λ瀣摍鐞氼偄鎯涢崥鎴滄唉閸欏鍋ｉ惃鍕偓鐔峰閿涘本鏆熼崐鑹扮Ш婢堆冩儧瀵版绉鸿箛?
MAGNET_PULL = 0.32

# 韫囶偄鎯涢崚棰佹唉閸欏鍋ｉ弮鍓佹畱閹舵牕濮╅懠鍐ㄦ纯
MAGNET_JITTER_RADIUS = 14

# 閽€钘夌摍濞夈垻姹楅幐浣虹敾鐢勬殶
RIPPLE_MAX_FRAMES = 24

# 閼虫粌鍩勬潻鐐靛殠閸斻劎鏁鹃幐浣虹敾鐢勬殶
WIN_LINE_MAX_FRAMES = 45

# 闂堢偞纭堕拃钘夌摍閸欏秹顩幐浣虹敾鐢勬殶
INVALID_MARK_MAX_FRAMES = 24

# 閹梹顥愰崝銊ф暰閹镐胶鐢荤敮褎鏆熼敍?0 FPS 娑撳瀹?0.3 缁?
UNDO_ANIM_MAX_FRAMES = 18

# 閹剙浠犻崷銊ュ嚒閺堝顥愮€涙劒绗傞弮鍓佹畱娑撳秴褰查拃钘夌摍閹绘劗銇氶柅蹇旀鎼?
OCCUPIED_HINT_ALPHA = 95

# 閼虫粌鍩勫Λ瀣摍娓氭繃顐奸梻顏嗗剨閹鎶氶弫?
WIN_STONE_FLASH_MAX_FRAMES = 54

# 濮ｅ繘顣奸懗婊冨焺濡鐡欐笟婵囶偧閻愰€涘瘨閻ㄥ嫰妫块梾鏂挎姎閺?
WIN_STONE_FLASH_STEP = 9

# 缂佹挻娼い鐢告桨閺夊灝鑴婇崙鍝勫З閻㈢粯鈧鎶氶弫?
END_PANEL_POP_FRAMES = 22

# 缂佹挻娼い鍨垼妫版﹢妫悜渚€鈧喎瀹?
END_TITLE_FLASH_SPEED = 6

# Board size options
BOARD_SIZE_CHOICES = [13, 15, 19]
DEFAULT_SIZE = 15

# ============================================================
#  App / Future Game Hub Config
# ============================================================

APP_TITLE = "PIXEL GAMEBOX"

GAME_LIBRARY = [
    {
        "id": "gomoku",
        "name": "GOMOKU",
        "default_board_size": DEFAULT_SIZE,
    }
]

# ============================================================
#  Desktop / Handheld UI Config
# ============================================================

DECK_TITLE = "HAO'S GAME DECK"

# 閹哄本婧€婢舵牗顢?/ 鐏炲繐绠烽崠鍝勭厵
HANDHELD_RECT = pygame.Rect(36, 22, WINDOW_W - 72, WINDOW_H - 44)
DESKTOP_SCREEN_RECT = pygame.Rect(120, 78, WINDOW_W - 240, WINDOW_H - 156)

# 鐏炲繐绠烽崘鍛攽闂堛垹绔风仦鈧?
DESKTOP_STATUS_H = 34
DESKTOP_GRID_TOP_PAD = 70
# 閸ョ偓鐖ｉ崝鐘层亣閿涘苯鑻熸稉鏃囶唨 3 x 2 缂冩垶鐗搁弴鏉戞綆閸栤偓閸︽澘鍨庣敮鍐ㄦ躬濡楀矂娼版稉顓㈡？
DESKTOP_ICON_SIZE = 124
DESKTOP_ICON_GAP_X = 92
DESKTOP_ICON_GAP_Y = 70

# 閻㈢敻鍣烘禒?100% 閹哄鍩?0% 閻ㄥ嫭鈧粯妞傞梹鍖＄窗40 閸掑棝鎸?
BATTERY_DRAIN_MS = 40 * 60 * 1000

# ============================================================
#  Boot / Shutdown Animation Config
# ============================================================

BOOT_TEXT = "WELCOME TO HAO'S GAME DECK"
SHUTDOWN_TEXT = "BYE BYE SEE U NEXT TIME~"

# 瀵偓閺堣櫣鏅棃銏＄瑤娴滎喗妞傞梹?
BOOT_FADE_IN_FRAMES = 42

# 閹垫挸鐡ч崺铏诡攨闂傛挳娈ч敍姘崇殶閹?
BOOT_TYPE_BASE_DELAY = 6

# 閹垫挸鐣€涙鎮楅敍宀€鐓弳鍌氫粻妞ゅ尅绱濋崓蹇撳櫙婢跺洤鎯庨崝?
BOOT_ENTER_PAUSE_FRAMES = 22

# 閸氼垰濮╂潻娑樺閺夆剝鈧粯妞傞梹鍖＄窗10 缁?
BOOT_PROGRESS_TOTAL_FRAMES = 60 * 10
SYSTEM_READY_PULSE_FRAMES = 90

# 閸忚櫕婧€閸掔娀娅庨弬鍥х摟閸╄櫣顢呴梻鎾
SHUTDOWN_DELETE_DELAY = 4

# 閸忚櫕婧€濞撴劙绮﹂弮鍫曟毐
SHUTDOWN_FADE_FRAMES = 60

# ============================================================
#  Snake Game Config
# ============================================================

SNAKE_GRID_COUNT = 24
SNAKE_CELL_SIZE = BOARD_PX // SNAKE_GRID_COUNT
SNAKE_BOARD_PX = SNAKE_GRID_COUNT * SNAKE_CELL_SIZE

SNAKE_X = BOARD_X
SNAKE_Y = BOARD_Y

# 鐠愵亜鎮嗛摂鍥┬╅崝銊┾偓鐔峰閿涙碍鏆熺€涙绉虹亸蹇氱Ш韫?
SNAKE_MOVE_INTERVAL_FRAMES = 8
BREAKOUT_END_POP_FRAMES = 22

# Falling-block game config
TETRIS_COLS = 10
TETRIS_VISIBLE_ROWS = 20
TETRIS_HIDDEN_ROWS = 2
TETRIS_ROWS = TETRIS_VISIBLE_ROWS + TETRIS_HIDDEN_ROWS
TETRIS_CELL = 25
TETRIS_BOARD_W = TETRIS_COLS * TETRIS_CELL
TETRIS_BOARD_H = TETRIS_VISIBLE_ROWS * TETRIS_CELL
TETRIS_BOARD_X = 420
TETRIS_BOARD_Y = 108
TETRIS_END_POP_FRAMES = 22

# 2048 Game Config
G2048_SIZE = 4
G2048_BOARD_PX = BOARD_PX
G2048_X = BOARD_X
G2048_Y = BOARD_Y
G2048_GAP = 10
G2048_CELL = (G2048_BOARD_PX - G2048_GAP * (G2048_SIZE + 1)) // G2048_SIZE
G2048_POP_FRAMES = 14
G2048_MERGE_FRAMES = 16
G2048_SLIDE_FRAMES = 8
G2048_INVALID_SHAKE_FRAMES = 14
G2048_END_POP_FRAMES = 22

# 2048 particle
G2048_PARTICLE_LIFE_MIN = 14
G2048_PARTICLE_LIFE_MAX = 26

# win flash
G2048_WIN_FLASH_FRAMES = 42

# Minesweeper Config
MINES_SIZE_CHOICES = [9, 16]
MINES_COUNT_CHOICES = {9: [10, 15, 20], 16: [40, 50, 60]}
DEFAULT_MINES_SIZE = 9
DEFAULT_MINES_COUNT = 10
MINES_BOARD_PX = BOARD_PX
MINES_X = BOARD_X
MINES_Y = BOARD_Y
MINES_REVEAL_POP_FRAMES = 10
MINES_FLAG_POP_FRAMES = 10
MINES_END_POP_FRAMES = 22
MINES_SHAKE_FRAMES = 16
MINES_FLAG_PARTICLE_COUNT = 8
MINES_EXPLOSION_PARTICLE_COUNT = 36

# death animation
MINES_DEATH_FLASH_FRAMES = 70          # flash buildup
MINES_DEATH_EXPLOSION_FRAMES = 95      # explosion main
MINES_DEATH_REVEAL_DELAY = 45          # pause after reveal
MINES_DEATH_FADE_FRAMES = 38           # black fade to end screen

# explosion particle counts
MINES_BIG_EXPLOSION_PARTICLES = 140
MINES_RING_EXPLOSION_PARTICLES = 72
MINES_EMBER_PARTICLES = 90

# hint
MINES_HINT_FLASH_FRAMES = 90
MINES_HINT_BUTTON_COOLDOWN = 30

PASSWORD_MAX_LENGTH = 4
PASSWORD_TARGET = ["0", "4", "2", "5"]
PASSWORD_ERROR_SHAKE_FRAMES = 30
PASSWORD_ERROR_FLASH_INTERVAL = 6


def get_cell_size(board_count):
    return BOARD_PX // (board_count - 1)


def get_star_points(board_count):
    if board_count == 19:
        pts = [3, 9, 15]
    elif board_count == 15:
        pts = [3, 7, 11]
    else:
        pts = [3, 6, 9]
    return [(r, c) for r in pts for c in pts]


# ============================================================
#  Warm vintage pixel palette
# ============================================================
class C:
    BG = (245, 225, 190)
    BOARD = (139, 90, 43)
    BOARD_EDGE = (101, 67, 33)
    GRID = (55, 33, 16)
    GRID_THICK = (35, 20, 10)
    OUTLINE = (18, 10, 5)
    GOLD = (218, 165, 32)
    GOLD_LIGHT = (245, 210, 80)
    GOLD_DARK = (170, 120, 20)
    RED = (185, 55, 55)
    RED_LIGHT = (225, 105, 105)
    CREAM = (255, 242, 215)
    CREAM_DARK = (230, 215, 180)
    TEXT = (38, 20, 10)
    TEXT_LIGHT = (245, 230, 200)
    STAR = (50, 30, 15)
    BLACK_STONE = (22, 14, 8)
    BLACK_HL = (70, 42, 25)
    BLACK_SH = (10, 6, 3)
    WHITE_STONE = (240, 228, 190)
    WHITE_HL = (255, 250, 235)
    WHITE_SH = (190, 170, 130)
    MENU_BG = (35, 18, 8)
    MENU_PANEL = (55, 30, 15)
    BTN_NORMAL = (245, 235, 200)
    BTN_HOVER = (255, 245, 220)
    BTN_SELECT = (218, 165, 32)
    BTN_BORDER = (30, 15, 5)

    # Desktop-only palette閿涙艾鎷版禍鏂跨摍濡灏崚鍡礉娴ｅ棔绮涙穱婵囧瘮婢跺秴褰滈崓蹇曠妞?
    DESK_BG_TOP = (24, 32, 46)
    DESK_BG_BOTTOM = (55, 28, 52)
    DESK_PANEL = (30, 38, 58)
    DESK_PANEL_DARK = (18, 22, 34)
    DESK_ACCENT = (95, 170, 185)
    DESK_ACCENT_LIGHT = (140, 220, 220)
    DESK_ICON = (70, 78, 120)
    DESK_ICON_HOVER = (92, 105, 160)
    DESK_ICON_SOON = (58, 54, 74)
    DESK_TEXT = (235, 240, 230)
    DESK_MUTED = (150, 160, 170)

    # Snake-only palette閿涙岸娼氱紒?/ 缁鳖偊绮﹂敍灞芥嫲 GOMOKU 閻ㄥ嫭顥氶柌鎴ｅ閸栧搫鍨?
    SNAKE_BG = (12, 28, 30)
    SNAKE_PANEL = (18, 48, 48)
    SNAKE_PANEL_DARK = (8, 20, 22)
    SNAKE_GRID = (28, 72, 70)
    SNAKE_GRID_DARK = (14, 42, 42)
    SNAKE_BODY = (70, 220, 145)
    SNAKE_HEAD = (120, 255, 180)
    SNAKE_SHADOW = (30, 120, 90)
    SNAKE_FOOD = (255, 95, 120)
    SNAKE_FOOD_LIGHT = (255, 170, 180)
    SNAKE_TEXT = (220, 255, 235)
    SNAKE_ACCENT = (80, 210, 210)
    SNAKE_ACCENT_LIGHT = (150, 255, 240)

    # Breakout palette
    BG_DEEP_BLUE = (8, 16, 32)
    BRICK_PURPLE = (130, 60, 180)
    BRICK_ORANGE = (220, 140, 40)
    BREAKOUT_PANEL = (18, 28, 48)
    YELLOW = (255, 220, 40)

    BREAKOUT_BG = (12, 16, 34)
    BREAKOUT_PANEL_DARK = (14, 13, 30)
    BREAKOUT_ACCENT = (245, 135, 70)
    BREAKOUT_ACCENT_LIGHT = (255, 195, 95)
    BREAKOUT_TEXT = (245, 235, 215)
    BREAKOUT_MUTED = (170, 150, 190)
    BREAKOUT_BALL_YELLOW = (255, 225, 90)
    BREAKOUT_BALL_CYAN = (115, 230, 255)
    BREAKOUT_BALL_PINK = (255, 130, 180)
    BREAKOUT_BRICK_PURPLE = (135, 95, 220)
    BREAKOUT_BRICK_ORANGE = (235, 120, 55)
    BREAKOUT_BRICK_BLUE = (80, 150, 230)
    BREAKOUT_PADDLE_ORANGE = (245, 145, 65)
    BREAKOUT_PADDLE_CYAN = (90, 220, 220)
    BREAKOUT_PADDLE_PINK = (255, 125, 175)

    # 2048 palette: cream/orange/brick red
    G2048_BG = (42, 25, 18)
    G2048_PANEL = (82, 48, 30)
    G2048_PANEL_DARK = (50, 30, 22)
    G2048_ACCENT = (235, 135, 58)
    G2048_ACCENT_LIGHT = (255, 205, 110)
    G2048_TEXT = (255, 241, 210)
    G2048_MUTED = (190, 150, 115)
    G2048_BOARD = (120, 76, 48)
    G2048_CELL_EMPTY = (70, 45, 34)
    G2048_TILE_2 = (238, 220, 185)
    G2048_TILE_4 = (240, 205, 145)
    G2048_TILE_8 = (238, 165, 85)
    G2048_TILE_16 = (230, 120, 70)
    G2048_TILE_32 = (210, 85, 60)
    G2048_TILE_64 = (180, 60, 50)
    G2048_TILE_128 = (235, 185, 75)
    G2048_TILE_256 = (230, 160, 55)
    G2048_TILE_512 = (215, 125, 45)
    G2048_TILE_1024 = (190, 90, 45)
    G2048_TILE_2048 = (150, 55, 38)

    # Minesweeper palette: dark green / sand / warning red
    MINES_BG = (18, 30, 24)
    MINES_PANEL = (34, 58, 44)
    MINES_PANEL_DARK = (18, 34, 28)
    MINES_ACCENT = (210, 170, 90)
    MINES_ACCENT_LIGHT = (245, 215, 130)
    MINES_TEXT = (240, 235, 200)
    MINES_MUTED = (145, 160, 130)
    MINES_BOARD = (58, 82, 58)
    MINES_CELL_CLOSED = (82, 112, 78)
    MINES_CELL_OPEN = (190, 178, 130)
    MINES_CELL_HOVER = (105, 140, 95)
    MINES_FLAG = (220, 70, 60)
    MINES_MINE = (25, 18, 15)
    MINES_MINE_RED = (210, 55, 45)

    # Falling-block palette: warm brass, coral, cream and dark cocoa
    TETRIS_BG = (34, 18, 24)
    TETRIS_PANEL = (82, 45, 42)
    TETRIS_PANEL_DARK = (38, 22, 28)
    TETRIS_BOARD = (24, 16, 22)
    TETRIS_GRID = (68, 42, 48)
    TETRIS_ACCENT = (224, 142, 62)
    TETRIS_ACCENT_LIGHT = (255, 210, 124)
    TETRIS_TEXT = (255, 238, 205)
    TETRIS_MUTED = (180, 136, 124)
    TETRIS_GHOST = (118, 82, 76)
    TETRIS_I = (90, 200, 190)
    TETRIS_O = (244, 190, 70)
    TETRIS_T = (190, 105, 150)
    TETRIS_S = (112, 184, 105)
    TETRIS_Z = (218, 86, 78)
    TETRIS_J = (92, 126, 190)
    TETRIS_L = (232, 126, 62)

    PASSWORD_BG = (14, 18, 30)
    PASSWORD_PANEL = (24, 30, 52)
    PASSWORD_DIGIT = (140, 220, 220)
    PASSWORD_DIGIT_ERROR = (235, 70, 70)
    PASSWORD_BTN = (48, 58, 98)
    PASSWORD_BTN_HOVER = (68, 82, 140)
    PASSWORD_BTN_BORDER = (95, 170, 185)
    PASSWORD_ERROR_TEXT = (235, 70, 70)
    PASSWORD_SUCCESS_TEXT = (140, 220, 220)


# ============================================================
#  Helper Functions
# ============================================================
def create_pixel_stone(base_color, highlight, shadow, size):
    """Draw a pixel-art circle onto a small surface."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = (size - 1) / 2.0
    radius = size / 2.0 - 0.3
    for y in range(size):
        for x in range(size):
            d = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if d <= radius:
                if x < size // 4 and y < size // 4:
                    c = highlight
                elif x > 3 * size // 4 and y > 3 * size // 4:
                    c = shadow
                elif d <= radius * 0.35:
                    c = highlight if (x + y) % 2 == 0 else base_color
                elif d > radius * 0.7:
                    c = shadow if (x + y) % 2 == 0 else base_color
                else:
                    c = base_color
                surf.set_at((x, y), c)
    return surf


def create_wood_texture(w, h):
    """Generate a wood-grain texture surface."""
    surf = pygame.Surface((w, h))
    surf.fill(C.BOARD)
    rng = random.Random(42)
    for _ in range(400):
        x, y = rng.randint(0, w - 1), rng.randint(0, h - 1)
        shade = rng.randint(-18, 18)
        c = (max(0, min(255, C.BOARD[0] + shade)),
             max(0, min(255, C.BOARD[1] + shade)),
             max(0, min(255, C.BOARD[2] + shade)))
        for i in range(rng.randint(2, 8)):
            if x + i < w:
                surf.set_at((x + i, y), c)
    for _ in range(60):
        y = rng.randint(0, h - 1)
        x = rng.randint(0, w - 40)
        length = rng.randint(20, 80)
        shade = rng.randint(-10, 10)
        c = (max(0, min(255, C.BOARD[0] + shade)),
             max(0, min(255, C.BOARD[1] + shade)),
             max(0, min(255, C.BOARD[2] + shade)))
        for i in range(length):
            px, py = x + i, y + rng.randint(-1, 1)
            if 3 <= px < w - 3 and 0 <= py < h:
                surf.set_at((px, py), c)
    return surf


def draw_decorative_border(surf, rect, color, thickness):
    """Thick pixel-art border with cuphead-style corner squares."""
    x, y, w, h = rect
    pygame.draw.rect(surf, color, (x, y, w, h), thickness)
    sq = thickness * 3
    for cx, cy in [(x, y), (x + w - sq, y), (x, y + h - sq), (x + w - sq, y + h - sq)]:
        pygame.draw.rect(surf, color, (cx, cy, sq, sq))
        inner = thickness + 1
        pygame.draw.rect(surf, C.GOLD, (cx + inner, cy + inner, sq - inner * 2, sq - inner * 2))


def render_pixel_text(font, text, color, scale=2):
    """Render text small then scale up for pixel look."""
    text = translate(str(text))
    render_font = get_chinese_font(12) if contains_chinese(text) else font
    small = render_font.render(text, False if contains_chinese(text) else True, color)
    w, h = small.get_width() * scale, small.get_height() * scale
    return pygame.transform.scale(small, (w, h))


def ease_out_back(t):
    """Ease-out-back easing for pop animations."""
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def render_vertical_pixel_text(font, text, color, scale=2, gap=6):
    """Render text vertically, one character per row."""
    chars = []

    for ch in text:
        if ch == " ":
            spacer = pygame.Surface((1, 12 * scale), pygame.SRCALPHA)
            chars.append(spacer)
        else:
            chars.append(render_pixel_text(font, ch, color, scale=scale))

    if not chars:
        return pygame.Surface((1, 1), pygame.SRCALPHA)

    w = max(ch.get_width() for ch in chars)
    h = sum(ch.get_height() for ch in chars) + gap * (len(chars) - 1)

    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    y = 0
    for ch_surf in chars:
        x = (w - ch_surf.get_width()) // 2
        surf.blit(ch_surf, (x, y))
        y += ch_surf.get_height() + gap

    return surf


def draw_restrained_meteors(surf, rect, tick, max_meteors=2, alpha_scale=1.0):
    """Draw meteor traces as timed twinkling star dots, not moving sprites."""
    max_meteors = max(0, min(2, int(max_meteors)))
    if max_meteors == 0 or rect.width <= 0 or rect.height <= 0:
        return

    paths = [
        ((1.05, 0.10), (0.72, 0.20), (0.44, 0.31)),
        ((0.92, 0.08), (0.60, 0.19), (0.26, 0.36)),
        ((1.08, 0.24), (0.80, 0.32), (0.50, 0.48)),
        ((0.78, 0.04), (0.52, 0.16), (0.20, 0.26)),
        ((1.02, 0.42), (0.75, 0.50), (0.48, 0.64)),
        ((0.88, 0.34), (0.62, 0.43), (0.30, 0.58)),
        ((1.10, 0.58), (0.76, 0.63), (0.42, 0.78)),
        ((0.70, 0.18), (0.45, 0.28), (0.18, 0.42)),
        ((1.04, 0.15), (0.86, 0.28), (0.66, 0.40)),
        ((0.62, 0.07), (0.38, 0.17), (0.14, 0.29)),
        ((1.06, 0.32), (0.88, 0.43), (0.70, 0.55)),
        ((0.98, 0.50), (0.70, 0.58), (0.36, 0.72)),
        ((0.84, 0.13), (0.56, 0.26), (0.32, 0.41)),
        ((1.12, 0.05), (0.92, 0.14), (0.74, 0.26)),
        ((0.76, 0.46), (0.50, 0.55), (0.24, 0.68)),
        ((1.02, 0.68), (0.78, 0.72), (0.54, 0.84)),
    ]
    schedules = [
        {"cycle": 430, "offset": 17, "active": 156, "seed": 3},
        {"cycle": 590, "offset": 113, "active": 174, "seed": 11},
    ]

    overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
    strength_scale = max(0.0, min(1.0, alpha_scale))

    def bezier(path, t):
        (x0, y0), (x1, y1), (x2, y2) = path
        inv = 1.0 - t
        x = inv * inv * x0 + 2 * inv * t * x1 + t * t * x2
        y = inv * inv * y0 + 2 * inv * t * y1 + t * t * y2
        return int(rect.width * x), int(rect.height * y)

    def bezier_direction(path, t):
        (x0, y0), (x1, y1), (x2, y2) = path
        dx = 2 * (1.0 - t) * (x1 - x0) + 2 * t * (x2 - x1)
        dy = 2 * (1.0 - t) * (y1 - y0) + 2 * t * (y2 - y1)
        dx *= rect.width
        dy *= rect.height
        length = max(1.0, math.hypot(dx, dy))
        return dx / length, dy / length

    def draw_trace_dot(x, y, alpha, size=3):
        if alpha <= 0:
            return
        pygame.draw.rect(overlay, (*C.DESK_ACCENT, min(90, alpha // 2)), (x - 3, y - 3, size + 6, size + 6))
        pygame.draw.rect(overlay, (*C.DESK_ACCENT_LIGHT, alpha), (x, y, size, size))
        if alpha > 105:
            shine = max(1, size - 2)
            pygame.draw.rect(overlay, (*C.DESK_TEXT, min(255, alpha + 65)), (x + 1, y + 1, shine, shine))

    for lane, schedule in enumerate(schedules[:max_meteors]):
        cycle = schedule["cycle"]
        event_tick = tick + schedule["offset"]
        cycle_index = event_tick // cycle
        frame = event_tick % cycle
        if frame >= schedule["active"]:
            continue

        path_index = (cycle_index * 7 + schedule["seed"]) % len(paths)
        path = paths[path_index]
        head = frame / max(1, schedule["active"] - 1)
        dots = 30
        tail = 16

        for index in range(dots):
            dot_t = index / (dots - 1)
            age = head * (dots + tail) - index
            if age < 0 or age > tail:
                continue
            fade = math.sin(min(1.0, max(0.0, head)) * math.pi)
            tail_fade = (1.0 - age / tail) ** 1.18
            alpha = int(360 * strength_scale * fade * tail_fade)
            if alpha <= 10:
                continue

            x, y = bezier(path, dot_t)
            flicker = 0.82 + 0.18 * math.sin(tick * 0.42 + index * 1.7 + lane)
            draw_trace_dot(x, y, min(255, int(alpha * flicker)), size=4 if age < 1.2 else 3)

            if age > 1.0:
                scatter_life = min(1.0, (age - 1.0) / max(1.0, tail - 1.0))
                scatter_alpha = int(alpha * (1.0 - scatter_life * 0.72) * 0.82)
                if scatter_alpha > 8:
                    dir_x, dir_y = bezier_direction(path, dot_t)
                    norm_x, norm_y = -dir_y, dir_x
                    for p in range(5):
                        side = -1 if (index + p + path_index) % 2 == 0 else 1
                        spread = (5 + p * 4) * (0.35 + scatter_life * 1.55)
                        lag = (3 + p * 2) * scatter_life
                        jitter_x = ((index * 7 + p * 5 + path_index) % 5) - 2
                        jitter_y = ((index * 3 + p * 7 + path_index) % 5) - 2
                        sx = int(x + norm_x * side * spread - dir_x * lag + jitter_x)
                        sy = int(y + norm_y * side * spread - dir_y * lag + jitter_y)
                        particle_size = 2 if p < 3 and scatter_life < 0.75 else 1
                        pygame.draw.rect(
                            overlay,
                            (*C.DESK_ACCENT_LIGHT, min(235, scatter_alpha)),
                            (sx, sy, particle_size, particle_size),
                        )

    surf.blit(overlay, rect.topleft)

# ============================================================
#  Particle (win celebration sparkles)
# ============================================================
class Particle:
    def __init__(self, x, y, color, vx, vy, life):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.12  # gravity
        self.life -= 1
        return self.life > 0

    def draw(self, surf, shake_x=0, shake_y=0):
        alpha = max(0, int(255 * self.life / self.max_life))
        size = max(1, int(3 * self.life / self.max_life))
        px, py = int(self.x + shake_x), int(self.y + shake_y)
        if 0 <= px < WINDOW_W and 0 <= py < WINDOW_H:
            rect = (px - size // 2, py - size // 2, size, size)
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            s.fill((*self.color, alpha))
            surf.blit(s, rect)


# ============================================================
#  Board Logic
# ============================================================
class Board:
    def __init__(self, board_count):
        self.board_count = board_count
        self.grid = [[0] * board_count for _ in range(board_count)]
        self.current_player = 1  # 1=Black, 2=White
        self.winner = 0          # 0=none, 1/2=winner, -1=draw
        self.win_stones = []
        self.last_move = None
        self.move_history = []
        self.move_count = 0

    @property
    def cell_size(self):
        return get_cell_size(self.board_count)

    @property
    def stone_size(self):
        return self.cell_size - 4

    @property
    def star_points(self):
        return get_star_points(self.board_count)

    def place_stone(self, row, col):
        if not (0 <= row < self.board_count and 0 <= col < self.board_count):
            return False
        if self.grid[row][col] != 0 or self.winner != 0:
            return False
        self.grid[row][col] = self.current_player
        self.move_history.append((row, col, self.current_player))
        self.last_move = (row, col)
        self.move_count += 1
        if self._check_win(row, col):
            self.winner = self.current_player
        elif self.move_count >= self.board_count * self.board_count:
            self.winner = -1
        else:
            self.current_player = 3 - self.current_player
        return True

    def undo(self):
        """Undo the last move. Returns True if successful."""
        if not self.move_history:
            return False
        row, col, player = self.move_history.pop()
        self.grid[row][col] = 0
        self.move_count -= 1
        self.winner = 0
        self.win_stones = []
        if self.move_history:
            self.last_move = (self.move_history[-1][0], self.move_history[-1][1])
        else:
            self.last_move = None
        self.current_player = player
        return True

    def _check_win(self, row, col):
        player = self.grid[row][col]
        dirs = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in dirs:
            stones = [(row, col)]
            for d in [1, -1]:
                for i in range(1, 5):
                    r = row + dr * i * d
                    c = col + dc * i * d
                    if (0 <= r < self.board_count and 0 <= c < self.board_count
                            and self.grid[r][c] == player):
                        stones.append((r, c))
            if len(stones) >= 5:
                self.win_stones = stones
                return True
        return False

    def reset(self):
        self.__init__(self.board_count)

    def is_empty(self, r, c):
        if 0 <= r < self.board_count and 0 <= c < self.board_count:
            return self.grid[r][c] == 0
        return False

    def has_moves(self):
        return self.move_count > 0


# ============================================================
#  Game
# ============================================================







