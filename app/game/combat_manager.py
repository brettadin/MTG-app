"""
Combat phase simulator with declare attackers, blockers, and damage assignment.

This module handles all combat-related mechanics including attacking, blocking,
damage assignment, first strike, double strike, trample, and combat tricks.

Classes:
    CombatManager: Manages entire combat phase
    Attacker: Attacking creature with blockers
    Blocker: Blocking creature with damage assignment
    CombatDamage: Damage assignment tracker

Features:
    - Declare attackers with legal attack validation
    - Declare blockers with legal block validation
    - Damage assignment (normal and first strike)
    - Combat abilities (first strike, double strike, trample, flying, etc.)
    - Damage prevention and replacement
    - Combat triggers
    - Removal of dead creatures

Usage:
    combat = CombatManager(game_engine)
    combat.declare_attacker(creature, defending_player)
    combat.declare_blocker(blocker, attacker)
    combat.assign_combat_damage()
"""

import logging
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class CombatAbility(Enum):
    """Combat-relevant abilities."""
    FLYING = "flying"
    REACH = "reach"
    FIRST_STRIKE = "first_strike"
    DOUBLE_STRIKE = "double_strike"
    TRAMPLE = "trample"
    VIGILANCE = "vigilance"
    MENACE = "menace"
    DEATHTOUCH = "deathtouch"
    LIFELINK = "lifelink"
    DEFENDER = "defender"


@dataclass
class Attacker:
    """Represents an attacking creature."""
    creature: object  # Card object
    defending_player: int  # Player ID being attacked
    blockers: List[object] = field(default_factory=list)
    damage_dealt: int = 0
    
    def is_blocked(self) -> bool:
        """Check if creature is blocked."""
        return len(self.blockers) > 0
    
    def is_unblocked(self) -> bool:
        """Check if creature is unblocked."""
        return len(self.blockers) == 0


@dataclass
class Blocker:
    """Represents a blocking creature."""
    creature: object  # Card object
    blocking: object  # Attacker creature
    damage_dealt: int = 0
    damage_received: int = 0


@dataclass
class CombatDamage:
    """Tracks combat damage assignment."""
    source: object  # Creature dealing damage
    target: object  # Creature or player receiving damage
    amount: int
    is_combat_damage: bool = True
    prevented: bool = False


