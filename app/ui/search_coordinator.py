"""
SearchCoordinator: centralizes search signals from different UI inputs and dispatches to results panel.
"""
import logging
from typing import Optional
from PySide6.QtCore import QObject, QTimer

from app.models import SearchFilters

logger = logging.getLogger(__name__)


class SearchCoordinator(QObject):
    def __init__(self, repository, results_panel, search_panel=None, quick_search_bar=None, parent=None):
        super().__init__(parent)
        self.repository = repository
        self.results_panel = results_panel
        self.search_panel = search_panel
        self.quick_search_bar = quick_search_bar

        # Debounce timer for quick searches (avoid spamming repo on rapid typing)
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(200)  # ms
        self._debounce_timer.timeout.connect(self._run_pending_search)

        self._pending_filters: Optional[SearchFilters] = None

        # wire signals if provided
        if self.quick_search_bar is not None:
            try:
                # New signal: search_filters_requested
                self.quick_search_bar.search_filters_requested.connect(self._on_quick_search_filters)
            except Exception:
                try:
                    # Backwards-compatible: search_requested (string)
                    self.quick_search_bar.search_requested.connect(self._on_quick_search_text)
                except Exception:
                    pass

        if self.search_panel is not None:
            try:
                self.search_panel.search_triggered.connect(self._on_search_panel_filters)
            except Exception:
                # some panels might emit different signal types; ignore
                pass

        if self.results_panel is not None and self.quick_search_bar is not None:
            try:
                self.results_panel.search_completed.connect(self._on_search_completed)
            except Exception:
                pass

    def _on_quick_search_filters(self, filters: SearchFilters):
        logger.info(f"Quick search filters received: {filters}")
        self._pending_filters = filters
        self._debounce_timer.start()

    def _on_quick_search_text(self, query: str):
        try:
            filters = SearchFilters()
            filters.name = query
            filters.limit = 100
            self._pending_filters = filters
            self._debounce_timer.start()
        except Exception as e:
            logger.exception("Error creating SearchFilters from quick text", exc_info=e)

    def _on_search_panel_filters(self, filters: SearchFilters):
        # Panel initiated search should run immediately
        logger.info(f"Advanced search filters received: {filters}")
        self._pending_filters = filters
        # bypass debounce
        self._run_pending_search()

    def _run_pending_search(self):
        if not self._pending_filters:
            return
        filters = self._pending_filters
        self._pending_filters = None
        try:
            logger.info(f"Running search with filters: {filters}")
            # delegate to results panel which handles pagination
            self.results_panel.search_with_filters(filters)
            # Update UI search panel display if present
            if self.search_panel and hasattr(self.search_panel, 'set_search'):
                try:
                    self.search_panel.set_search(filters)
                except Exception:
                    pass
            # If we have quick_search_bar, set its result count when available
            # We don't block; results_panel may update result count later
        except Exception as e:
            logger.exception(f"Error running search: {e}", exc_info=e)

    def _on_search_completed(self, total_count: int):
        # Update quick search count label if available
        if self.quick_search_bar is not None and hasattr(self.quick_search_bar, 'set_result_count'):
            try:
                self.quick_search_bar.set_result_count(total_count)
            except Exception:
                pass