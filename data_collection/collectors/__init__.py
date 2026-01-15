"""
Peer review collectors for different sources.
"""

from .elife_collector import ElifeCollector
from .f1000_collector import F1000Collector

__all__ = [
    'ElifeCollector',
    'F1000Collector',
]
