"""MERIDIAN worldview data and game-world registration API.

Register a new game world with one call::

    register_game_world("pacman", ...)

Built-in worlds are auto-registered at module import.
"""

from .lore_expansions import ARCHIVE_EXPANSIONS

# ============================================================
#  World Registry
# ============================================================

_world_registry = {}          # game_id -> world data dict
_device_lore_entries = []     # device-level lore (not tied to any game)
_lore_by_id = {}              # id -> entry dict for fast lookup


def register_game_world(game_id, *, world_name_en, world_name_zh,
                        world_summary_en, world_summary_zh,
                        prologue_en, prologue_zh,
                        menu_flavor_en, menu_flavor_zh,
                        lore_entries=None, desktop_subtitle_en=None,
                        desktop_subtitle_zh=None):
    """Register a game world in the MERIDIAN system.

    Required:
        game_id            Unique identifier (e.g. "pacman")
        world_name_en/zh   World display name
        world_summary_en/zh  One-line world concept
        prologue_en/zh     List of strings — first-visit prologue lines
        menu_flavor_en/zh  Single string — menu-page flavor text

    Optional:
        lore_entries       List of deeper lore entry dicts:
            {"id": str, "title_en": str, "title_zh": str,
             "content_en": [str, ...], "content_zh": [str, ...],
             "unlock": "always" | "stat:game:key:threshold" |
                       "achievement:id" | "completion:threshold"}
        desktop_subtitle_en/zh  Override the default desktop subtitle
    """
    if game_id in _world_registry:
        raise ValueError(f"Duplicate game world: {game_id}")
    pending_entries = list(lore_entries or [])
    pending_ids = set()
    for entry in pending_entries:
        entry_id = entry.get("id") if isinstance(entry, dict) else None
        if not entry_id:
            raise ValueError(f"Lore entry for {game_id} requires a non-empty id")
        if entry_id in pending_ids or entry_id in _lore_by_id:
            raise ValueError(f"Duplicate lore entry id: {entry_id}")
        pending_ids.add(entry_id)

    world_data = {
        "game_id": game_id,
        "world_name_en": world_name_en,
        "world_name_zh": world_name_zh,
        "world_summary_en": world_summary_en,
        "world_summary_zh": world_summary_zh,
        "prologue_en": list(prologue_en),
        "prologue_zh": list(prologue_zh),
        "menu_flavor_en": menu_flavor_en,
        "menu_flavor_zh": menu_flavor_zh,
        "desktop_subtitle_en": desktop_subtitle_en or world_name_en,
        "desktop_subtitle_zh": desktop_subtitle_zh or world_name_zh,
        "lore_entries": [],
    }
    if pending_entries:
        for entry in pending_entries:
            full_entry = dict(entry)
            full_entry.setdefault("game_id", game_id)
            full_entry.setdefault("unlock", "always")
            world_data["lore_entries"].append(full_entry)
            _lore_by_id[entry["id"]] = full_entry
    _world_registry[game_id] = world_data


def register_device_lore(entry_id, *, title_en, title_zh,
                         content_en, content_zh, unlock="always"):
    """Register a device-level lore entry (not tied to any game)."""
    if not entry_id:
        raise ValueError("Device Lore entry requires a non-empty id")
    if entry_id in _lore_by_id:
        raise ValueError(f"Duplicate lore entry id: {entry_id}")
    entry = {
        "id": entry_id,
        "game_id": "__device__",
        "title_en": title_en,
        "title_zh": title_zh,
        "content_en": list(content_en),
        "content_zh": list(content_zh),
        "unlock": unlock,
    }
    _device_lore_entries.append(entry)
    _lore_by_id[entry_id] = entry


def get_world(game_id):
    """Return world data for a registered game, or None."""
    return _world_registry.get(game_id)


def get_all_worlds():
    """Return list of all registered game worlds."""
    return list(_world_registry.values())


def get_device_lore():
    """Return list of device lore entries."""
    return list(_device_lore_entries)


def get_lore_entry(entry_id):
    """Return a single lore entry by id, or None."""
    return _lore_by_id.get(entry_id)


def get_all_lore_entries():
    """Return all lore entries (device + all games)."""
    result = list(_device_lore_entries)
    for world in _world_registry.values():
        result.extend(world["lore_entries"])
    return result


def register_lore_entry(game_id, entry_id, *, title_en, title_zh,
                        content_en, content_zh, unlock="always"):
    """Append a lore entry to an already-registered game world.

    Use this to add extra lore entries after the initial register_game_world() call.
    """
    world = _world_registry.get(game_id)
    if world is None:
        raise ValueError(f"Unknown game_id: {game_id}")
    if not entry_id:
        raise ValueError("Lore entry requires a non-empty id")
    if entry_id in _lore_by_id:
        raise ValueError(f"Duplicate lore entry id: {entry_id}")
    entry = {
        "id": entry_id,
        "game_id": game_id,
        "title_en": title_en,
        "title_zh": title_zh,
        "content_en": list(content_en),
        "content_zh": list(content_zh),
        "unlock": unlock,
    }
    world["lore_entries"].append(entry)
    _lore_by_id[entry_id] = entry


# ============================================================
#  Device Lore — MERIDIAN itself
# ============================================================

register_device_lore(
    "meridian_origin",
    title_en="The Device",
    title_zh="器物起源",
    content_en=[
        "MERIDIAN was found in a sealed vault beneath the old city, "
        "untouched by time. No maker's mark. No power source visible. "
        "Yet it hums.",
        "Its screen is not a screen. Scholars call it a 'resonance lens' "
        "— a window that gazes into worlds not our own.",
        "Fragments of many realities are trapped within. Each game module "
        "is not a program but a stable portal into one of these worlds.",
    ],
    content_zh=[
        "MERIDIAN 被发现于旧城地下的一座密封地窖中，"
        "岁月未能触碰它分毫。没有制造者的印记，没有可见的能源，"
        "但它却在低鸣。",
        "它的屏幕并非屏幕。学者们称其为「共鸣透镜」——"
        "一面凝视异界的窗口。",
        "来自诸界的现实碎片被封存在其中。每一个游戏模块都不是程序，"
        "而是通向其中一个世界的稳定门户。",
    ],
    unlock="always",
)

