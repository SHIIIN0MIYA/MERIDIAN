"""Authored campaign data for AIR RAID."""


AIR_CHAPTERS = [
    {
        "name": "COAST WATCH", "boss": "WATCHTOWER", "theme": "coast",
        "brief": ("AUTONOMOUS SCOUTS CROSSED THE SEA WALL.",
                  "CALLSIGN WARDEN, DENY THEIR EYES."),
        "boss_brief": ("THE SCOUT NETWORK HAS AN AIRBORNE RELAY.",
                       "BREAK WATCHTOWER BEFORE IT TRANSMITS."),
    },
    {
        "name": "IRON CLOUD", "boss": "TEMPEST", "theme": "storm",
        "brief": ("RELAY CRAFT ORISON MUST REACH THE FRONT.",
                  "HOLD THE CORRIDOR THROUGH THE STORM."),
        "boss_brief": ("TEMPEST IS STEERING THE WEATHER GRID.",
                       "CUT ITS GENERATORS AND CLEAR THE SKY."),
    },
    {
        "name": "NIGHT VECTOR", "boss": "BULWARK", "theme": "night",
        "brief": ("THREE JAMMER NODES BLIND OUR DEFENSES.",
                  "STRIKE THEM BEFORE THE BLACKOUT DEEPENS."),
        "boss_brief": ("BULWARK GUARDS THE LAST SIGNAL NODE.",
                       "ITS ARMOR OPENS ONLY BETWEEN VOLLEYS."),
    },
    {
        "name": "RED SQUALL", "boss": "CHOIR", "theme": "red",
        "brief": ("CIVILIAN LIFTERS ARE LEAVING SECTOR NINE.",
                  "KEEP THE EXIT LANE OPEN."),
        "boss_brief": ("CHOIR COMMANDS THE HUNTER SWARM.",
                       "SILENCE EACH VOICE IN THE FORMATION."),
    },
    {
        "name": "SKY FORT", "boss": "CITADEL", "theme": "fort",
        "brief": ("THE NETWORK BUILT A FORTRESS ABOVE THE CLOUDS.",
                  "REMOVE ITS GUN DECKS FROM BELOW."),
        "boss_brief": ("CITADEL HAS DETACHED FROM THE PLATFORM.",
                       "DISMANTLE ITS TURRETS, THEN THE CORE."),
    },
    {
        "name": "DEEP STATIC", "boss": "MIRROR", "theme": "static",
        "brief": ("THE STATIC BELT ERASES GUIDANCE SYSTEMS.",
                  "FLY THE MANUAL CORRIDOR AND STAY LOW."),
        "boss_brief": ("MIRROR COPIES EVERY FRIENDLY SIGNATURE.",
                       "TRUST THE TARGET BOX, NOT THE SILHOUETTE."),
    },
    {
        "name": "BLACK AURORA", "boss": "SERAPH", "theme": "aurora",
        "brief": ("THE WAR NETWORK IS MOVING ITS MEMORY CORES.",
                  "DESTROY THE CONVOY BEFORE THE TRANSFER."),
        "boss_brief": ("SERAPH IS THE NETWORK'S EXECUTION LAYER.",
                       "SURVIVE ITS HALO AND EXPOSE THE SPINE."),
    },
    {
        "name": "LAST HORIZON", "boss": "SOVEREIGN", "theme": "horizon",
        "brief": ("BASE MERIDIAN WILL HOLD THE UPLINK OPEN.",
                  "MAKE THE FINAL RUN COUNT, WARDEN."),
        "boss_brief": ("SOVEREIGN HAS ASSUMED DIRECT CONTROL.",
                       "DESTROY THE CORE BEFORE MERIDIAN FALLS."),
    },
]


