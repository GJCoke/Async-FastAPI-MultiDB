"""
Author  : Coke
Date    : 2025-04-10
"""

from celery.beat import Scheduler as _Scheduler


class Scheduler(_Scheduler):
    """Custom Scheduler."""