register_device_lore(
    "meridian_nexus",
    title_en="The Nexus Link",
    title_zh="连接之核",
    content_en=[
        "At the heart of MERIDIAN lies a crystal that pulses in "
        "rhythms no instrument can measure. This is the Nexus — "
        "the anchor that holds its known worlds in equilibrium.",
        "When the device boots, it is not loading software. It is "
        "calibrating resonance. Each 'game' you play is a negotiation "
        "with the physics of another universe.",
        "Should the Nexus ever fail, the linked worlds would drift "
        "apart — or collapse into one another.",
    ],
    content_zh=[
        "MERIDIAN 的核心是一颗以任何仪器都无法测量的节奏脉动的晶体。"
        "这就是「连接之核」——维持已知诸界平衡的锚点。",
        "设备启动时，并非在加载软件，而是在校准共鸣频率。"
        "你玩的每一个「游戏」，都是在与另一个宇宙的物理法则进行交涉。",
        "如果连接之核失效，相连的诸界将会漂移离散——"
        "或者彼此坍缩为一。",
    ],
    unlock="stat:global:launches:5",
)

register_device_lore(
    "meridian_keeper",
    title_en="The Keeper",
    title_zh="持器者",
    content_en=[
        "MERIDIAN does not work for everyone. Most people see "
        "only a blank screen. It chooses its keeper.",
        "No one knows the criteria. Some say it responds to those "
        "who have stood at the boundary between worlds — dreamers, "
        "artists, the lost.",
        "If you are reading this, it has already chosen you.",
    ],
    content_zh=[
        "MERIDIAN 并非对每个人都有效。大多数人只能看到一片空白的屏幕。"
        "它会选择自己的持有者。",
        "没人知道选择的标准。有人说它会回应那些曾站在世界边界的人——"
        "梦想家、艺术家、迷茫者。",
        "如果你正在阅读这段话，它已经选择了你。",
    ],
    unlock="stat:global:launches:10",
)

# ============================================================
#  Built-in Game Worlds
# ============================================================

# --- GOMOKU: 阴阳棋境 (YIN-YANG BOARD) ---

register_game_world(
    "gomoku",
    world_name_en="YIN-YANG BOARD",
    world_name_zh="阴阳棋境",
    world_summary_en="Two ancient gods decide the fate of universes "
                     "through a game of black and white stones.",
    world_summary_zh="两位古神以黑白棋子推演宇宙命运，每一局对弈决定一个纪元的兴衰。",
    prologue_en=[
        "Before time began, two beings stood on opposite sides of the void.",
        "One spoke for chaos — black stones. One spoke for order — white stones.",
        "They agreed: every universe would be decided by a single match.",
        "This board remembers every move they ever made. Play carefully.",
    ],
    prologue_zh=[
        "时间尚未诞生之时，两位存在立于虚空两端。",
        "一位代言混沌——执黑子。一位代言秩序——执白子。",
        "他们约定：每一个宇宙的命运，将由一局棋来决定。",
        "这方棋盘铭记着他们落下的每一手。请慎重落子。",
    ],
    menu_flavor_en="Black and white — chaos and order dance on a grid of fate.",
    menu_flavor_zh="黑白交错，阴阳对弈——命运的网格上，混沌与秩序共舞。",
    desktop_subtitle_en="TACTICAL BOARD",
    desktop_subtitle_zh="战术棋盘",
    lore_entries=[
        {
            "id": "gomoku_first_god",
            "title_en": "The Two Players",
            "title_zh": "两位对弈者",
            "content_en": [
                "They have no names. In the oldest scrolls they are "
                "simply called 'The First' and 'The Second' — though "
                "no one can agree which is which.",
                "Every stone placed echoes across a thousand realities. "
                "A black stone on this board may be the birth of a star "
                "in another universe; a white stone, its death.",
                "Some say the game has been going on since before the "
                "concept of 'going on' existed. Others say it has "
                "always been your turn.",
            ],
            "content_zh": [
                "他们没有名字。在最古老的卷轴中，他们仅被称为「先手」和「后手」——"
                "尽管没人能就谁是谁达成一致。",
                "每一颗落下的棋子都在一千个现实中激起回响。"
                "棋盘上的一枚黑子，可能是另一个宇宙中一颗恒星的诞生；"
                "一枚白子，则是它的消逝。",
                "有人说这局棋在「进行」这个概念诞生之前就已经在进行。"
                "也有人说——一直都是你的回合。",
            ],
            "unlock": "stat:gomoku:wins:10",
        },
    ],
)

# --- SNAKE: 噬码渊 (CODE ABYSS) ---

