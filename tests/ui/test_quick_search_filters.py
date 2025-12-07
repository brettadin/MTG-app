import pytest
from PySide6.QtWidgets import QApplication

from app.ui.quick_search import QuickSearchBar
from app.models import SearchFilters


def test_quick_search_emits_filters(qtbot):
    quick = QuickSearchBar()
    qtbot.addWidget(quick)

    emitted = []

    def on_filters(filters):
        emitted.append(filters)

    quick.search_filters_requested.connect(on_filters)

    quick.search_input.setText("swamp")
    quick._on_search()

    assert len(emitted) == 1
    assert isinstance(emitted[0], SearchFilters)
    assert emitted[0].name == "swamp"


class FakeResultsPanel:
    def __init__(self):
        self.called_with = None

    def search_with_filters(self, filters):
        self.called_with = filters


def test_search_coordinator_debounced_search(qtbot):
    from app.ui.search_coordinator import SearchCoordinator
    from app.ui.panels.search_panel import SearchPanel

    # Create quick search and results panel
    quick = QuickSearchBar()
    results = FakeResultsPanel()
    panel = SearchPanel(None, None)

    # Instantiate coordinator
    coord = SearchCoordinator(None, results, search_panel=panel, quick_search_bar=quick)

    # Emit search filters
    filters = SearchFilters()
    filters.name = "island"
    quick.search_filters_requested.emit(filters)

    qtbot.wait(300)  # wait for debounce

    assert isinstance(results.called_with, SearchFilters)
    assert results.called_with.name == "island"


def test_search_panel_set_search(qtbot):
    from app.ui.panels.search_panel import SearchPanel
    from app.config import Config

    config = Config()
    # show name input to verify it is filled
    panel = SearchPanel(None, config, show_name_input=True)
    qtbot.addWidget(panel)

    filters = SearchFilters()
    filters.name = "Mountain"
    filters.text = """"""
    filters.type_line = "Land"

    panel.set_search(filters)

    assert panel.name_input.text() == "Mountain"
    assert panel.type_input.text() == "Land"


def test_search_panel_hide_name_input(qtbot):
    from app.ui.panels.search_panel import SearchPanel
    from app.config import Config

    config = Config()
    panel = SearchPanel(None, config, show_name_input=False)
    qtbot.addWidget(panel)

    # Name group should be hidden (name_input may not exist in layout)
    # We check that the widget still has attribute but it is not in the visible layout
    assert hasattr(panel, 'name_input')

    # Setting a SearchFilters object should not raise even if name_input isn't visible
    filters = SearchFilters()
    filters.name = 'Island'
    panel.set_search(filters)


def test_search_coordinator_updates_quick_count(qtbot):
    from app.ui.search_coordinator import SearchCoordinator
    from app.ui.panels.search_panel import SearchPanel
    from PySide6.QtCore import QObject, Signal

    class FakeResultsPanel(QObject):
        search_completed = Signal(int)

        def __init__(self):
            super().__init__()
            self.called_with = None

        def search_with_filters(self, filters):
            self.called_with = filters
            # Simulate search finished with 1 result
            self.search_completed.emit(1)

    quick = QuickSearchBar()
    results = FakeResultsPanel()
    panel = SearchPanel(None, None)
    qtbot.addWidget(quick)

    coord = SearchCoordinator(None, results, search_panel=panel, quick_search_bar=quick)

    # Emit filters
    filters = SearchFilters()
    filters.name = "Swamp"
    quick.search_filters_requested.emit(filters)

    qtbot.wait(300)

    # Coordinator should have invoked search and quick_search bar should have been updated
    assert isinstance(results.called_with, SearchFilters)
    assert results.called_with.name == "Swamp"
    assert quick.result_label.text() == "1 result"
