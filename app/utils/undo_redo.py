"""
Undo/Redo system for MTG Deck Builder.

Implements Command pattern for reversible deck operations.
"""

import logging
from typing import Optional, Any
from abc import ABC, abstractmethod
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class Command(ABC):
    """
    Abstract base class for undoable commands.
    """
    
    @abstractmethod
    def execute(self) -> bool:
        """
        Execute the command.
        
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """
        Undo the command.
        
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get human-readable description of command."""
        pass


class AddCardCommand(Command):
    """Command to add a card to a deck using DeckService (uses deck_id + card uuid)."""

    def __init__(self, deck_service, deck_id: int, card_uuid: str, count: int = 1, zone: str = 'main', card_name: str | None = None):
        """
        Initialize add card command.

        Args:
            deck_service: DeckService instance
            deck_id: ID of the deck to modify
            card_uuid: UUID of the card to add
            count: Number of copies
            zone: 'main', 'sideboard', or 'commander'
            card_name: Optional friendly name for UI descriptions
        """
        self.deck_service = deck_service
        self.deck_id = deck_id
        self.card_uuid = card_uuid
        self.count = count
        self.zone = zone
        self.card_name = card_name or card_uuid

    def execute(self) -> bool:
        """Add card to deck via DeckService."""
        try:
            if self.zone == 'main':
                # DeckService handles quantity aggregation
                result = self.deck_service.add_card(self.deck_id, self.card_uuid, self.count, is_commander=False)
            elif self.zone == 'sideboard':
                # Sideboard not yet fully modeled in DB; treat as main for now
                result = self.deck_service.add_card(self.deck_id, self.card_uuid, self.count, is_commander=False)
            elif self.zone == 'commander':
                # Set as commander
                result = self.deck_service.set_commander(self.deck_id, self.card_uuid, is_partner=False)
            else:
                result = False

            return bool(result)
        except Exception as e:
            logger.error(f"Error adding card: {e}")
            return False

    def undo(self) -> bool:
        """Remove card from deck via DeckService."""
        try:
            if self.zone == 'main' or self.zone == 'sideboard':
                result = self.deck_service.remove_card(self.deck_id, self.card_uuid, self.count)
            elif self.zone == 'commander':
                # Unset commander
                result = self.deck_service.set_commander(self.deck_id, None)
            else:
                result = False

            return bool(result)
        except Exception as e:
            logger.error(f"Error undoing add card: {e}")
            return False

    def get_description(self) -> str:
        """Get description for undo history UI."""
        name = self.card_name or self.card_uuid
        if self.count == 1:
            return f"Add {name}"
        return f"Add {self.count}x {name}"


class RemoveCardCommand(Command):
    """Command to remove a card from deck."""
    
    def __init__(self, deck_service, deck_name: str, card_name: str, count: int = 1, zone: str = 'main'):
        """
        Initialize remove card command.
        
        Args:
            deck_service: DeckService instance
            deck_name: Name of deck
            card_name: Card to remove
            count: Number of copies
            zone: 'main', 'sideboard', or 'commander'
        """
        self.deck_service = deck_service
        self.deck_name = deck_name
        self.card_name = card_name
        self.count = count
        self.zone = zone
    
    def execute(self) -> bool:
        """Remove card from deck."""
        try:
            deck = self.deck_service.get_deck(self.deck_name)
            if not deck:
                return False
            
            if self.zone == 'main':
                for _ in range(self.count):
                    deck.remove_card(self.card_name)
            elif self.zone == 'sideboard':
                for _ in range(self.count):
                    deck.remove_sideboard_card(self.card_name)
            elif self.zone == 'commander':
                deck.set_commander(None)
            
            self.deck_service.save_deck(deck)
            return True
        except Exception as e:
            logger.error(f"Error removing card: {e}")
            return False
    
    def undo(self) -> bool:
        """Re-add card to deck."""
        try:
            deck = self.deck_service.get_deck(self.deck_name)
            if not deck:
                return False
            
            if self.zone == 'main':
                for _ in range(self.count):
                    deck.add_card(self.card_name)
            elif self.zone == 'sideboard':
                for _ in range(self.count):
                    deck.add_sideboard_card(self.card_name)
            elif self.zone == 'commander':
                deck.set_commander(self.card_name)
            
            self.deck_service.save_deck(deck)
            return True
        except Exception as e:
            logger.error(f"Error undoing remove card: {e}")
            return False
    
    def get_description(self) -> str:
        """Get description."""
        if self.count == 1:
            return f"Remove {self.card_name}"
        return f"Remove {self.count}x {self.card_name}"


class RenameDeckCommand(Command):
    """Command to rename a deck."""
    
    def __init__(self, deck_service, old_name: str, new_name: str):
        """
        Initialize rename deck command.
        
        Args:
            deck_service: DeckService instance
            old_name: Current deck name
            new_name: New deck name
        """
        self.deck_service = deck_service
        self.old_name = old_name
        self.new_name = new_name
    
    def execute(self) -> bool:
        """Rename deck."""
        try:
            deck = self.deck_service.get_deck(self.old_name)
            if not deck:
                return False
            
            deck.name = self.new_name
            self.deck_service.delete_deck(self.old_name)
            self.deck_service.save_deck(deck)
            return True
        except Exception as e:
            logger.error(f"Error renaming deck: {e}")
            return False
    
    def undo(self) -> bool:
        """Restore old name."""
        try:
            deck = self.deck_service.get_deck(self.new_name)
            if not deck:
                return False
            
            deck.name = self.old_name
            self.deck_service.delete_deck(self.new_name)
            self.deck_service.save_deck(deck)
            return True
        except Exception as e:
            logger.error(f"Error undoing rename: {e}")
            return False
    
    def get_description(self) -> str:
        """Get description."""
        return f"Rename '{self.old_name}' to '{self.new_name}'"


class CommandHistory(QObject):
    """
    Manages command history for undo/redo.
    """
    
    # Signals
    can_undo_changed = Signal(bool)
    can_redo_changed = Signal(bool)
    history_changed = Signal()
    
    def __init__(self, max_history: int = 50):
        """
        Initialize command history.
        
        Args:
            max_history: Maximum number of commands to keep
        """
        super().__init__()
        
        self.max_history = max_history
        self.undo_stack: list[Command] = []
        self.redo_stack: list[Command] = []
    
    def execute(self, command: Command) -> bool:
        """
        Execute a command and add to history.
        
        Args:
            command: Command to execute
            
        Returns:
            True if successful
        """
        if command.execute():
            # Add to undo stack
            self.undo_stack.append(command)
            
            # Clear redo stack (new action invalidates redo)
            self.redo_stack.clear()
            
            # Limit history size
            if len(self.undo_stack) > self.max_history:
                self.undo_stack.pop(0)
            
            self._emit_signals()
            logger.debug(f"Executed: {command.get_description()}")
            return True
        
        return False
    
    def undo(self) -> bool:
        """
        Undo the last command.
        
        Returns:
            True if successful
        """
        if not self.can_undo():
            return False
        
        command = self.undo_stack.pop()
        
        if command.undo():
            # Add to redo stack
            self.redo_stack.append(command)
            
            self._emit_signals()
            logger.debug(f"Undid: {command.get_description()}")
            return True
        else:
            # Put back on undo stack if undo failed
            self.undo_stack.append(command)
            return False
    
    def redo(self) -> bool:
        """
        Redo the last undone command.
        
        Returns:
            True if successful
        """
        if not self.can_redo():
            return False
        
        command = self.redo_stack.pop()
        
        if command.execute():
            # Add back to undo stack
            self.undo_stack.append(command)
            
            self._emit_signals()
            logger.debug(f"Redid: {command.get_description()}")
            return True
        else:
            # Put back on redo stack if redo failed
            self.redo_stack.append(command)
            return False
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self.redo_stack) > 0
    
    def get_undo_text(self) -> Optional[str]:
        """Get description of next undo action."""
        if self.can_undo():
            return self.undo_stack[-1].get_description()
        return None
    
    def get_redo_text(self) -> Optional[str]:
        """Get description of next redo action."""
        if self.can_redo():
            return self.redo_stack[-1].get_description()
        return None
    
    def clear(self):
        """Clear all history."""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._emit_signals()
    
    def _emit_signals(self):
        """Emit state change signals."""
        self.can_undo_changed.emit(self.can_undo())
        self.can_redo_changed.emit(self.can_redo())
        self.history_changed.emit()
