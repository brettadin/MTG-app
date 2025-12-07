"""
Documentation viewer dialog for in-app help and rules.
"""
import logging
from pathlib import Path
from typing import List, Tuple

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QTextBrowser, QPushButton, QLabel, QLineEdit
)
from PySide6.QtCore import Qt

logger = logging.getLogger(__name__)


class DocumentationDialog(QDialog):
    """Simple documentation browser to view markdown files in-app.

    The dialog shows a list of available docs on the left and the rendered
    content on the right. It attempts to render Markdown via QTextBrowser
    setMarkdown(), and falls back to plain text or HTML if needed.
    """

    def __init__(self, docs: List[Tuple[str, str]] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Documentation")
        self.setMinimumSize(900, 600)

        self._docs: List[Tuple[str, Path]] = []
        if docs is None:
            docs = []
        for name, path in docs:
            self._docs.append((name, Path(path)))

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        top_bar = QHBoxLayout()
        label = QLabel("Documentation")
        label.setStyleSheet("font-weight: bold; font-size: 16px")
        top_bar.addWidget(label)
        top_bar.addStretch()
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        top_bar.addWidget(self.close_btn)
        layout.addLayout(top_bar)

        inner = QHBoxLayout()
        # Left pane: doc list and search
        left = QVBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Filter documentation...")
        self.search_box.textChanged.connect(self._filter_docs)
        left.addWidget(self.search_box)

        self.list_widget = QListWidget()
        for name, _ in self._docs:
            self.list_widget.addItem(name)
        self.list_widget.currentRowChanged.connect(self._on_selection_changed)
        left.addWidget(self.list_widget)

        inner.addLayout(left, stretch=1)

        # Right pane: markdown/HTML render
        self.viewer = QTextBrowser()
        # Optional: enable link handling to open in system browser
        self.viewer.setOpenExternalLinks(True)
        inner.addWidget(self.viewer, stretch=3)

        layout.addLayout(inner)

        # Select first doc by default
        if self._docs:
            self.list_widget.setCurrentRow(0)

    def _filter_docs(self, text: str):
        text = text.lower().strip()
        self.list_widget.clear()
        for name, _ in self._docs:
            if not text or text in name.lower():
                self.list_widget.addItem(name)

    def _on_selection_changed(self, index: int):
        if index < 0:
            return
        # Map the visible row (in filtered mode) to doc path; we can rebuild list
        current_name = self.list_widget.item(index).text()
        for name, path in self._docs:
            if name == current_name:
                self._load_doc(path)
                return

    def _load_doc(self, path: Path):
        try:
            if not path.exists():
                self.viewer.setText(f"Documentation not found: {path}")
                return
            text = path.read_text(encoding="utf-8")

            # Try to use Markdown rendering if available in QTextBrowser
            try:
                self.viewer.setMarkdown(text)
            except Exception:
                # Fall back to raw text display
                try:
                    import markdown as md
                    html = md.markdown(text)
                    self.viewer.setHtml(html)
                except Exception:
                    # Last resort: plain text
                    self.viewer.setPlainText(text)
        except Exception as e:
            logger.error(f"Failed to load doc {path}: {e}")
            self.viewer.setText(f"Error loading doc: {e}")
