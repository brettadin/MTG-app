"""
Simple tutorial dialog to guide users through basic actions.
"""
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QListWidget, QTextBrowser
)

logger = logging.getLogger(__name__)


class TutorialDialog(QDialog):
    """A simple tutorial wizard with a list of steps and a description pane.

    This dialog is intentionally non-invasive: it doesn't highlight UI elements
    (that would require deeper UI orchestration), but it provides a step-by-step
    checklist and context for each step. Future agents can augment it to
    highlight widgets or run each step programmatically.
    """

    def __init__(self, steps=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tutorial")
        self.setMinimumSize(800, 500)

        if steps is None:
            steps = [
                ("Create a Deck", "Use File → New Deck to create a new deck."),
                ("Search for Cards", "Use the quick search to find a card, e.g., 'Lightning Bolt'."),
                ("View Details", "Click a result to open Card Details and view rulings and printings."),
                ("Add to Deck", "Click '+ Add to Deck' in the card detail panel to add the card to your active deck."),
                ("Validate & Playtest", "Use Deck → Validate Deck and Deck → Playtest (Goldfish) to simulate draws and mana curves."),
            ]

        self.steps = steps
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        top_label = QLabel("A short interactive tutorial to get you started. Follow the steps on the left and read the details on the right.")
        top_label.setWordWrap(True)
        layout.addWidget(top_label)

        inner = QHBoxLayout()

        self.steps_list = QListWidget()
        for title, _ in self.steps:
            self.steps_list.addItem(title)
        self.steps_list.currentRowChanged.connect(self._on_step_changed)
        inner.addWidget(self.steps_list, 1)

        self.description = QTextBrowser()
        inner.addWidget(self.description, 2)

        layout.addLayout(inner)

        # Footer with navigation and close
        footer = QHBoxLayout()
        self.prev_btn = QPushButton("Back")
        self.prev_btn.clicked.connect(self._prev)
        footer.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self._next)
        footer.addWidget(self.next_btn)

        footer.addStretch()
        self.finish_btn = QPushButton("Finish")
        self.finish_btn.clicked.connect(self.accept)
        footer.addWidget(self.finish_btn)

        layout.addLayout(footer)

        # Select first step
        if self.steps:
            self.steps_list.setCurrentRow(0)

    def _on_step_changed(self, index: int):
        if index < 0 or index >= len(self.steps):
            self.description.clear()
            return
        _, desc = self.steps[index]
        self.description.setPlainText(desc)
        self._update_nav(index)

    def _update_nav(self, index: int):
        self.prev_btn.setEnabled(index > 0)
        self.next_btn.setEnabled(index < len(self.steps) - 1)

    def _prev(self):
        row = max(0, self.steps_list.currentRow() - 1)
        self.steps_list.setCurrentRow(row)

    def _next(self):
        row = min(len(self.steps) - 1, self.steps_list.currentRow() + 1)
        self.steps_list.setCurrentRow(row)
