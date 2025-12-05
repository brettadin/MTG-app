"""
Mana pool and mana ability system for MTG.
"""

import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ManaType(Enum):
    """Types of mana."""
    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    COLORLESS = "C"
    GENERIC = "X"  # Can be paid with any color or colorless


class ManaPool:
    """
    A player's mana pool.
    
    Stores floating mana that empties between steps.
    """
    
    def __init__(self, player_id: int):
        """
        Initialize mana pool.
        
        Args:
            player_id: Owner of this mana pool
        """
        self.player_id = player_id
        self.mana: Dict[ManaType, int] = {
            ManaType.WHITE: 0,
            ManaType.BLUE: 0,
            ManaType.BLACK: 0,
            ManaType.RED: 0,
            ManaType.GREEN: 0,
            ManaType.COLORLESS: 0
        }
        logger.info(f"ManaPool initialized for player {player_id}")
    
    def add_mana(self, mana_type: ManaType, amount: int = 1):
        """
        Add mana to pool.
        
        Args:
            mana_type: Type of mana to add
            amount: Amount to add
        """
        if mana_type == ManaType.GENERIC:
            # Generic mana can't be added, it's only for costs
            logger.warning("Cannot add generic mana to pool")
            return
        
        self.mana[mana_type] = self.mana.get(mana_type, 0) + amount
        logger.info(f"Player {self.player_id} adds {amount} {mana_type.value}")
    
    def remove_mana(self, mana_type: ManaType, amount: int = 1) -> bool:
        """
        Remove mana from pool.
        
        Args:
            mana_type: Type of mana to remove
            amount: Amount to remove
            
        Returns:
            True if successful
        """
        if self.mana.get(mana_type, 0) < amount:
            return False
        
        self.mana[mana_type] -= amount
        logger.info(f"Player {self.player_id} spends {amount} {mana_type.value}")
        return True
    
    def has_mana(self, mana_type: ManaType, amount: int = 1) -> bool:
        """
        Check if pool has enough mana.
        
        Args:
            mana_type: Type of mana to check
            amount: Amount needed
            
        Returns:
            True if enough mana available
        """
        return self.mana.get(mana_type, 0) >= amount
    
    def can_pay_cost(self, cost: str) -> bool:
        """
        Check if can pay mana cost.
        
        Args:
            cost: Mana cost string (e.g., "2UU", "WUBRG")
            
        Returns:
            True if cost can be paid
        """
        required_mana = self._parse_mana_cost(cost)
        
        # Check colored mana requirements
        for mana_type, amount in required_mana.items():
            if mana_type == ManaType.GENERIC:
                continue
            if not self.has_mana(mana_type, amount):
                return False
        
        # Check generic mana requirement
        generic_required = required_mana.get(ManaType.GENERIC, 0)
        total_mana = sum(self.mana.values())
        colored_required = sum(
            amount for mana_type, amount in required_mana.items()
            if mana_type != ManaType.GENERIC
        )
        
        return total_mana >= (colored_required + generic_required)
    
    def pay_cost(self, cost: str) -> bool:
        """
        Pay mana cost from pool.
        
        Args:
            cost: Mana cost string
            
        Returns:
            True if cost was paid
        """
        if not self.can_pay_cost(cost):
            return False
        
        required_mana = self._parse_mana_cost(cost)
        
        # Pay colored mana first
        for mana_type, amount in required_mana.items():
            if mana_type == ManaType.GENERIC:
                continue
            self.remove_mana(mana_type, amount)
        
        # Pay generic mana with any remaining mana
        generic_required = required_mana.get(ManaType.GENERIC, 0)
        paid = 0
        
        for mana_type in [ManaType.WHITE, ManaType.BLUE, ManaType.BLACK, 
                         ManaType.RED, ManaType.GREEN, ManaType.COLORLESS]:
            while self.mana[mana_type] > 0 and paid < generic_required:
                self.remove_mana(mana_type, 1)
                paid += 1
        
        logger.info(f"Player {self.player_id} paid cost: {cost}")
        return True
    
    def empty_pool(self):
        """Empty all mana from pool (happens at end of steps)."""
        if any(amount > 0 for amount in self.mana.values()):
            logger.info(f"Player {self.player_id} empties mana pool")
            for mana_type in self.mana:
                self.mana[mana_type] = 0
    
    def get_total_mana(self) -> int:
        """
        Get total mana in pool.
        
        Returns:
            Total mana count
        """
        return sum(self.mana.values())
    
    def _parse_mana_cost(self, cost: str) -> Dict[ManaType, int]:
        """
        Parse mana cost string.
        
        Args:
            cost: Mana cost (e.g., "2UU", "WUBRG", "3")
            
        Returns:
            Dictionary of mana types to amounts
        """
        result: Dict[ManaType, int] = {}
        
        i = 0
        while i < len(cost):
            char = cost[i]
            
            if char.isdigit():
                # Generic mana
                num = ""
                while i < len(cost) and cost[i].isdigit():
                    num += cost[i]
                    i += 1
                result[ManaType.GENERIC] = result.get(ManaType.GENERIC, 0) + int(num)
                continue
            elif char == 'W':
                result[ManaType.WHITE] = result.get(ManaType.WHITE, 0) + 1
            elif char == 'U':
                result[ManaType.BLUE] = result.get(ManaType.BLUE, 0) + 1
            elif char == 'B':
                result[ManaType.BLACK] = result.get(ManaType.BLACK, 0) + 1
            elif char == 'R':
                result[ManaType.RED] = result.get(ManaType.RED, 0) + 1
            elif char == 'G':
                result[ManaType.GREEN] = result.get(ManaType.GREEN, 0) + 1
            elif char == 'C':
                result[ManaType.COLORLESS] = result.get(ManaType.COLORLESS, 0) + 1
            
            i += 1
        
        return result