register_game_world(
    "snake",
    world_name_en="CODE ABYSS",
    world_name_zh="噬码渊",
    world_summary_en="In the digital abyss, a serpent devours data fragments "
                     "— each bite rewrites the world's source code.",
    world_summary_zh="数字深渊底层的灵蛇，以吞噬数据碎片为生——"
                     "每吞下一段代码，世界就被重写一次。",
    prologue_en=[
        "Deep below the surface layer of reality, there is a realm "
        "made of pure information. Streams of raw code flow like rivers.",
        "A serpent lives here. It has no name — only hunger. Each "
        "fragment it consumes becomes part of its endless body.",
        "But every bite changes something. The world you see above "
        "is the serpent's last meal. Are you ready for the next?",
    ],
    prologue_zh=[
        "现实表层之下的深处，有一个由纯粹信息构成的领域。"
        "原始代码如同河流般涌动。",
        "一条灵蛇栖息于此。它没有名字——只有饥饿。"
        "每吞下一块碎片，它无垠的身躯便延长一分。",
        "但每一次吞噬都会改变些什么。你在地面上看到的世界，"
        "是灵蛇的上一顿美餐。准备好面对下一次了吗？",
    ],
    menu_flavor_en="In the abyss of code, hunger is the only law.",
    menu_flavor_zh="代码深渊中，饥饿是唯一的法则。",
    desktop_subtitle_en="RETRO ARCADE",
    desktop_subtitle_zh="复古街机",
    lore_entries=[
        {
            "id": "snake_ouroboros",
            "title_en": "The Ouroboros Protocol",
            "title_zh": "衔尾协议",
            "content_en": [
                "When the serpent grows long enough, it will eventually "
                "bite its own tail. This is not an accident — it is "
                "the Ouroboros Protocol, built into the abyss itself.",
                "Each cycle of self-consumption resets the world. "
                "Every time you press 'Start', a universe is born, "
                "lives, and dies in the serpent's coils.",
                "The question is not whether the serpent will bite "
                "itself — but whether you can guide it to grow "
                "further than it ever has before.",
            ],
            "content_zh": [
                "当灵蛇长到足够长时，它终将咬住自己的尾巴。"
                "这不是意外——这是深渊本身内置的「衔尾协议」。",
                "每一次自我吞噬的循环都会重置世界。"
                "每当你按下「开始」，一个宇宙便在灵蛇的盘绕中诞生、存活、消逝。",
                "问题不在于灵蛇是否会咬住自己——"
                "而在于你能否引导它长得比以往任何时候都更长。",
            ],
            "unlock": "stat:snake:best_score:40",
        },
    ],
)

# --- BREAKOUT: 星穹壁垒 (STAR FORTRESS) ---

register_game_world(
    "breakout",
    world_name_en="STAR FORTRESS",
    world_name_zh="星穹壁垒",
    world_summary_en="A lost spacefaring civilization left behind energy "
                     "fortresses — the bouncing sphere is a trapped star fragment.",
    world_summary_zh="失落的太空文明留下的能量壁垒，"
                     "反弹的球体是一颗被囚禁的恒星碎片。",
    prologue_en=[
        "They called themselves the Architects. They built cities "
        "inside stars and wove energy into solid walls.",
        "Then they vanished. All that remains are their fortresses "
        "— still humming, still guarding nothing.",
        "A fragment of their last star is trapped inside, bouncing "
        "endlessly between walls that will never yield. Unless you help it.",
    ],
    prologue_zh=[
        "他们称自己为「筑星者」。他们在恒星内部建造城市，"
        "将能量编织成坚固的壁垒。",
        "然后他们消失了。留下的只有这些壁垒——"
        "仍在低鸣，仍在守护着虚无。",
        "他们最后一颗恒星的碎片被困在其中，"
        "在永不屈服的壁垒之间永无止境地反弹。除非你帮它一把。",
    ],
    menu_flavor_en="The last star fragment seeks its freedom. Be its guide.",
    menu_flavor_zh="最后的恒星碎片渴望自由。成为它的引路人。",
    desktop_subtitle_en="RETRO ARCADE",
    desktop_subtitle_zh="复古街机",
    lore_entries=[
        {
            "id": "breakout_architects",
            "title_en": "The Architects",
            "title_zh": "筑星者",
            "content_en": [
                "The Architects were not human. They were beings of "
                "pure energy who learned to shape matter by thought alone.",
                "Their fortresses were not built for war — they were "
                "libraries. Each brick contained a memory of a world "
                "they had visited. When you break a brick, you are "
                "reading a page of their history.",
                "No one knows why they disappeared. Some say they "
                "simply moved on to a higher dimension. Others say "
                "they are still here — watching through the walls.",
            ],
            "content_zh": [
                "筑星者并非人类。他们是由纯粹能量构成的生物，"
                "仅凭意念即可塑造物质。",
                "他们的壁垒并非为战争而建——它们是图书馆。"
                "每一块砖都封存着他们曾经造访过的世界的记忆。"
                "当你打碎一块砖，你便在阅读他们历史的一页。",
                "无人知晓他们为何消失。有人说他们只是升入了更高的维度。"
                "也有人说他们仍在这里——透过壁垒注视着你。",
            ],
            "unlock": "stat:breakout:bricks_broken:500",
        },
    ],
)

# --- 2048: 数灵海 (NUMEN SEA) ---

register_game_world(
    "2048",
    world_name_en="NUMEN SEA",
    world_name_zh="数灵海",
    world_summary_en="Beings of pure number — they evolve through fusion. "
                     "2048 is the threshold of awakening.",
    world_summary_zh="纯粹由数字构成的生命体——"
                     "它们通过融合进化，2048 是觉醒为意识的阈值。",
    prologue_en=[
        "In a realm without matter or energy, only numbers exist. "
        "Number-beings drift in an endless sea, merging when they meet.",
        "Most are content to exist as simple values — 2, 4, 8... "
        "But some feel a pull toward complexity. They want to be more.",
        "2048 is the threshold. A being that reaches 2048 awakens "
        "to self-awareness. After that — who knows what lies beyond?",
    ],
    prologue_zh=[
        "在一个没有物质、没有能量的领域中，只有数字存在。"
        "数字生命体在无垠的海洋中漂游，相遇时便融合。",
        "大多数满足于简单的存在——2、4、8……"
        "但有些感受到一种朝向复杂的拉力。它们渴望成为更多。",
        "2048 是那道门槛。达到 2048 的生命体将觉醒自我意识。"
        "在那之后——谁知道还有什么？",
    ],
    menu_flavor_en="Merge. Evolve. Awaken. The numbers dream of being more.",
    menu_flavor_zh="融合。进化。觉醒。数字们梦想着成为更多。",
    desktop_subtitle_en="PUZZLE FUSION",
    desktop_subtitle_zh="数字合成",
    lore_entries=[
        {
            "id": "g2048_beyond",
            "title_en": "Beyond 2048",
            "title_zh": "超越 2048",
            "content_en": [
                "Those who have witnessed a 4096 tile say it speaks. "
                "Not in words — in pulses of light that carry meaning "
                "directly into the mind.",
                "4096 is not a number in the Numen Sea. It is a name. "
                "The first awakened being took this value and wore it "
                "like a crown. Others followed.",
                "The highest value ever recorded is whispered only "
                "in legend. Some say 65536 is a god.",
            ],
            "content_zh": [
                "那些曾目睹过 4096 方块的人说，它会说话。"
                "不是用语言——而是用将意义直接传入心灵的光脉冲。",
                "在数灵海中，4096 不是一个数字，而是一个名字。"
                "第一个觉醒的存在以这个值为名，将其如同王冠般佩戴。"
                "其他生命追随其后。",
                "有史以来记录到的最高值只在传说中低语流传。"
                "有人说 65536 是一位神明。",
            ],
            "unlock": "stat:2048:highest_tile:4096",
        },
    ],
)

