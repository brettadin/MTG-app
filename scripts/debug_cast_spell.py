import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.game.game_engine import GameEngine, GamePhase, GameStep, Zone, Card

eng = GameEngine(num_players=2)
player1_deck = [Card(f'Card{i}', ['Creature']) for i in range(60)]
player2_deck = [Card(f'Card{i}', ['Creature']) for i in range(60)]
eng.add_player('A', player1_deck)
eng.add_player('B', player2_deck)
eng.start_game()
eng.current_phase = GamePhase.PRECOMBAT_MAIN
eng.current_step = GameStep.MAIN
creature = Card('Bear', ['Creature'])
creature.power = 2
creature.toughness = 2
creature.damage = 0
creature.controller = 0
creature.zone = Zone.BATTLEFIELD
eng.players[0].battlefield.append(creature)
bolt = Card('Lightning Bolt', ['Instant'])
bolt.controller = 0
bolt.zone = Zone.HAND
eng.players[0].hand.append(bolt)
print('Before cast, priority_player_index=', eng.priority_player_index, 'active_player=', eng.active_player_index)

def deal_damage(game_engine):
    creature.damage += 3
    print('deal_damage called')

eng.cast_spell(bolt, resolve_effect=deal_damage)
print('After cast, priority_player_index=', eng.priority_player_index, 'stack size=', len(eng.stack_manager.stack))
eng.pass_priority()
print('After pass_priority, priority_player_index=', eng.priority_player_index, 'stack size=', len(eng.stack_manager.stack), 'creature damage=', creature.damage)