class ManaAbility:
    """
    A mana ability (doesn't use the stack).
    
    Examples: Tapping lands, Llanowar Elves, mana rocks
    """
    
    def __init__(self, 
                 source_card,
                 mana_produced: List[tuple],  # [(ManaType, amount), ...]
                 tap_cost: bool = True,
                 additional_cost: Optional[str] = None):
        """
        Initialize mana ability.
        
        Args:
            source_card: Card with this ability
            mana_produced: List of (ManaType, amount) tuples
            tap_cost: Whether ability requires tapping
            additional_cost: Additional cost (e.g., "Pay 1 life")
        """
        self.source_card = source_card
        self.mana_produced = mana_produced
        self.tap_cost = tap_cost
        self.additional_cost = additional_cost
    
    def can_activate(self, game_engine) -> bool:
        """
        Check if ability can be activated.
        
        Args:
            game_engine: Reference to game engine
            
        Returns:
            True if ability can be activated
        """
        # Check if card is tapped (if tap cost)
        if self.tap_cost and self.source_card.is_tapped:
            return False
        
        # Check additional costs
        if self.additional_cost:
            # Would need to check specific costs here
            pass
        
        return True
    
    def activate(self, game_engine, mana_pool: ManaPool):
        """
        Activate mana ability.
        
        Args:
            game_engine: Reference to game engine
            mana_pool: Player's mana pool
        """
        if not self.can_activate(game_engine):
            logger.warning(f"Cannot activate mana ability on {self.source_card.name}")
            return
        
        # Pay costs
        if self.tap_cost:
            self.source_card.is_tapped = True
        
        # Add mana to pool
        for mana_type, amount in self.mana_produced:
            mana_pool.add_mana(mana_type, amount)
        
        logger.info(f"Activated mana ability on {self.source_card.name}")


class ManaManager:
    """
    Manages mana pools and mana abilities.
    """
    
    def __init__(self, game_engine):
        """
        Initialize mana manager.
        
        Args:
            game_engine: Reference to main GameEngine
        """
        self.game_engine = game_engine
        self.mana_pools: Dict[int, ManaPool] = {}
        self.mana_abilities: List[ManaAbility] = []
        logger.info("ManaManager initialized")
    
    def create_mana_pool(self, player_id: int) -> ManaPool:
        """
        Create mana pool for player.
        
        Args:
            player_id: Player ID
            
        Returns:
            Created mana pool
        """
        pool = ManaPool(player_id)
        self.mana_pools[player_id] = pool
        return pool
    
    def get_mana_pool(self, player_id: int) -> Optional[ManaPool]:
        """
        Get player's mana pool.
        
        Args:
            player_id: Player ID
            
        Returns:
            Mana pool or None
        """
        return self.mana_pools.get(player_id)
    
    def empty_all_pools(self):
        """Empty all mana pools (at end of step)."""
        for pool in self.mana_pools.values():
            pool.empty_pool()
    
    def register_mana_ability(self, ability: ManaAbility):
        """
        Register a mana ability.
        
        Args:
            ability: Mana ability to register
        """
        self.mana_abilities.append(ability)
        logger.info(f"Registered mana ability for {ability.source_card.name}")
    
    def unregister_mana_ability(self, ability: ManaAbility):
        """
        Unregister a mana ability.
        
        Args:
            ability: Mana ability to remove
        """
        if ability in self.mana_abilities:
            self.mana_abilities.remove(ability)
    
    def get_available_mana_abilities(self, player_id: int) -> List[ManaAbility]:
        """
        Get all mana abilities available to player.
        
        Args:
            player_id: Player ID
            
        Returns:
            List of available mana abilities
        """
        abilities = []
        for ability in self.mana_abilities:
            if ability.source_card.controller == player_id:
                if ability.can_activate(self.game_engine):
                    abilities.append(ability)
        return abilities
    
    def activate_land_for_mana(self, card, player_id: int):
        """
        Activate a land for mana.
        
        Args:
            card: Land card
            player_id: Player activating
        """
        pool = self.get_mana_pool(player_id)
        if not pool:
            return
        
        # Parse land types and add appropriate mana
        # This is simplified - real MTG lands can be more complex
        type_line = card.type_line.lower()
        
        if "plains" in type_line:
            pool.add_mana(ManaType.WHITE)
        if "island" in type_line:
            pool.add_mana(ManaType.BLUE)
        if "swamp" in type_line:
            pool.add_mana(ManaType.BLACK)
        if "mountain" in type_line:
            pool.add_mana(ManaType.RED)
        if "forest" in type_line:
            pool.add_mana(ManaType.GREEN)
        
        card.is_tapped = True
        logger.info(f"Player {player_id} tapped {card.name} for mana")
