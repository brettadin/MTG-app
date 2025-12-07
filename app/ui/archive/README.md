Archived UI code

This directory contains historical or archived UI code that has been replaced by `IntegratedMainWindow`.

Files placed here:
- `main_window.py` - Archived original main window implementation (see commit history for original content)
- `enhanced_main_window.py` - Archived enhanced window example (see commit history)

Reason: To consolidate UI into `IntegratedMainWindow` and reduce duplicate code across multiple main window implementations.

If you need to restore or review the original code, check git history (`git log -- app/ui/main_window.py`) and use `git checkout <commit> -- app/ui/main_window.py`.
