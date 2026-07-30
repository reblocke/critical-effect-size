"""Focused exact Wald critical-effect and detectability applet contract."""

from .contract import (
    SUPPORTED_RULES,
    calculate,
    calculate_json,
)
from .models import (
    CriticalEffectRequest,
    CriticalEffectResponse,
    ValidationError,
)
from .version import __version__

__all__ = [
    "SUPPORTED_RULES",
    "CriticalEffectRequest",
    "CriticalEffectResponse",
    "ValidationError",
    "__version__",
    "calculate",
    "calculate_json",
]
