from __future__ import annotations

from typing import Protocol
from .interaction_port import InteractionPort


class FramePort(InteractionPort, Protocol):

    def frame_locator(selector: str) -> "FramePort": ...
