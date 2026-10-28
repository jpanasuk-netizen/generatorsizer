"""Hermes gateway bridge for the Connecture bus."""

from hermes.bridge import process_new
from hermes.configcheck import diagnose, repaired_primary

__all__ = ["diagnose", "process_new", "repaired_primary"]
