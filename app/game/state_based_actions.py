"""
State-based actions system.
Implements all MTG state-based actions that are checked continuously.
"""

import logging
from typing import List, Set
from enum import Enum

logger = logging.getLogger(__name__)


class StateBasedAction(Enum):
    """Types of state-based actions."""
    # Player-based
    PLAYER_LOSES_AT_0_LIFE = "player_loses_at_0_life"
    PLAYER_LOSES_WITH_10_POISON = "player_loses_with_10_poison"
    PLAYER_LOSES_TO_DRAWING_FROM_EMPTY_LIBRARY = "player_loses_to_drawing_from_empty_library"
    
    # Creature-based
    CREATURE_WITH_LETHAL_DAMAGE = "creature_with_lethal_damage"
    CREATURE_WITH_0_TOUGHNESS = "creature_with_0_toughness"
    CREATURE_WITH_DEATHTOUCH_DAMAGE = "creature_with_deathtouch_damage"
    
    # Planeswalker-based
    PLANESWALKER_WITH_0_LOYALTY = "planeswalker_with_0_loyalty"
    
    # Legend rule
    LEGENDARY_RULE = "legendary_rule"
    
    # Token in graveyard/exile
    TOKEN_IN_WRONG_ZONE = "token_in_wrong_zone"
    
    # Auras
    AURA_NOT_ATTACHED = "aura_not_attached"
    AURA_ILLEGAL_ATTACHMENT = "aura_illegal_attachment"
    
    # Equipment
    EQUIPMENT_ON_ILLEGAL_CREATURE = "equipment_on_illegal_creature"
    
    # +1/+1 and -1/-1 counters
    COUNTERS_CANCEL = "counters_cancel"
    
    # Copy tokens
    COPY_TOKEN_EFFECT_ENDS = "copy_token_effect_ends"