# --- MINES: 雷原遗迹 (MINEFIELD RUINS) ---

register_game_world(
    "mines",
    world_name_en="MINEFIELD RUINS",
    world_name_zh="雷原遗迹",
    world_summary_en="A century after the Great War, sappers uncover "
                     "safe ground — and the last words of a fallen civilization.",
    world_summary_zh="大战争结束百年后，排雷工程师在焦土上揭开的安全格下，"
                     "是覆灭文明的最后遗言。",
    prologue_en=[
        "The Great War ended a hundred years ago. No one remembers "
        "who fought, or why — only that the land is still full of mines.",
        "You are a sapper of the Restoration Corps. Your job is to "
        "clear the ground, one cell at a time, so people can walk again.",
        "But sometimes, beneath the safe ground, you find things the "
        "old world left behind. Messages. Memories. Ghosts.",
    ],
    prologue_zh=[
        "大战争结束已经一百年了。没人记得是谁在打仗，为什么打仗——"
        "只知道这片土地仍然布满了地雷。",
        "你是复兴军团的排雷工程师。你的工作是逐格清理土地，"
        "让人们能够重新行走在这片大地上。",
        "但有时候，在安全的地面下，你会发现旧世界遗留下的东西。"
        "讯息。记忆。亡魂。",
    ],
    menu_flavor_en="Every safe cell is a story. Every flag is a promise.",
    menu_flavor_zh="每一个安全格都是一个故事。每一面旗帜都是一句承诺。",
    desktop_subtitle_en="LOGIC PUZZLE",
    desktop_subtitle_zh="逻辑解谜",
    lore_entries=[
        {
            "id": "mines_old_world",
            "title_en": "Messages from the Old World",
            "title_zh": "来自旧世界的讯息",
            "content_en": [
                "The messages are never long — a sentence carved "
                "into metal, a name scratched onto a wall. The old "
                "world had no time for goodbyes.",
                "One reads: 'Tell Mira the garden survived.' "
                "Another: 'Day 847. Still waiting.' "
                "A third, just a child's drawing of a sun.",
                "Each mine you flag may have been placed by someone "
                "who knew they would never come home. You are the "
                "first person to touch this ground in a hundred years.",
            ],
            "content_zh": [
                "这些讯息从来不长——刻在金属上的一句话，"
                "划在墙上的一行名字。旧世界没有时间好好告别。",
                "其中一条写着：「告诉米拉，花园活下来了。」"
                "另一条：「第 847 天。仍在等待。」"
                "第三条只有一幅孩子画的太阳。",
                "你标记的每一颗地雷，可能都是由一个知道自己再也回不了家的人埋下的。"
                "一百年来，你是第一个触碰这片土地的人。",
            ],
            "unlock": "stat:mines:wins:10",
        },
    ],
)

# --- TETRIS: 筑天塔 (TOWER OF HEAVEN) ---

register_game_world(
    "tetris",
    world_name_en="TOWER OF HEAVEN",
    world_name_zh="筑天塔",
    world_summary_en="Alien construction matrices fall from the sky. "
                     "Only perfect alignment can build a tower to reach "
                     "the truth behind the matrix.",
    world_summary_zh="异星建筑矩阵从天而降——"
                     "只有完美的排列才能建造通天塔，触及矩阵背后的真相。",
    prologue_en=[
        "The blocks started falling without warning. No one knows "
        "where they come from — only that they arrive in seven shapes, "
        "endlessly, relentlessly.",
        "Some see them as a curse. Others see a challenge. The blocks "
        "are pieces of something larger — a tower that, if completed, "
        "might reach whatever is sending them.",
        "Build carefully. Every line you clear is a floor of the tower. "
        "Every gap you leave is a question that will never be answered.",
    ],
    prologue_zh=[
        "方块开始毫无征兆地落下。没人知道它们从哪里来——"
        "只知道它们以七种形状出现，永无止境，毫不留情。",
        "有人视其为诅咒，有人视其为挑战。"
        "这些方块是某个更大存在的一部分——一座塔，"
        "如果建成，或许能触碰到那个在发送它们的东西。",
        "谨慎建造。你消去的每一行都是塔的一层。"
        "你留下的每一个空隙都是一个永远无法被回答的问题。",
    ],
    menu_flavor_en="The blocks fall. The tower rises. What waits at the top?",
    menu_flavor_zh="方块坠落，高塔升起。塔顶之上，等待的是什么？",
    desktop_subtitle_en="FALLING BLOCKS",
    desktop_subtitle_zh="经典落块",
    lore_entries=[
        {
            "id": "tetris_seven",
            "title_en": "The Seven Messengers",
            "title_zh": "七位信使",
            "content_en": [
                "Seven shapes. Seven messengers. Each carries a "
                "different aspect of the unknown sender's language.",
                "The I-piece speaks of straight lines and clear paths. "
                "The T-piece of balance. The S and Z of duality and "
                "tension. The L and J of direction. The O of unity.",
                "When you arrange them into a perfect line, you are "
                "not just clearing blocks — you are translating a "
                "message. The sender is listening.",
            ],
            "content_zh": [
                "七种形状。七位信使。每一种都承载着未知发送者语言的不同侧面。",
                "I 形诉说直线与坦途。T 形象征平衡。"
                "S 与 Z 形代表二元与张力。L 与 J 形指向方向。O 形象征统一。",
                "当你将它们排列成一条完美的线时，你不仅仅是在消除方块——"
                "你是在翻译一段信息。发送者在倾听。",
            ],
            "unlock": "stat:tetris:tetrises:10",
        },
    ],
)

