"""H-001 · 저장소 골격 수용 테스트.

docs/02_CONTRACTS.md §1 패키지 구조 다이어그램 기준 11개 섹터.
카드 본문의 "12개 섹터"는 오기이며 무시한다.
"""

from __future__ import annotations

import importlib

import pytest

SECTORS = [
    "core",
    "plant",
    "connect",
    "semantic",
    "evidence",
    "operate",
    "studio",
    "agent",
    "twin",
    "physics",
    "capture",
]


@pytest.mark.parametrize("sector", SECTORS)
def test_all_sector_publics_importable(sector: str) -> None:
    """Each sector's public.py must import without error."""
    module = importlib.import_module(f"loom.{sector}.public")
    assert module is not None


def test_sector_list_has_no_duplicates() -> None:
    """Boundary: the 11 sectors are distinct (no accidental duplicate/typo)."""
    assert len(SECTORS) == len(set(SECTORS)) == 11


def test_empty_sector_name_is_not_importable() -> None:
    """Boundary: an empty/invalid sector name must fail to import, not silently pass."""
    with pytest.raises((ModuleNotFoundError, ImportError, ValueError)):
        importlib.import_module("loom..public")
