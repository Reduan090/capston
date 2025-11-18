"""Compatibility shim: keep `utils.doc_handler` but delegate to `utils.document_handler`.

This file exists to make the rename transparent to code that still imports
`utils.doc_handler`. The real implementation lives in `utils.document_handler`.
"""

from .document_handler import *  # noqa: F401,F403

__all__ = [name for name in dir() if not name.startswith("_")]