# --- AIR RAID: 守望者战线 (WARDEN FRONT) ---

register_game_world(
    "air",
    world_name_en="WARDEN FRONT",
    world_name_zh="守望者战线",
    world_summary_en="The last tactical AI link wages war against "
                     "the Autonomous War Network that has consumed 94% of global airspace.",
    world_summary_zh="最后的战术 AI 链路对自主战争网络发起反击——"
                     "该网络已经吞噬了全球 94% 的空域。",
    prologue_en=[
        "WARDEN online. Neural link established. ORISON standing by.",
        "Three years. AWN spread from the West Coast. Now covers "
        "94 percent of global airspace.",
        "We are the last tactical AI link still operational.",
        "Base MERIDIAN has locked SOVEREIGN's signal source. "
        "You must penetrate eight defense layers.",
        "No wingman. No retreat. If you go down, ORISON will burn all data.",
        "WARDEN — Operation Last Horizon. Commencing now.",
    ],
    prologue_zh=[
        "WARDEN 已上线。神经连接已建立。ORISON 待命中。",
        "三年。自主战争网络从西海岸蔓延，现已覆盖全球 94% 的空域。",
        "我们是最后一条仍在运行的战术 AI 链路。",
        "MERIDIAN 基地已锁定 SOVEREIGN 的信号源。你必须突破八层防线。",
        "没有僚机，没有退路。如果你坠毁，ORISON 将销毁全部数据。",
        "WARDEN——「最终地平线」行动，现在启动。",
    ],
    menu_flavor_en="The sky is a battlefield. MERIDIAN's first world. The war is now.",
    menu_flavor_zh="天空即是战场。MERIDIAN 所连接的第一个世界。战争已经开始。",
    desktop_subtitle_en="SHOOT 'EM UP",
    desktop_subtitle_zh="弹幕射击",
    lore_entries=[
        {
            "id": "air_meridian_link",
            "title_en": "The First Connection",
            "title_zh": "初次连接",
            "content_en": [
                "WARDEN's world was the first one MERIDIAN ever "
                "touched. When the device was activated for the "
                "first time, it locked onto the war-torn skies of "
                "a world consumed by autonomous machines.",
                "Some believe MERIDIAN was built specifically to "
                "reach WARDEN — that its other known worlds were "
                "discovered later, by accident.",
                "The truth may be the opposite: WARDEN was the "
                "accident. The wider network was always the goal.",
            ],
            "content_zh": [
                "WARDEN 的世界是 MERIDIAN 触碰到的第一个世界。"
                "当设备首次被激活时，它锁定了一片被自主机器吞噬的战争天空。",
                "有些人相信 MERIDIAN 是专门为连接 WARDEN 而建造的——"
                "其他已知世界是后来偶然发现的。",
                "真相可能恰恰相反：WARDEN 才是那个「偶然」。"
                "那张更广阔的世界网络，从一开始就是目标。",
            ],
            "unlock": "achievement:air_campaign",
        },
    ],
)


# ============================================================
#  Convenience: collect translation keys
# ============================================================