class CombatManager:
    """
    Manages the combat phase including attackers, blockers, and damage.
    
    Handles all combat rules including:
    - Legal attack/block validation
    - Combat abilities (flying, first strike, etc.)
    - Damage assignment
    - Combat tricks and removal
    """
    
    def __init__(self, game_engine):
        """
        Initialize combat manager.
        
        Args:
            game_engine: Reference to main GameEngine
        """
        self.game_engine = game_engine
        self.attackers: List[Attacker] = []
        self.blockers: List[Blocker] = []
        self.combat_damage: List[CombatDamage] = []
        logger.info("CombatManager initialized")
    
    def start_combat(self):
        """Start combat phase - clear previous combat data."""
        self.attackers.clear()
        self.blockers.clear()
        self.combat_damage.clear()
        self.game_engine.log_event("Combat begins")
    
    def can_attack(self, creature, defending_player_id: int) -> Tuple[bool, str]:
        """
        Check if a creature can attack.
        
        Args:
            creature: Creature card to check
            defending_player_id: Player being attacked
            
        Returns:
            Tuple of (can_attack, reason)
        """
        # Must be a creature
        if not creature.is_creature():
            return False, "Not a creature"
        
        # Must be controlled by active player
        if creature.controller != self.game_engine.active_player_index:
            return False, "Not controlled by active player"
        
        # Must be on battlefield
        from app.game.game_engine import Zone
        if creature.zone != Zone.BATTLEFIELD:
            return False, "Not on battlefield"
        
        # Must be untapped
        if creature.tapped:
            return False, "Already tapped"
        
        # Can't have summoning sickness (unless haste)
        if creature.summoning_sick and "haste" not in creature.oracle_text.lower():
            return False, "Summoning sickness"
        
        # Can't have defender
        if self._has_ability(creature, CombatAbility.DEFENDER):
            return False, "Has defender"
        
        # Can't attack own player
        if defending_player_id == creature.controller:
            return False, "Cannot attack yourself"
        
        return True, "OK"
    
    def declare_attacker(self, creature, defending_player_id: int) -> bool:
        """
        Declare a creature as an attacker.
        
        Args:
            creature: Creature to declare as attacker
            defending_player_id: Player being attacked
            
        Returns:
            True if successfully declared
        """
        can_attack, reason = self.can_attack(creature, defending_player_id)
        if not can_attack:
            logger.warning(f"Cannot attack: {reason}")
            return False
        
        # Tap the creature (unless vigilance)
        if not self._has_ability(creature, CombatAbility.VIGILANCE):
            creature.tapped = True
        
        # Add to attackers
        attacker = Attacker(
            creature=creature,
            defending_player=defending_player_id
        )
        self.attackers.append(attacker)
        
        self.game_engine.log_event(
            f"{creature.name} attacks player {defending_player_id}"
        )
        
        return True
    
    def can_block(self, blocker, attacker) -> Tuple[bool, str]:
        """
        Check if a creature can block an attacker.
        
        Args:
            blocker: Creature attempting to block
            attacker: Attacking creature
            
        Returns:
            Tuple of (can_block, reason)
        """
        # Must be a creature
        if not blocker.is_creature():
            return False, "Not a creature"
        
        # Must be untapped
        if blocker.tapped:
            return False, "Already tapped"
        
        # Find the attacker object
        attacker_obj = None
        for att in self.attackers:
            if att.creature == attacker:
                attacker_obj = att
                break
        
        if not attacker_obj:
            return False, "Creature not attacking"
        
        # Must be controlled by defending player
        if blocker.controller != attacker_obj.defending_player:
            return False, "Not controlled by defending player"
        
        # Flying/reach check
        if self._has_ability(attacker, CombatAbility.FLYING):
            if not (self._has_ability(blocker, CombatAbility.FLYING) or
                   self._has_ability(blocker, CombatAbility.REACH)):
                return False, "Cannot block flying"
        
        return True, "OK"
    
    def declare_blocker(self, blocker, attacker) -> bool:
        """
        Declare a creature as a blocker.
        
        Args:
            blocker: Creature blocking
            attacker: Attacking creature being blocked
            
        Returns:
            True if successfully declared
        """
        can_block, reason = self.can_block(blocker, attacker)
        if not can_block:
            logger.warning(f"Cannot block: {reason}")
            return False
        
        # Find attacker object
        attacker_obj = None
        for att in self.attackers:
            if att.creature == attacker:
                attacker_obj = att
                break
        
        if not attacker_obj:
            return False
        
        # Add blocker to attacker's blocker list
        attacker_obj.blockers.append(blocker)
        
        # Create blocker object
        blocker_obj = Blocker(
            creature=blocker,
            blocking=attacker
        )
        self.blockers.append(blocker_obj)
        
        self.game_engine.log_event(
            f"{blocker.name} blocks {attacker.name}"
        )
        
        return True
    
    def check_menace(self) -> bool:
        """
        Check menace requirement (must be blocked by 2+ creatures).
        
        Returns:
            True if all menace requirements are met
        """
        for attacker in self.attackers:
            if self._has_ability(attacker.creature, CombatAbility.MENACE):
                if attacker.is_blocked() and len(attacker.blockers) < 2:
                    self.game_engine.log_event(
                        f"{attacker.creature.name} has menace - illegal block!"
                    )
                    return False
        return True
    
    def assign_first_strike_damage(self):
        """Assign first strike/double strike damage."""
        self.game_engine.log_event("First strike damage")
        
        first_strikers = []
        
        # Find all first strike/double strike creatures
        for attacker in self.attackers:
            if (self._has_ability(attacker.creature, CombatAbility.FIRST_STRIKE) or
                self._has_ability(attacker.creature, CombatAbility.DOUBLE_STRIKE)):
                first_strikers.append(('attacker', attacker))
        
        for blocker in self.blockers:
            if (self._has_ability(blocker.creature, CombatAbility.FIRST_STRIKE) or
                self._has_ability(blocker.creature, CombatAbility.DOUBLE_STRIKE)):
                first_strikers.append(('blocker', blocker))
        
        # Assign damage for first strikers
        self._assign_damage_for_creatures(first_strikers, is_first_strike=True)
        
        # Apply damage
        self._apply_damage()
        
        # Remove dead creatures (won't deal normal damage)
        self._remove_dead_creatures()
    
    def assign_normal_damage(self):
        """Assign normal combat damage."""
        self.game_engine.log_event("Combat damage")
        
        # All creatures deal damage (except those that only have first strike)
        all_combatants = []
        
        for attacker in self.attackers:
            # Skip if only first strike (not double strike)
            if (self._has_ability(attacker.creature, CombatAbility.FIRST_STRIKE) and
                not self._has_ability(attacker.creature, CombatAbility.DOUBLE_STRIKE)):
                continue
            all_combatants.append(('attacker', attacker))
        
        for blocker in self.blockers:
            # Skip if only first strike (not double strike)
            if (self._has_ability(blocker.creature, CombatAbility.FIRST_STRIKE) and
                not self._has_ability(blocker.creature, CombatAbility.DOUBLE_STRIKE)):
                continue
            all_combatants.append(('blocker', blocker))
        
        # Assign damage
        self._assign_damage_for_creatures(all_combatants, is_first_strike=False)
        
        # Apply damage
        self._apply_damage()
        
        # Remove dead creatures
        self._remove_dead_creatures()
    
    def _assign_damage_for_creatures(self, combatants: List[Tuple], is_first_strike: bool):
        """
        Assign damage for a list of creatures.
        
        Args:
            combatants: List of (type, creature) tuples
            is_first_strike: Whether this is first strike damage
        """
        for combatant_type, combatant in combatants:
            if combatant_type == 'attacker':
                self._assign_attacker_damage(combatant)
            else:
                self._assign_blocker_damage(combatant)
    
    def _assign_attacker_damage(self, attacker: Attacker):
        """
        Assign damage for an attacking creature.
        
        Args:
            attacker: Attacker object
        """
        power = attacker.creature.power or 0
        
        if attacker.is_unblocked():
            # Deal damage to defending player
            defending_player = self.game_engine.players[attacker.defending_player]
            damage = CombatDamage(
                source=attacker.creature,
                target=defending_player,
                amount=power
            )
            self.combat_damage.append(damage)
            attacker.damage_dealt = power
        
        else:
            # Deal damage to blockers
            has_trample = self._has_ability(attacker.creature, CombatAbility.TRAMPLE)
            
            # Active player assigns damage order among blockers
            damage_remaining = power
            
            for blocker in attacker.blockers:
                if damage_remaining <= 0:
                    break
                
                blocker_toughness = blocker.toughness or 0
                # If only a single blocker, special rules apply: if attacker has trample,
                # assign only enough to be lethal to blocker and pass the rest to player;
                # otherwise (no trample), attacker may assign all damage to the single blocker.
                if len(attacker.blockers) == 1:
                    if has_trample:
                        damage_to_blocker = min(damage_remaining, blocker_toughness)
                    else:
                        damage_to_blocker = damage_remaining
                else:
                    damage_to_blocker = min(damage_remaining, blocker_toughness)
                
                # Deathtouch only needs 1 damage to be lethal
                if self._has_ability(attacker.creature, CombatAbility.DEATHTOUCH):
                    damage_to_blocker = min(1, damage_remaining)
                
                damage = CombatDamage(
                    source=attacker.creature,
                    target=blocker,
                    amount=damage_to_blocker
                )
                self.combat_damage.append(damage)
                damage_remaining -= damage_to_blocker
            
            # Trample damage to player
            if has_trample and damage_remaining > 0:
                defending_player = self.game_engine.players[attacker.defending_player]
                damage = CombatDamage(
                    source=attacker.creature,
                    target=defending_player,
                    amount=damage_remaining
                )
                self.combat_damage.append(damage)
            
            attacker.damage_dealt = power
    
    def _assign_blocker_damage(self, blocker: Blocker):
        """
        Assign damage for a blocking creature.
        
        Args:
            blocker: Blocker object
        """
        power = blocker.creature.power or 0
        
        # Blocker deals damage to attacker
        damage = CombatDamage(
            source=blocker.creature,
            target=blocker.blocking,
            amount=power
        )
        self.combat_damage.append(damage)
        blocker.damage_dealt = power
    
    def _apply_damage(self):
        """Apply all queued combat damage."""
        for damage_obj in self.combat_damage:
            if damage_obj.prevented:
                continue
            
            # Damage to player
            if hasattr(damage_obj.target, 'life'):
                damage_obj.target.life -= damage_obj.amount
                
                # Lifelink
                if self._has_ability(damage_obj.source, CombatAbility.LIFELINK):
                    controller = self.game_engine.players[damage_obj.source.controller]
                    controller.life += damage_obj.amount
                    self.game_engine.log_event(
                        f"{damage_obj.source.name} lifelink: +{damage_obj.amount} life"
                    )
                
                self.game_engine.log_event(
                    f"{damage_obj.source.name} deals {damage_obj.amount} damage to player {damage_obj.target.player_id}"
                )
            
            # Damage to creature
            elif hasattr(damage_obj.target, 'damage'):
                damage_obj.target.damage += damage_obj.amount
                
                # Lifelink
                if self._has_ability(damage_obj.source, CombatAbility.LIFELINK):
                    controller = self.game_engine.players[damage_obj.source.controller]
                    controller.life += damage_obj.amount
                
                self.game_engine.log_event(
                    f"{damage_obj.source.name} deals {damage_obj.amount} damage to {damage_obj.target.name}"
                )
        
        # Clear damage queue
        self.combat_damage.clear()
    
    def _remove_dead_creatures(self):
        """Remove creatures that died from combat damage."""
        # Check all creatures for lethal damage
        for player in self.game_engine.players:
            for creature in player.battlefield[:]:
                if not creature.is_creature():
                    continue
                
                toughness = creature.toughness or 0
                
                # Lethal damage
                if creature.damage >= toughness:
                    self.game_engine.move_to_graveyard(creature)
                
                # Deathtouch (any damage is lethal)
                elif creature.damage > 0:
                    # Check if any damage source had deathtouch
                    for damage_obj in self.combat_damage:
                        if (damage_obj.target == creature and
                            self._has_ability(damage_obj.source, CombatAbility.DEATHTOUCH)):
                            self.game_engine.move_to_graveyard(creature)
                            break
    
    def end_combat(self):
        """End combat phase - clean up."""
        self.game_engine.log_event("Combat ends")
        
        # Clear combat data
        self.attackers.clear()
        self.blockers.clear()
        self.combat_damage.clear()
    
    def _has_ability(self, creature, ability: CombatAbility) -> bool:
        """
        Check if a creature has a combat ability.
        
        Args:
            creature: Creature to check
            ability: CombatAbility to check for
            
        Returns:
            True if creature has the ability
        """
        if not hasattr(creature, 'oracle_text'):
            return False
        
        text = creature.oracle_text.lower()
        ability_name = ability.value.replace('_', ' ')
        
        return ability_name in text
    
    def get_combat_summary(self) -> Dict:
        """
        Get summary of current combat state.
        
        Returns:
            Dictionary with combat information
        """
        return {
            'num_attackers': len(self.attackers),
            'num_blockers': len(self.blockers),
            'attackers': [
                {
                    'name': att.creature.name,
                    'power': att.creature.power,
                    'defending_player': att.defending_player,
                    'blocked': att.is_blocked(),
                    'num_blockers': len(att.blockers)
                }
                for att in self.attackers
            ],
            'blockers': [
                {
                    'name': blk.creature.name,
                    'power': blk.creature.power,
                    'blocking': blk.blocking.name
                }
                for blk in self.blockers
            ]
        }
