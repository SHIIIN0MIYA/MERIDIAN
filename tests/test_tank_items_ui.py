import pygame

from meridian.tank_engine import ItemType
from meridian.tank_items_ui import draw_item_icon


def test_all_eight_item_icons_have_unique_pixel_signatures():
    pygame.init()
    signatures = []
    for item in ItemType:
        surface = pygame.Surface((32, 32))
        draw_item_icon(surface, item, surface.get_rect(), {"accent": (90, 230, 220)})
        signatures.append(pygame.image.tobytes(surface, "RGB"))
    assert len(set(signatures)) == 8
