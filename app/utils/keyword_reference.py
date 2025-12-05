"""
MTG keyword abilities reference system.
Comprehensive database of keyword abilities with explanations and rulings.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class KeywordAbility:
    """Represents a keyword ability."""
    name: str
    reminder_text: str
    rules_text: str
    introduced: str  # Set code where introduced
    evergreen: bool  # Whether it's evergreen (always in Standard)
    category: str  # combat, evasion, protection, activated, triggered, etc.
    examples: List[str]  # Example card names


class KeywordReference:
    """
    Comprehensive reference for MTG keyword abilities.
    """
    
    def __init__(self):
        """Initialize keyword reference."""
        self.keywords: Dict[str, KeywordAbility] = self._build_keyword_database()
        logger.info(f"Keyword reference initialized with {len(self.keywords)} abilities")
    
    def _build_keyword_database(self) -> Dict[str, KeywordAbility]:
        """Build the complete keyword ability database."""
        keywords = {}
        
        # Evergreen keywords
        keywords['flying'] = KeywordAbility(
            name='Flying',
            reminder_text='This creature can\'t be blocked except by creatures with flying or reach.',
            rules_text='A creature with flying can only be blocked by other creatures with flying or reach.',
            introduced='Alpha',
            evergreen=True,
            category='evasion',
            examples=['Serra Angel', 'Shivan Dragon', 'Delver of Secrets']
        )
        
        keywords['deathtouch'] = KeywordAbility(
            name='Deathtouch',
            reminder_text='Any amount of damage this deals to a creature is enough to destroy it.',
            rules_text='Any amount of damage dealt by a source with deathtouch to a creature is lethal damage.',
            introduced='Future Sight',
            evergreen=True,
            category='combat',
            examples=['Typhoid Rats', 'Vampire Nighthawk', 'Questing Beast']
        )
        
        keywords['first strike'] = KeywordAbility(
            name='First Strike',
            reminder_text='This creature deals combat damage before creatures without first strike.',
            rules_text='Creatures with first strike deal combat damage in the first combat damage step.',
            introduced='Alpha',
            evergreen=True,
            category='combat',
            examples=['Mirran Crusader', 'Adorned Pouncer']
        )
        
        keywords['double strike'] = KeywordAbility(
            name='Double Strike',
            reminder_text='This creature deals both first-strike and regular combat damage.',
            rules_text='A creature with double strike deals combat damage in both damage steps.',
            introduced='Legions',
            evergreen=True,
            category='combat',
            examples=['Boros Charm', 'Swiftblade Vindicator', 'Fiendish Duo']
        )
        
        keywords['haste'] = KeywordAbility(
            name='Haste',
            reminder_text='This creature can attack and tap as soon as it comes under your control.',
            rules_text='Creatures with haste aren\'t affected by summoning sickness.',
            introduced='Alpha',
            evergreen=True,
            category='combat',
            examples=['Lightning Bolt', 'Zurgo Helmsmasher', 'Embercleave']
        )
        
        keywords['hexproof'] = KeywordAbility(
            name='Hexproof',
            reminder_text='This permanent can\'t be the target of spells or abilities your opponents control.',
            rules_text='A permanent with hexproof can\'t be targeted by spells or abilities controlled by opponents.',
            introduced='Duels of the Planeswalkers 2012',
            evergreen=True,
            category='protection',
            examples=['Slippery Bogle', 'Invisible Stalker', 'Thrun, the Last Troll']
        )
        
        keywords['indestructible'] = KeywordAbility(
            name='Indestructible',
            reminder_text='Damage and effects that say "destroy" don\'t destroy this permanent.',
            rules_text='Permanents with indestructible can\'t be destroyed by damage or "destroy" effects.',
            introduced='Darksteel',
            evergreen=True,
            category='protection',
            examples=['Darksteel Colossus', 'Avacyn, Angel of Hope', 'Stuffy Doll']
        )
        
        keywords['lifelink'] = KeywordAbility(
            name='Lifelink',
            reminder_text='Damage dealt by this creature also causes you to gain that much life.',
            rules_text='When a source with lifelink deals damage, its controller gains that much life.',
            introduced='Future Sight',
            evergreen=True,
            category='combat',
            examples=['Vampire Nighthawk', 'Sorin, Vengeful Bloodlord', 'Aetherflux Reservoir']
        )
        
        keywords['menace'] = KeywordAbility(
            name='Menace',
            reminder_text='This creature can\'t be blocked except by two or more creatures.',
            rules_text='A creature with menace can only be blocked by two or more creatures.',
            introduced='Magic Origins',
            evergreen=True,
            category='evasion',
            examples=['Ankle Shanker', 'Goblin Heelcutter', 'Judith, the Scourge Diva']
        )
        
        keywords['reach'] = KeywordAbility(
            name='Reach',
            reminder_text='This creature can block creatures with flying.',
            rules_text='A creature with reach can block creatures with flying.',
            introduced='Future Sight',
            evergreen=True,
            category='combat',
            examples=['Giant Spider', 'Ishkanah, Grafwidow', 'Hornet Queen']
        )
        
        keywords['trample'] = KeywordAbility(
            name='Trample',
            reminder_text='This creature can deal excess combat damage to the player or planeswalker it\'s attacking.',
            rules_text='Trample damage in excess of what\'s needed to destroy blockers is dealt to the defending player.',
            introduced='Alpha',
            evergreen=True,
            category='combat',
            examples=['Ghalta, Primal Hunger', 'Craterhoof Behemoth', 'Questing Beast']
        )
        
        keywords['vigilance'] = KeywordAbility(
            name='Vigilance',
            reminder_text='Attacking doesn\'t cause this creature to tap.',
            rules_text='Creatures with vigilance don\'t tap when attacking.',
            introduced='Champions of Kamigawa',
            evergreen=True,
            category='combat',
            examples=['Serra Angel', 'Gideon, Ally of Zendikar', 'Ajani\'s Pridemate']
        )
        
        keywords['ward'] = KeywordAbility(
            name='Ward',
            reminder_text='Whenever this permanent becomes the target of a spell or ability an opponent controls, counter it unless that player pays the ward cost.',
            rules_text='Ward provides protection similar to hexproof, but opponents can pay the ward cost to target it.',
            introduced='Strixhaven',
            evergreen=True,
            category='protection',
            examples=['Enduring Angel', 'Saryth, the Viper\'s Fang', 'Iymrith, Desert Doom']
        )
        
        # Non-evergreen but common keywords
        keywords['flash'] = KeywordAbility(
            name='Flash',
            reminder_text='You may cast this spell any time you could cast an instant.',
            rules_text='A spell with flash can be cast at instant speed.',
            introduced='Mirage',
            evergreen=False,
            category='timing',
            examples=['Ambush Viper', 'Teferi, Mage of Zhalfir', 'Mystical Tutor']
        )
        
        keywords['defender'] = KeywordAbility(
            name='Defender',
            reminder_text='This creature can\'t attack.',
            rules_text='Creatures with defender can\'t attack.',
            introduced='Champions of Kamigawa',
            evergreen=False,
            category='restriction',
            examples=['Wall of Omens', 'Overgrown Battlement', 'Tree of Redemption']
        )
        
        keywords['prowess'] = KeywordAbility(
            name='Prowess',
            reminder_text='Whenever you cast a noncreature spell, this creature gets +1/+1 until end of turn.',
            rules_text='Prowess triggers whenever you cast a noncreature spell.',
            introduced='Khans of Tarkir',
            evergreen=False,
            category='triggered',
            examples=['Monastery Swiftspear', 'Soulfire Grand Master', 'Sprite Dragon']
        )
        
        keywords['flashback'] = KeywordAbility(
            name='Flashback',
            reminder_text='You may cast this card from your graveyard for its flashback cost. Then exile it.',
            rules_text='A spell with flashback can be cast from the graveyard by paying its flashback cost.',
            introduced='Odyssey',
            evergreen=False,
            category='graveyard',
            examples=['Faithless Looting', 'Ancient Grudge', 'Think Twice']
        )
        
        keywords['kicker'] = KeywordAbility(
            name='Kicker',
            reminder_text='You may pay an additional cost as you cast this spell.',
            rules_text='Kicker is an optional additional cost. If paid, the spell has additional effects.',
            introduced='Invasion',
            evergreen=False,
            category='additional_cost',
            examples=['Rite of Replication', 'Everflowing Chalice', 'Verdurous Gearhulk']
        )
        
        keywords['convoke'] = KeywordAbility(
            name='Convoke',
            reminder_text='Your creatures can help cast this spell. Each creature you tap pays for 1 mana or one mana of that creature\'s color.',
            rules_text='Convoke allows you to tap creatures to help pay for a spell.',
            introduced='Ravnica',
            evergreen=False,
            category='alternative_cost',
            examples=['Chord of Calling', 'Stoke the Flames', 'Venerated Loxodon']
        )
        
        keywords['delve'] = KeywordAbility(
            name='Delve',
            reminder_text='Each card you exile from your graveyard pays for 1 generic mana.',
            rules_text='Delve lets you exile cards from your graveyard to reduce the mana cost.',
            introduced='Future Sight',
            evergreen=False,
            category='alternative_cost',
            examples=['Treasure Cruise', 'Dig Through Time', 'Gurmag Angler']
        )
        
        keywords['cascade'] = KeywordAbility(
            name='Cascade',
            reminder_text='When you cast this spell, exile cards from the top of your library until you exile a nonland card with lesser mana value. You may cast it without paying its mana cost.',
            rules_text='Cascade allows you to cast a cheaper spell for free when casting a spell with cascade.',
            introduced='Alara Reborn',
            evergreen=False,
            category='triggered',
            examples=['Bloodbraid Elf', 'Shardless Agent', 'Maelstrom Wanderer']
        )
        
        keywords['storm'] = KeywordAbility(
            name='Storm',
            reminder_text='When you cast this spell, copy it for each spell cast before it this turn.',
            rules_text='Storm creates a copy of the spell for each other spell cast earlier that turn.',
            introduced='Scourge',
            evergreen=False,
            category='triggered',
            examples=['Grapeshot', 'Tendrils of Agony', 'Empty the Warrens']
        )
        
        keywords['landfall'] = KeywordAbility(
            name='Landfall',
            reminder_text='Whenever a land enters the battlefield under your control, [effect]',
            rules_text='Landfall abilities trigger whenever a land enters under your control.',
            introduced='Zendikar',
            evergreen=False,
            category='triggered',
            examples=['Scute Swarm', 'Lotus Cobra', 'Omnath, Locus of Creation']
        )
        
        keywords['proliferate'] = KeywordAbility(
            name='Proliferate',
            reminder_text='Choose any number of permanents and/or players, then give each another counter of each kind already there.',
            rules_text='Proliferate adds one more of each type of counter already on chosen targets.',
            introduced='Scars of Mirrodin',
            evergreen=False,
            category='triggered',
            examples=['Thrummingbird', 'Flux Channeler', 'Evolution Sage']
        )
        
        keywords['mutate'] = KeywordAbility(
            name='Mutate',
            reminder_text='If you cast this spell for its mutate cost, put it over or under target non-Human creature you own. They mutate into the creature on top plus all abilities underneath.',
            rules_text='Mutate creates a merged creature with all abilities of all merged cards.',
            introduced='Ikoria',
            evergreen=False,
            category='alternative_cost',
            examples=['Auspicious Starrix', 'Gemrazer', 'Illuna, Apex of Wishes']
        )
        
        keywords['foretell'] = KeywordAbility(
            name='Foretell',
            reminder_text='During your turn, you may pay 2 mana and exile this card from your hand face down. Cast it on a later turn for its foretell cost.',
            rules_text='Foretell lets you exile cards for later casting at a reduced cost.',
            introduced='Kaldheim',
            evergreen=False,
            category='alternative_cost',
            examples=['Saw It Coming', 'Behold the Multiverse', 'Doomskar']
        )
        
        return keywords
    
    def search(self, query: str) -> List[KeywordAbility]:
        """
        Search for keyword abilities.
        
        Args:
            query: Search query
            
        Returns:
            List of matching KeywordAbility objects
        """
        query_lower = query.lower()
        matches = []
        
        for keyword in self.keywords.values():
            if (query_lower in keyword.name.lower() or
                query_lower in keyword.reminder_text.lower() or
                query_lower in keyword.rules_text.lower()):
                matches.append(keyword)
        
        return matches
    
    def get_keyword(self, name: str) -> Optional[KeywordAbility]:
        """
        Get a specific keyword ability.
        
        Args:
            name: Keyword name
            
        Returns:
            KeywordAbility object or None
        """
        return self.keywords.get(name.lower())
    
    def get_by_category(self, category: str) -> List[KeywordAbility]:
        """
        Get all keywords in a category.
        
        Args:
            category: Category name
            
        Returns:
            List of KeywordAbility objects
        """
        return [
            kw for kw in self.keywords.values()
            if kw.category == category
        ]
    
    def get_evergreen_keywords(self) -> List[KeywordAbility]:
        """Get all evergreen keywords."""
        return [kw for kw in self.keywords.values() if kw.evergreen]
    
    def get_all_categories(self) -> List[str]:
        """Get list of all categories."""
        categories = set(kw.category for kw in self.keywords.values())
        return sorted(list(categories))
    
    def extract_keywords_from_text(self, oracle_text: str) -> List[str]:
        """
        Extract keyword abilities from oracle text.
        
        Args:
            oracle_text: Card's oracle text
            
        Returns:
            List of keyword names found
        """
        found = []
        text_lower = oracle_text.lower()
        
        for name, keyword in self.keywords.items():
            if keyword.name.lower() in text_lower:
                found.append(keyword.name)
        
        return found