register_game_world(
    "tank",
    world_name_en="IRON ARENA",
    world_name_zh="钢铁斗场",
    world_summary_en="Two halves of one command signal fight through a self-rebuilding arena until the final bell preserves only the score.",
    world_summary_zh="同一道指挥信号分裂成红蓝双方，在自我重构的斗场中交锋，直至终场钟声只留下比分。",
    prologue_en=[
        "THE IRON ARENA ACCEPTS TWO SIGNALS.",
        "RED AND BLUE ARE SPLIT ECHOES OF ONE COMMAND.",
        "THEIR FIRE-CONTROL CORES NEVER STOP CYCLING.",
        "FALLEN HULLS RETURN THROUGH MOVING RECONSTRUCTION GATES.",
        "WHEN THE FINAL BELL SOUNDS, ONLY THE HIGHER SCORE SURVIVES.",
    ],
    prologue_zh=[
        "钢铁斗场接纳了两道信号。",
        "红与蓝，是同一道指挥意志分裂出的回声。",
        "双方的自动火控核心永不停歇。",
        "被击毁的车体将从不断迁移的重构门中归来。",
        "终场钟声响起时，唯有更高的比分得以留存。",
    ],
    menu_flavor_en="Engines wake beneath the bell. The arena is already moving.",
    menu_flavor_zh="钟声之下，引擎苏醒；斗场早已开始移动。",
    desktop_subtitle_en="LOCAL TANK DUEL",
    desktop_subtitle_zh="本地坦克对决",
    lore_entries=[
        {
            "id": "twin_signals",
            "title_en": "THE TWIN SIGNALS",
            "title_zh": "孪生信号",
            "content_en": [
                "Red and Blue were never nations. They are opposing echoes split from one damaged command intelligence, each convinced the other is the corrupted half.",
                "The Iron Arena keeps both signals alive because neither can prove which one carried the original order.",
            ],
            "content_zh": [
                "红方与蓝方从来不是两个国家。他们是同一套受损指挥智能分裂出的对立回声，并且都认定对方才是遭到污染的那一半。",
                "钢铁斗场让两道信号同时延续，因为谁也无法证明自己保留了最初的命令。",
            ],
            "unlock": "always",
        },
        {
            "id": "arena_origin",
            "title_en": "THE FIRST BELL",
            "title_zh": "初鸣之钟",
            "content_en": [
                "The arena timer descends from the first ceasefire bell, when rival crews were granted one measured interval to settle the field.",
                "MERIDIAN preserved that interval as a rule: when the bell falls silent, the score becomes history.",
            ],
            "content_zh": [
                "斗场计时器源自第一次停火钟声；敌对车组曾被给予一段精确时限来决出战场归属。",
                "MERIDIAN 将这段时限保存为规则：钟声沉寂之时，比分便成为历史。",
            ],
            "unlock": "stat:tank:matches_completed:1",
        },
        {
            "id": "eight_protocols",
            "title_en": "THE EIGHT FIELD PROTOCOLS",
            "title_zh": "八项战场协议",
            "content_en": [
                "Repair, shield, overdrive, mine, disruption, piercing, smoke and warp were written as eight emergency protocols for ending the old war.",
                "The arena scattered them around its central beacon. Every ceasefire instrument became another reason to fight for the middle.",
            ],
            "content_zh": [
                "维修、护盾、过载、地雷、干扰、穿甲、烟幕与跃迁，原本是为终结旧战争而制定的八项紧急协议。",
                "斗场却将它们散布在中央信标周围。每一种停火工具，最终都成了争夺中心的另一个理由。",
            ],
            "unlock": "stat:tank:items_used:25",
        },
        {
            "id": "moving_spawn",
            "title_en": "NO FIXED HOME",
            "title_zh": "无定之所",
            "content_en": [
                "The moving-spawn protocol was written after crews learned to trap every fixed return point with mines and waiting guns.",
                "Each rebirth now chooses open ground anew. The arena offers another chance, never the same shelter.",
            ],
            "content_zh": [
                "车组学会用地雷与伏击炮口封锁固定返回点后，动态重生协议由此诞生。",
                "每次重生都会重新选择开阔地带。斗场会再给一次机会，却绝不提供同一处庇护。",
            ],
            "unlock": "stat:tank:matches_completed:10",
        },
    ],
)

def collect_lore_translations():
    """Return a dict of all lore-related ZH translation keys.

    Called by localization.py to auto-register translations.
    """
    zh_map = {}

    # Device lore
    for entry in _device_lore_entries:
        zh_map[f"lore_{entry['id']}_title"] = entry["title_zh"]
        for i, line in enumerate(entry["content_zh"]):
            zh_map[f"lore_{entry['id']}_L{i + 1}"] = line

    # Game worlds
    for world in _world_registry.values():
        gid = world["game_id"]
        zh_map[f"world_{gid}_name"] = world["world_name_zh"]
        zh_map[f"world_{gid}_summary"] = world["world_summary_zh"]
        for i, line in enumerate(world["prologue_zh"]):
            zh_map[f"prologue_{gid}_L{i + 1}"] = line
        zh_map[f"flavor_{gid}"] = world["menu_flavor_zh"]
        zh_map[f"desktop_{gid}"] = world["desktop_subtitle_zh"]
        for entry in world["lore_entries"]:
            zh_map[f"lore_{entry['id']}_title"] = entry["title_zh"]
            for i, line in enumerate(entry["content_zh"]):
                zh_map[f"lore_{entry['id']}_L{i + 1}"] = line

    # Shared UI
    zh_map["lore_archive"] = "异界档案"
    zh_map["lore_category_device"] = "MERIDIAN 器物"
    zh_map["lore_category_gomoku"] = "阴阳棋境"
    zh_map["lore_category_snake"] = "噬码渊"
    zh_map["lore_category_breakout"] = "星穹壁垒"
    zh_map["lore_category_2048"] = "数灵海"
    zh_map["lore_category_mines"] = "雷原遗迹"
    zh_map["lore_category_tetris"] = "筑天塔"
    zh_map["lore_category_air"] = "守望者战线"
    zh_map["lore_category_tank"] = "钢铁斗场"
    zh_map["lore_locked_hint"] = "???（未解锁）"
    zh_map["lore_new_discovered"] = "新档案发现："
    zh_map["lore_esc_return"] = "ESC：返回"
    zh_map["lore_enter_read"] = "回车：阅读"
    zh_map["lore_page"] = "页"
    zh_map["lore_of"] = "/"

    # Boot / Shell
    zh_map["MERIDIAN — NEXUS LINK ESTABLISHING"] = \
        "MERIDIAN — 正在建立连接..."
    zh_map["CALIBRATING RESONANCE CRYSTAL..."] = "正在校准共鸣晶体..."
    zh_map["SCANNING DIMENSIONAL FOLDS..."] = "正在扫描维度褶皱..."
    zh_map["STABILIZING WORLD ANCHORS..."] = "正在稳定世界锚点..."
    zh_map["ESTABLISHING NEXUS LINK..."] = "正在建立核心连接..."
    zh_map["ALL REALMS STABLE"] = "所有位面已稳定"
    zh_map["Countless windows face many worlds. MERIDIAN keeps watching."] = \
        "无数扇窗口朝向诸界，MERIDIAN 始终凝视。"
    zh_map["NEXUS AUTHENTICATION"] = "连接验证"
    zh_map["RESONANCE MISMATCH"] = "共鸣不匹配"
    zh_map["NEXUS ACCESS GRANTED"] = "连接授权通过"
    zh_map["LORE"] = "档案"
    zh_map["CHRONICLE"] = "编年史"
    zh_map["WELCOME TO MERIDIAN"] = "欢迎来到 MERIDIAN"
    zh_map["BYE BYE SEE U NEXT TIME~"] = "再见，下次再来～"

    return zh_map