class StateBasedActionsChecker:
    """
    Checks and performs state-based actions.
    
    State-based actions are checked whenever a player would receive priority
    and are performed simultaneously.
    """
    
    def __init__(self, game_engine):
        """
        Initialize SBA checker.
        
        Args:
            game_engine: Reference to main GameEngine
        """
        self.game_engine = game_engine
        self.actions_performed: List[str] = []
        logger.info("StateBasedActionsChecker initialized")
    
    def check_all(self) -> bool:
        """
        Check all state-based actions.
        
        Returns:
            True if any actions were performed
        """
        self.actions_performed.clear()
        actions_taken = False
        
        # Keep checking until no more actions are performed
        while True:
            round_actions = self._check_round()
            if not round_actions:
                break
            actions_taken = True
        
        if self.actions_performed:
            logger.info(f"SBAs performed: {len(self.actions_performed)}")
        
        return actions_taken
    
    def _check_round(self) -> bool:
        """
        Perform one round of SBA checks.
        
        Returns:
            True if any actions were performed
        """
        actions_this_round = False
        
        # Player-based SBAs
        actions_this_round |= self._check_player_life()
        actions_this_round |= self._check_poison_counters()
        actions_this_round |= self._check_empty_library()
        
        # Creature-based SBAs
        actions_this_round |= self._check_lethal_damage()
        actions_this_round |= self._check_zero_toughness()
        actions_this_round |= self._check_deathtouch_damage()
        
        # Planeswalker SBAs
        actions_this_round |= self._check_planeswalker_loyalty()
        
        # Legend rule
        actions_this_round |= self._check_legend_rule()
        
        # Tokens
        actions_this_round |= self._check_tokens_in_wrong_zones()
        
        # Auras and Equipment
        actions_this_round |= self._check_auras()
        actions_this_round |= self._check_equipment()
        
        # Counter interactions
        actions_this_round |= self._check_counter_cancellation()
        
        return actions_this_round
    
    def _check_player_life(self) -> bool:
        """Check if any players have 0 or less life."""
        actions = False
        
        for player in self.game_engine.players:
            if player.life <= 0 and not player.lost_game:
                self._log_action(f"Player {player.player_id} loses (life: {player.life})")
                player.lost_game = True
                actions = True
        
        return actions
    
    def _check_poison_counters(self) -> bool:
        """Check if any players have 10+ poison counters."""
        actions = False
        
        for player in self.game_engine.players:
            if hasattr(player, 'poison_counters') and player.poison_counters >= 10 and not player.lost_game:
                self._log_action(f"Player {player.player_id} loses (poison: {player.poison_counters})")
                player.lost_game = True
                actions = True
        
        return actions
    
    def _check_empty_library(self) -> bool:
        """Check if any players tried to draw from empty library."""
        # This is checked when draw happens, not as SBA
        # But we can check if library is empty and player has lost
        return False
    
    def _check_lethal_damage(self) -> bool:
        """Check creatures with lethal damage."""
        actions = False
        
        for player in self.game_engine.players:
            for permanent in player.battlefield[:]:
                if not self._is_creature(permanent):
                    continue
                
                damage = getattr(permanent, 'damage', 0)
                toughness = getattr(permanent, 'toughness', 0)
                
                if damage >= toughness > 0:
                    self._log_action(f"{permanent.name} dies (lethal damage: {damage}/{toughness})")
                    self.game_engine.move_to_graveyard(permanent)
                    actions = True
        
        return actions
    
    def _check_zero_toughness(self) -> bool:
        """Check creatures with 0 or less toughness."""
        actions = False
        
        for player in self.game_engine.players:
            for permanent in player.battlefield[:]:
                if not self._is_creature(permanent):
                    continue
                
                toughness = getattr(permanent, 'toughness', 0)
                
                if toughness <= 0:
                    self._log_action(f"{permanent.name} dies (0 toughness)")
                    self.game_engine.move_to_graveyard(permanent)
                    actions = True
        
        return actions
    
    def _check_deathtouch_damage(self) -> bool:
        """Check creatures with deathtouch damage."""
        actions = False
        
        for player in self.game_engine.players:
            for permanent in player.battlefield[:]:
                if not self._is_creature(permanent):
                    continue
                
                if hasattr(permanent, 'has_deathtouch_damage') and permanent.has_deathtouch_damage:
                    self._log_action(f"{permanent.name} dies (deathtouch)")
                    self.game_engine.move_to_graveyard(permanent)
                    actions = True
        
        return actions
    
    def _check_planeswalker_loyalty(self) -> bool:
        """Check planeswalkers with 0 loyalty."""
        actions = False
        
        for player in self.game_engine.players:
            for permanent in player.battlefield[:]:
                if not self._is_planeswalker(permanent):
                    continue
                
                loyalty = getattr(permanent, 'loyalty', 0)
                
                if loyalty <= 0:
                    self._log_action(f"{permanent.name} dies (0 loyalty)")
                    self.game_engine.move_to_graveyard(permanent)
                    actions = True
        
        return actions
    
    def _check_legend_rule(self) -> bool:
        """Check legendary permanent rule."""
        actions = False
        
        for player in self.game_engine.players:
            # Group legendaries by name
            legendaries = {}
            
            for permanent in player.battlefield:
                if not self._is_legendary(permanent):
                    continue
                
                name = permanent.name
                if name not in legendaries:
                    legendaries[name] = []
                legendaries[name].append(permanent)
            
            # If multiple copies, player chooses one to keep
            for name, copies in legendaries.items():
                if len(copies) > 1:
                    # For now, keep the first one
                    to_remove = copies[1:]
                    for permanent in to_remove:
                        self._log_action(f"{permanent.name} put into graveyard (legend rule)")
                        self.game_engine.move_to_graveyard(permanent)
                        actions = True
        
        return actions
    
    def _check_tokens_in_wrong_zones(self) -> bool:
        """Remove tokens from zones other than battlefield."""
        actions = False
        
        for player in self.game_engine.players:
            # Check graveyard
            for card in player.graveyard[:]:
                if getattr(card, 'is_token', False):
                    self._log_action(f"Token {card.name} ceases to exist (in graveyard)")
                    player.graveyard.remove(card)
                    actions = True
            
            # Check exile
            for card in player.exile[:]:
                if getattr(card, 'is_token', False):
                    self._log_action(f"Token {card.name} ceases to exist (in exile)")
                    player.exile.remove(card)
                    actions = True
            
            # Check hand (shouldn't happen but check anyway)
            for card in player.hand[:]:
                if getattr(card, 'is_token', False):
                    self._log_action(f"Token {card.name} ceases to exist (in hand)")
                    player.hand.remove(card)
                    actions = True
        
        return actions
    
    def _check_auras(self) -> bool:
        """Check auras for illegal attachments."""
        actions = False
        
        for player in self.game_engine.players:
            for permanent in player.battlefield[:]:
                if not self._is_aura(permanent):
                    continue
                
                # Aura must be attached to something
                attached_to = getattr(permanent, 'attached_to', None)
                
                if not attached_to:
                    self._log_action(f"{permanent.name} put into graveyard (not attached)")
                    self.game_engine.move_to_graveyard(permanent)
                    actions = True
                    continue
                
                # Check if attachment is still legal
                if not self._is_legal_attachment(permanent, attached_to):
                    self._log_action(f"{permanent.name} put into graveyard (illegal attachment)")
                    self.game_engine.move_to_graveyard(permanent)
                    actions = True
        
        return actions
    
    def _check_equipment(self) -> bool:
        """Check equipment for illegal attachments."""
        actions = False
        
        for player in self.game_engine.players:
            for permanent in player.battlefield:
                if not self._is_equipment(permanent):
                    continue
                
                attached_to = getattr(permanent, 'attached_to', None)
                
                if attached_to:
                    # Equipment must be attached to creature you control
                    if not self._is_creature(attached_to):
                        permanent.attached_to = None
                        self._log_action(f"{permanent.name} unattached (not on creature)")
                        actions = True
                    elif attached_to.controller != permanent.controller:
                        permanent.attached_to = None
                        self._log_action(f"{permanent.name} unattached (not your creature)")
                        actions = True
        
        return actions
    
    def _check_counter_cancellation(self) -> bool:
        """Check for +1/+1 and -1/-1 counter cancellation."""
        actions = False
        
        for player in self.game_engine.players:
            for permanent in player.battlefield:
                plus_counters = getattr(permanent, 'plus_counters', 0)
                minus_counters = getattr(permanent, 'minus_counters', 0)
                
                if plus_counters > 0 and minus_counters > 0:
                    cancel = min(plus_counters, minus_counters)
                    permanent.plus_counters -= cancel
                    permanent.minus_counters -= cancel
                    
                    if cancel > 0:
                        self._log_action(
                            f"{permanent.name}: {cancel} +1/+1 and -1/-1 counters removed"
                        )
                        actions = True
        
        return actions
    
    def _is_creature(self, card) -> bool:
        """Check if card is a creature."""
        # Some tests/legacy code use `types` list instead of a type_line string
        type_line = getattr(card, 'type_line', '') or ''
        if 'Creature' in type_line:
            return True
        types_list = getattr(card, 'types', [])
        if isinstance(types_list, (list, tuple)) and 'Creature' in types_list:
            return True
        return False
    
    def _is_planeswalker(self, card) -> bool:
        """Check if card is a planeswalker."""
        type_line = getattr(card, 'type_line', '') or ''
        if 'Planeswalker' in type_line:
            return True
        types_list = getattr(card, 'types', [])
        if isinstance(types_list, (list, tuple)) and 'Planeswalker' in types_list:
            return True
        return False
    
    def _is_legendary(self, card) -> bool:
        """Check if card is legendary."""
        type_line = getattr(card, 'type_line', '') or ''
        if 'Legendary' in type_line:
            return True
        types_list = getattr(card, 'types', [])
        if isinstance(types_list, (list, tuple)) and 'Legendary' in types_list:
            return True
        return False
    
    def _is_aura(self, card) -> bool:
        """Check if card is an aura."""
        type_line = getattr(card, 'type_line', '') or ''
        return 'Enchantment' in type_line and 'Aura' in type_line
    
    def _is_equipment(self, card) -> bool:
        """Check if card is equipment."""
        type_line = getattr(card, 'type_line', '') or ''
        return 'Artifact' in type_line and 'Equipment' in type_line
    
    def _is_legal_attachment(self, aura, target) -> bool:
        """Check if aura can legally attach to target."""
        # Simplified check - in real game would check aura's enchant ability
        oracle_text = getattr(aura, 'oracle_text', '').lower()
        
        if 'enchant creature' in oracle_text:
            return self._is_creature(target)
        elif 'enchant player' in oracle_text:
            return hasattr(target, 'player_id')
        elif 'enchant land' in oracle_text:
            return 'Land' in getattr(target, 'type_line', '')
        
        # Default to true if can't determine
        return True
    
    def _log_action(self, message: str):
        """Log a state-based action."""
        self.actions_performed.append(message)
        logger.info(f"SBA: {message}")
        self.game_engine.log_event(f"SBA: {message}")
