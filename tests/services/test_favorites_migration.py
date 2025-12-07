import os
import tempfile

from app.data_access.database import Database
from app.services.favorites_service import FavoritesService
from app.services.collection_service import CollectionTracker


def create_db_with_two_cards():
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, 'test_mtg_index.sqlite')

    db = Database(db_path)
    db.create_tables()

    with db.transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO sets(code, name) VALUES (?, ?)", ("SET", "Test Set"))
        cursor.execute(
            """
            INSERT INTO cards(uuid, name, set_code, collector_number, mana_value, mana_cost, colors, color_identity, type_line, rarity, text, oracle_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "uuid-swamp",
                "Swamp",
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
            )
        )
        cursor.execute(
            """
            INSERT INTO cards(uuid, name, set_code, collector_number, mana_value, mana_cost, colors, color_identity, type_line, rarity, text, oracle_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "uuid-mountain",
                "Mountain",
                "SET",
                "2",
                0,
                "",
                "",
                "R",
                "Basic Land — Mountain",
                "common",
                "",
                ""
            )
        )

    db.close()
    return db_path


def test_migrate_favorites_to_collection(tmp_path):
    db_path = create_db_with_two_cards()
    db = Database(db_path)

    fav_service = FavoritesService(db)
    collection_tracker = CollectionTracker()

    # Add favorites
    fav_service.add_favorite_card('uuid-swamp', note='Nice card')
    fav_service.add_favorite_printing('uuid-mountain', 'SET', '2', note='Cool art')

    # Before migration, collection tracker should have none
    assert not collection_tracker.is_favorite('Swamp')
    assert not collection_tracker.is_favorite('Mountain')

    migrated = fav_service.migrate_to_collection(collection_tracker, remove_after_migrate=True)
    assert migrated >= 2

    # Now favorites in collection tracker should be present
    assert collection_tracker.is_favorite('Swamp')
    assert collection_tracker.is_favorite('Mountain')

    # And favorites are removed from DB
    assert not fav_service.is_favorite_card('uuid-swamp')
    assert not fav_service.is_favorite_printing('uuid-mountain')

    db.close()