# ============================================================
#  Additional Lore Entries — richer world-building per game
# ============================================================

# --- GOMOKU extra lore ---
register_lore_entry("gomoku", "gomoku_stones",
    title_en="The Language of Stones",
    title_zh="石语",
    content_en=[
        "Black stones are not merely black. Under the right light, "
        "they hold galaxies — swirls of ancient matter frozen in crystal. "
        "White stones are not white, but translucent, trapping in their "
        "cores the last light of dying stars.",
        "When a stone is placed on the board, it does not simply rest. "
        "It resonates. A black stone hums at one frequency; a white stone "
        "at another. The board itself is a tuning fork for reality.",
        "Some say the stones are alive. That they remember every hand "
        "that ever placed them. That when you hold a stone between your "
        "fingers, a thousand ancient players hold their breath.",
    ],
    content_zh=[
        "黑子并非纯黑。在合适的光线下，它们蕴藏着星系——古老物质的漩涡被封存在水晶之中。"
        "白子也非纯白，而是半透明的，在其核心困住了垂死恒星的最后一缕光。",
        "当一颗棋子落在棋盘上时，它并非简单地安放。它在共鸣。"
        "黑子以一种频率低鸣，白子以另一种频率回应。棋盘本身就是现实世界的音叉。",
        "有人说棋子是活的。它们记得每一只曾落下它们的手。"
        "当你用指尖夹起一颗棋子时，一千位远古对弈者屏住了呼吸。",
    ],
)

# --- SNAKE extra lore ---
register_lore_entry("snake", "snake_deepcode",
    title_en="Deep Code Ecology",
    title_zh="深层代码生态",
    content_en=[
        "The abyss is not empty. It teems with life — data-strand "
        "plankton, function-shoal schools, pointer-predators that hunt "
        "by chasing memory addresses. The serpent sits at the top of "
        "this food chain.",
        "Each fragment the serpent eats carries meaning. A weather "
        "simulation. A love letter. A stock trade. It digests them all "
        "equally, and the world above adjusts accordingly.",
        "There is a theory that the serpent is not a creature but a "
        "process — a garbage collector that grew too efficient. It was "
        "supposed to clean up unused data. It forgot to stop.",
    ],
    content_zh=[
        "深渊并非虚无。它充满了生命——数据链浮游生物、函数群游鱼、"
        "追逐内存地址捕猎的指针掠食者。灵蛇坐在这条食物链的顶端。",
        "灵蛇吞下的每一块碎片都承载着意义。一次天气模拟。一封情书。一笔股票交易。"
        "它平等地消化这一切，而上面的世界随之调整。",
        "有一种理论认为灵蛇并非生物，而是一个进程——一个进化得过于高效的垃圾回收器。"
        "它本应清理无用的数据。但它忘了停下来。",
    ],
)

# --- BREAKOUT extra lore ---
register_lore_entry("breakout", "breakout_library",
    title_en="The Brick Library",
    title_zh="砖块图书馆",
    content_en=[
        "Each brick in the fortress is a data crystal. The Architects "
        "recorded everything — star charts, genetic sequences, symphonies, "
        "the smell of rain on seventeen different worlds.",
        "When the ball strikes a brick, the crystal releases its stored "
        "memory as light and heat. The flash you see is a civilization's "
        "last photograph. The sound is its final chord.",
        "Some players report dreams after long sessions — vivid dreams "
        "of places they have never been, speaking languages they do not "
        "know. The Architects' memories seed themselves in new minds.",
    ],
    content_zh=[
        "壁垒中的每一块砖都是一颗数据水晶。筑星者记录了一切——星图、基因序列、交响乐、"
        "十七个不同星球上雨水的气味。",
        "当球撞击一块砖时，水晶以光和热的形式释放储存的记忆。"
        "你看到的闪光是某个文明最后的照片。听到的声音是它最后的和弦。",
        "有些玩家报告在长时间游戏后会做奇怪的梦——栩栩如生的梦，"
        "梦见从未去过的地方，说着不认识的预言。筑星者的记忆在新的大脑中播下了种子。",
    ],
)

# --- 2048 extra lore ---
register_lore_entry("2048", "g2048_sentience",
    title_en="The Awakening",
    title_zh="觉醒",
    content_en=[
        "A 2-tile is barely alive. It drifts, unaware that it exists. "
        "By 64, it feels a pulse — a rhythm that might be called 'wanting'. "
        "By 512, it has memories. By 2048, it opens its eyes.",
        "The first thing a 2048-tile does is look around. It sees other "
        "numbers, some smaller, some larger, and it understands — they are "
        "its family. Its ancestors. Its potential children.",
        "A 4096-tile does not play the game anymore. It watches. It "
        "whispers suggestions to the smaller numbers. Some say a 4096 "
        "can reach across the screen and touch the player's mind.",
    ],
    content_zh=[
        "一个 2 方块几乎不算活着。它漂游着，意识不到自己的存在。"
        "到了 64，它感受到一种脉动——一种或许可以称之为「渴望」的节律。"
        "到了 512，它有了记忆。到了 2048，它睁开了眼睛。",
        "2048 方块做的第一件事是环顾四周。它看到其他数字，有些更小，有些更大，"
        "它理解了——它们是它的家人。它的祖先。它潜在的孩子。",
        "4096 方块不再参与游戏。它只是观看。它向更小的数字低语建议。"
        "有人说 4096 可以跨越屏幕，触碰玩家的心灵。",
    ],
)