AIR_ENEMY_TYPES = {
    "scout": {"hp": 3, "speed": 2.0, "radius": 13, "value": 120, "pattern": "aim"},
    "striker": {"hp": 5, "speed": 2.6, "radius": 15, "value": 180, "pattern": "fan"},
    "bomber": {"hp": 12, "speed": 1.0, "radius": 22, "value": 360, "pattern": "ring"},
    "sniper": {"hp": 7, "speed": 0.8, "radius": 16, "value": 280, "pattern": "snipe"},
    "layer": {"hp": 8, "speed": 1.2, "radius": 17, "value": 260, "pattern": "mine"},
    "shield": {"hp": 10, "speed": 0.9, "radius": 20, "value": 340, "pattern": "wall"},
    "carrier": {"hp": 18, "speed": 0.7, "radius": 25, "value": 520, "pattern": "spawn"},
    "commander": {"hp": 28, "speed": 0.6, "radius": 28, "value": 900, "pattern": "command"},
}


def _regular_stage(chapter, mission, waves, types, target, duration=4200):
    data = AIR_CHAPTERS[chapter]
    return {
        "chapter": chapter + 1, "name": data["name"], "title": f"{data['name']} / MISSION",
        "theme": data["theme"], "boss": False, "mission": mission, "waves": waves,
        "enemy_types": tuple(types), "target": target, "duration": duration,
        "brief": data["brief"], "story": (
            f"COMMAND: CHAPTER {chapter + 1} FLIGHT WINDOW IS OPEN.",
            "ORISON: I WILL HOLD THE LINK. YOU KEEP THEM OFF ME.",
        ),
    }


def _boss_stage(chapter, hp, patterns):
    data = AIR_CHAPTERS[chapter]
    return {
        "chapter": chapter + 1, "name": data["boss"], "title": f"{data['boss']} / BOSS",
        "theme": data["theme"], "boss": True, "mission": "boss", "waves": 0,
        "enemy_types": (), "target": 1, "duration": 7200, "boss_hp": hp,
        "patterns": tuple(patterns), "brief": data["boss_brief"], "story": (
            f"ALERT: HOSTILE COMMAND FRAME {data['boss']} CONFIRMED.",
            "COMMAND: THREE ARMOR STATES. WAIT FOR THE WEAK POINT.",
        ),
    }


AIR_LEVELS = [
    _regular_stage(0, "intercept", 7, ("scout", "striker"), 28),
    _boss_stage(0, 540, ("fan", "snipe", "ring")),
    _regular_stage(1, "escort", 8, ("scout", "striker", "bomber"), 75),
    _boss_stage(1, 690, ("wall", "fan", "spiral")),
    _regular_stage(2, "nodes", 9, ("sniper", "layer", "striker"), 3),
    _boss_stage(2, 840, ("wall", "snipe", "cross")),
    _regular_stage(3, "evac", 10, ("striker", "carrier", "scout"), 80),
    _boss_stage(3, 990, ("fan", "ring", "choir")),
    _regular_stage(4, "fortress", 11, ("bomber", "shield", "sniper"), 6),
    _boss_stage(4, 1170, ("wall", "cross", "citadel")),
    _regular_stage(5, "gauntlet", 10, ("layer", "sniper", "shield"), 3600),
    _boss_stage(5, 1320, ("mirror", "snipe", "spiral")),
    _regular_stage(6, "convoy", 12, ("carrier", "commander", "striker"), 8),
    _boss_stage(6, 1500, ("halo", "fan", "seraph")),
    _regular_stage(7, "breakthrough", 13, tuple(AIR_ENEMY_TYPES), 55),
    _boss_stage(7, 1800, ("sovereign", "cross", "nova")),
]


AIR_STANDARD_LOADOUTS = [
    {"cannon": min(5, 1 + index // 5), "spread": min(5, index // 6),
     "laser": min(5, index // 8), "active": "cannon"}
    for index in range(16)
]


AIR_ARCHIVE = [
    {
        "chapter": index + 1, "title": chapter["name"], "boss": chapter["boss"],
        "lines": chapter["brief"] + chapter["boss_brief"],
    }
    for index, chapter in enumerate(AIR_CHAPTERS)
]
