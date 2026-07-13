import pygame
import pytest

from tests.visual_compare import compare_surfaces


def test_compare_rejects_size_mismatch():
    with pytest.raises(ValueError, match="size mismatch"):
        compare_surfaces(pygame.Surface((10, 10)), pygame.Surface((11, 10)))


def test_compare_reports_exact_changed_pixel_count_and_ratio():
    actual = pygame.Surface((10, 10))
    expected = actual.copy()
    expected.set_at((2, 3), (255, 0, 0))

    diff = compare_surfaces(actual, expected, tolerance=0)

    assert diff.different_pixels == 1
    assert diff.total_pixels == 100
    assert diff.ratio == pytest.approx(0.01)


@pytest.mark.parametrize(
    ("changed_pixels", "tolerance", "passed"),
    ((1, 0.01, True), (2, 0.01, False)),
)
def test_compare_applies_tolerance_to_changed_pixel_ratio(
    changed_pixels, tolerance, passed
):
    actual = pygame.Surface((10, 10))
    expected = actual.copy()
    for x in range(changed_pixels):
        expected.set_at((x, 0), (255, 255, 255))

    diff = compare_surfaces(actual, expected, tolerance=tolerance)

    assert diff.passed is passed


def test_compare_builds_same_size_diff_with_dark_matches_and_magenta_changes():
    actual = pygame.Surface((2, 1))
    actual.set_at((0, 0), (80, 120, 160))
    actual.set_at((1, 0), (10, 20, 30))
    expected = actual.copy()
    expected.set_at((1, 0), (30, 20, 10))

    diff = compare_surfaces(actual, expected, tolerance=0)

    assert diff.diff_surface.get_size() == actual.get_size()
    assert diff.diff_surface.get_at((0, 0)) == pygame.Color(20, 30, 40, 255)
    assert diff.diff_surface.get_at((1, 0)) == pygame.Color(255, 0, 255, 255)