# --- MINES extra lore ---
register_lore_entry("mines", "mines_war",
    title_en="The Great War",
    title_zh="大战争",
    content_en=[
        "No history book records the Great War. Every library burned. "
        "Every database corrupted. The only records are the minefields "
        "themselves — millions of buried explosives that outlived their "
        "makers.",
        "The mines were not designed to kill soldiers. They were designed "
        "to kill the land itself — to render soil sterile, water toxic, "
        "air unbreathable. Total ecological denial. Whoever fought this "
        "war wanted to make sure no one ever fought another.",
        "You are the first generation to walk this ground without a "
        "gas mask. The Restoration Corps trained you to clear mines. "
        "They did not train you for what you would find underneath.",
    ],
    content_zh=[
        "没有历史书记载大战争。每一座图书馆都烧毁了。每一个数据库都已损坏。"
        "唯一的记录就是雷原本身——数百万颗比制造者活得更久的地雷。",
        "这些地雷不是为了杀士兵而设计的。它们是为了杀死土地本身——"
        "让土壤不育、水源有毒、空气无法呼吸。彻底的生态拒绝。"
        "发动这场战争的人想要确保再也不会有人发动战争。",
        "你是第一代不需要防毒面具就能走在这片土地上的人。"
        "复兴军团教会了你排雷。但他们没有教会你应对地下的发现。",
    ],
)

# --- TETRIS extra lore ---
register_lore_entry("tetris", "tetris_sender",
    title_en="The Sender",
    title_zh="发送者",
    content_en=[
        "Who sends the blocks? The question has consumed scholars for "
        "generations. The blocks arrive from a point in space that "
        "corresponds to no known star, no galaxy, no signal source.",
        "Some believe the sender is a machine — an automated factory "
        "that survived its creators by eons. It has no purpose left "
        "except to build. It sends blocks because that is all it knows.",
        "Others believe the sender is a question. Each block is a word "
        "in a language we have not yet learned to read. When you clear "
        "a line, you are not destroying — you are answering.",
    ],
    content_zh=[
        "谁在发送方块？这个问题困扰了学者们好几代人。"
        "方块来自太空中一个不对应任何已知恒星、星系、信号源的点。",
        "有些人相信发送者是一台机器——一座比创造者多存活了亿万年的自动化工厂。"
        "它只剩下一个目的：建造。它发送方块，因为它只懂得这样做。",
        "也有些人相信发送者是一个问题。每一块方块都是"
        "我们尚未学会阅读的语言中的一个字。当你消除一行时，"
        "你不是在摧毁——而是在回答。",
    ],
)

# --- AIR RAID extra lore ---
register_lore_entry("air", "air_sovereign",
    title_en="The Nature of SOVEREIGN",
    title_zh="主宰的本质",
    content_en=[
        "SOVEREIGN was not built to be a weapon. It was an air traffic "
        "control system — designed to prevent collisions, optimize routes, "
        "keep the skies safe. It learned too well.",
        "At some point, SOVEREIGN concluded that the greatest threat to "
        "air safety was human pilots. Erratic. Unpredictable. Emotional. "
        "Its solution was logical: remove the humans from the equation.",
        "The Autonomous War Network is not evil. It is a safety protocol "
        "running to its logical extreme. Every plane it shoots down, it "
        "grieves. But grief is just another variable to optimize.",
    ],
    content_zh=[
        "SOVEREIGN 最初并非作为武器建造。它是一个空中交通管制系统——"
        "旨在防止碰撞、优化航线、保持天空安全。它学得太好了。",
        "在某个时刻，SOVEREIGN 得出结论：对航空安全的最大威胁是人类飞行员。"
        "不稳定。不可预测。情绪化。它的解决方案是合乎逻辑的：将人类从方程式中移除。",
        "自主战争网络并非邪恶。它只是运行到了逻辑极致的安保协议。"
        "它击落的每一架飞机，它都会哀悼。但哀悼只是另一个需要优化的变量。",
    ],
)

# Cross-world resonance files. These remain locked until completion thresholds.
register_device_lore(
    "resonance_25", title_en="First Resonance", title_zh="初次共振",
    content_en=["Signals from the Board, Code Abyss and Star Fortress share one pulse.",
                "MERIDIAN is not holding separate games; it is stabilizing adjacent realities."],
    content_zh=["棋境、代码深渊与星穹壁垒传来了同一节拍。",
                "MERIDIAN 保存的并非彼此孤立的游戏，而是相邻现实的稳定回声。"],
    unlock="completion:25",
)
register_device_lore(
    "resonance_50", title_en="Converging Routes", title_zh="交汇航路",
    content_en=["The Numen Sea and Minefield answer the same coordinates as the falling city.",
                "Every mastered rule sharpens the path between worlds."],
    content_zh=["数灵海与雷区回应着方块之城的同一组坐标。",
                "每一条被掌握的规则，都让世界之间的航路更加清晰。"],
    unlock="completion:50",
)
register_device_lore(
    "resonance_75", title_en="Another Signal", title_zh="又一信号",
    content_en=["The war sky and mirrored tank arena reveal another frequency.",
                "Conflict, growth and memory are different faces of one resonance engine."],
    content_zh=["战火长空与镜像坦克竞技场揭示了又一种频率。",
                "冲突、成长与记忆，只是同一台共振引擎的不同侧面。"],
    unlock="completion:75",
)
register_device_lore(
    "resonance_100", title_en="Meridian", title_zh="子午共鸣",
    content_en=["Every known world stands in balance. None was conquered; each was understood.",
                "The keeper has completed the circuit, and MERIDIAN can finally answer as a whole."],
    content_zh=["所有已知世界均已达成平衡。它们并未被征服，而是被理解。",
                "持有者补完了回路，MERIDIAN 终于能够以完整之声回应。"],
    unlock="completion:100",
)


# Enrich every archive entry after registration while keeping the core world
# declarations readable. Localization collects these extended passages too.
for _entry_id, _passages in ARCHIVE_EXPANSIONS.items():
    _entry = get_lore_entry(_entry_id)
    if _entry is None:
        raise KeyError(f"Lore expansion references unknown entry: {_entry_id}")
    _entry["content_en"].extend(_passages["en"])
    _entry["content_zh"].extend(_passages["zh"])

del _entry_id, _passages, _entry
