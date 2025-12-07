"""
Compatibility shim for legacy `main_window` module.

The original `MainWindow` implementation has been consolidated into
`IntegratedMainWindow` (see `app/ui/integrated_main_window.py`). This file
re-exports `IntegratedMainWindow` to maintain backward compatibility for
scripts or tools that import `MainWindow` from `app.ui.main_window`.
"""

import warnings

from app.ui.integrated_main_window import IntegratedMainWindow as MainWindow

warnings.warn(
    "app.ui.main_window.MainWindow has been archived; import app.ui.integrated_main_window.IntegratedMainWindow instead.",
    DeprecationWarning,
)
