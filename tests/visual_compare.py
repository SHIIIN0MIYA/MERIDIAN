from dataclasses import dataclass, field

import pygame


@dataclass(frozen=True)
class VisualDiff:
    different_pixels: int
    total_pixels: int
    ratio: float
    diff_surface: pygame.Surface
    _passed: bool = field(init=False, repr=False, compare=False)

    @property
    def passed(self) -> bool:
        return self._passed


def compare_surfaces(
    actual: pygame.Surface,
    expected: pygame.Surface,
    tolerance: float = 0.0005,
) -> VisualDiff:
    if actual.get_size() != expected.get_size():
        raise ValueError(
            f"surface size mismatch: {actual.get_size()} != {expected.get_size()}"
        )

    width, height = actual.get_size()
    total_pixels = width * height
    different_pixels = 0
    diff_surface = pygame.Surface((width, height))

    actual.lock()
    expected.lock()
    diff_surface.lock()
    try:
        for y in range(height):
            for x in range(width):
                actual_color = actual.get_at((x, y))
                expected_color = expected.get_at((x, y))
                if actual_color[:3] != expected_color[:3]:
                    different_pixels += 1
                    diff_surface.set_at((x, y), (255, 0, 255))
                else:
                    diff_surface.set_at(
                        (x, y),
                        tuple(channel // 4 for channel in actual_color[:3]),
                    )
    finally:
        diff_surface.unlock()
        expected.unlock()
        actual.unlock()

    ratio = different_pixels / total_pixels if total_pixels else 0.0
    result = VisualDiff(different_pixels, total_pixels, ratio, diff_surface)
    object.__setattr__(result, "_passed", ratio <= tolerance)
    return result
