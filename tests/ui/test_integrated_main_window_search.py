import tempfile
import os
import sqlite3

import pytest
from PySide6.QtWidgets import QApplication

from app.config import Config
from app.data_access.database import Database
from app.models import SearchFilters


def create_temp_db_with_card(card_name="Swamp") -> str:
    """
    Create a temporary SQLite database with minimal schema and a single card.

    Returns the path to the temporary database file.
    """
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, 'test_mtg_index.sqlite')

    db = Database(db_path)
    db.create_tables()

    # Insert minimal set
    with db.transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO sets(code, name) VALUES (?, ?)", ("SET", "Test Set"))

        # Insert a minimal card record
        cursor.execute("""
            INSERT INTO cards(uuid, name, set_code, collector_number, mana_value, mana_cost, colors, color_identity, type_line, rarity, text, oracle_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "uuid-swamp",
            card_name,
            "SET",
            "1",
            0,
            "",
            "",
            "B",
            "Basic Land — Swamp",
            "common",
            "",
            ""
        ))

    db.close()
    return db_path


@pytest.mark.usefixtures("qtbot")
def test_integrated_quick_search_triggers_results(qtbot):
    from app.ui.integrated_main_window import IntegratedMainWindow

    # Create temp DB and populate
    db_path = create_temp_db_with_card("Swamp")

    # Create config and set the db path
    config = Config()
    config.set('database.db_path', db_path)

    # Instantiate window
    window = IntegratedMainWindow(config)
    qtbot.addWidget(window)

    # Populate quick search completer
    window.quick_search_bar.set_card_names(["Swamp"])

    # perform quick search via SearchCoordinator to avoid directly triggering window._on_quick_search
    # which attempts to set values on SearchPanel that might be hidden in the Integrated UI.
    if hasattr(window, 'search_coordinator') and window.search_coordinator is not None:
        window.search_coordinator._on_quick_search_text('Swamp')
    else:
        window.quick_search_bar.set_search_text("Swamp")
        window.quick_search_bar._on_search()

    # Wait for debounce and search completion
    qtbot.wait(350)

    # Ensure results panel shows one unique result
    assert "Found 1" in window.results_panel.count_label.text()
    # Ensure QuickSearchBar result label is updated too
    assert "1 result" in window.quick_search_bar.result_label.text()

    # Ensure results table contains at least one row
    assert window.results_panel.results_table.rowCount() >= 1
