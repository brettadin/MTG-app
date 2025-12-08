# Agent Handoff & Guidance

> ⚠️ Agents & Contributors: Before making changes, please read `doc/prompts/MTG_FUNDEMENTALS_AND_GUIDE.txt`. This file is the canonical project guidance and MTG rules summary and should be the first reference for all future agents.

This document is intended for future agents working on the MTG-app project. It summarizes recent work, the architectural choices, and step-by-step tasks to help continue development.

## ✅ Summary of Recent Work
- Fixed Quick Search bug and adjusted Quick Search to emit both legacy string and SearchFilters object (backwards compatibility).
- Implemented `SearchCoordinator` to centralize quick and advanced search flows.
- Added an integration test to validate QuickSearch -> SearchCoordinator -> ResultsPanel flow.
- Implemented and tested database FTS5 full-text search and indexes.
- Fixed a bug in `MTGRepository.search_cards_fts` (joined by `rowid` instead of `uuid`).
- Added `populate_fts_index` and unit tests for the FTS pipeline.
- Moved legacy UI files `main_window.py` and `enhanced_main_window.py` into `app/ui/archive/` and replaced them with shims exporting `IntegratedMainWindow` for backwards compatibility.
- Improved `SearchPanel.set_search` to be robust when certain input widgets are hidden; wrapped setText calls in try/except.
- Standardized Scryfall image loading by using the `ScryfallClient` API instead of raw urllib requests and implemented a `QThread` worker (`app/ui/workers/image_downloader.py`) to avoid blocking the UI (see `app/ui/panels/card_detail_panel.py`).
 - Recent session summary is available in `SESSION_17_SUMMARY.md` (Session 17 - Agent Handoff & Cleanups).
 - Recent session summary is available in `SESSION_17_SUMMARY.md` (Session 17 - Agent Handoff & Cleanups).
 - Primary agent guidance: `doc/prompts/MTG_FUNDEMENTALS_AND_GUIDE.txt` — this file contains the detailed MTG fundamentals, design goals, and developer guidance that agents should consult first when working on the project.
 - Historical context / initial prompt (secondary reference): `doc/prompts/INITIAL PROMPT.txt`.
 - Testing note: tests now run with `MTG_TEST_MODE=1` by default in `tests/conftest.py`; this suppresses modal dialogs during automated tests.

## 🛠️ Key Architectural Notes
- SearchFilters is the canonical input object for searches. All signals should be migrated to emit SearchFilters objects where possible.
- `SearchCoordinator` is the canonical central point for normalizing search events and performing debounced searches.
- `MTGRepository` contains both LIKE and FTS5-based search methods; use `search_cards_fts` for performance-sensitive paths.
- The primary UI entry window is `IntegratedMainWindow` (monolithic but the planned decomposition target). Old windows are kept as archived copies.
 - Documentation: In-app documentation files were added at `doc/` (`RULES.md`, `KEY_TERMS.md`, `TUTORIAL.md`) and can be viewed via Help → Documentation in the app. The viewer is implemented at `app/ui/documentation_dialog.py`; future agents should keep these markdown files updated when features or rules change.

## 🔍 Future Steps for Agents (Checklist)
1. Decompose `IntegratedMainWindow` into smaller widgets or controllers. Suggested submodules:
   - `DeckBuilderTab` (Left filters + Results + Deck panel)
   - `CollectionTab` (Collection management)
   - `GameTab` (Game viewer + controls)
   - Each submodule should be independently testable and instantiated in the main window.

2. Convert Scryfall downloading to a non-blocking pattern.
   - Approach: Use Qt `QThread` per download or QThreadPool + QRunnable to offload I/O.
   - Replace `ScryfallClient.download_card_image` sync calls with either `asyncio` + runner or `QThread` wrappers.
   - Add progress indicators and caching behaviors.

3. Expand integration tests to cover the IntegratedMainWindow flow for:
   - Deck operations: add, remove, save, load
   - Game simulation: phasing, stack resolution, priority passing
   - UI interactions: quick search, advanced search, add to deck, show printings

4. Complete game engine critical tasks
   - Replace simplified mana system with a full ManaManager
   - Complete stack resolution and state-based action handling
   - Add more engine integration tests for complex card interactions

5. Perform a repository-wide duplicate code audit
   - Search for duplicates using grep and remove archived/unused files
   - Centralize common behaviors into utilities and managers

6. Documentation consolidation
   - Consolidate docs into `FEATURES.md`, `USER_GUIDE.md`, `API_REFERENCE.md` as planned
   - Keep session logs in `doc/archive/` and add the agent guidance to `doc/AGENT_GUIDANCE.md`
   - Document all changes made before you respond to the user. No exceptions.
   - Revise future steps for agents so they refer to the same documents, and get updated instructions.
   - read ## PERSONAL NOTES AND SOME IDEAS FROM SOLO HUMAN DEV  to see if any new notes or stuff have been added :D

   ## 🧪 Test Mode & Blocking Dialogs
   - To prevent modal dialogs blocking automated test runs, tests set the `MTG_TEST_MODE` environment variable and `Config` has `ui.test_mode` that can be toggled.
   - In test mode, `IntegratedMainWindow` monkeypatches `QMessageBox` to no-op versions; if you need to assert dialog content or behaviors in tests, explicitly disable test_mode or use mocks to capture calls.
    - Favorites migration note: the preferred model for favorites is to use `CollectionTracker` favorites (collection tags). UI panels generally use `CollectionTracker` where available; `FavoritesService` remains for backward-compatible DB storage and migrations via `FavoritesService.migrate_to_collection()`.
## ✅ How to Run Tests Locally (Quick Reference)
- Run a specific test file (pytest-qt and environment required):

```pwsh
cd C:/Code/mtg-app/MTG-app
.venv\Scripts\activate
${env:MTG_TEST_MODE} = '1'
python -m pytest tests/ui/test_quick_search_filters.py -q
```

- Run all tests (may require test fixtures or a prepared DB):

```pwsh
${env:MTG_TEST_MODE} = '1'
python -m pytest -q
```

## 🧭 Design & Coding Tips for Agents
- Maintain backwards compatibility; keep `search_requested` string emission until all consumers migrate to `SearchFilters`.
- Make minimal, observable changes: run UI tests after each change to ensure no regressions.
- Use `SearchCoordinator` for centralizing search logic; don't duplicate search logic in multiple panels.
- For UI changes, prefer `pytest-qt` tests to validate signal flows and event handling.

## 📋 Where to Look For Tasks
- `doc/TODO.md`: high-level TODOs and priorities
- `doc/UI_REDESIGN_PLAN.md`: proposed UI changes and priorities
- `doc/IMPLEMENTATION_ROADMAP.md`: step-by-step technical tasks and code locations
- `doc/FEATURE_CHECKLIST.md`: checklist of features
- `doc/FEATURE_SUMMARY.md`: summary of features
- `doc/FEATURE_IDEAS.md`: ideas for features to add. use this if you think of something, if the user suggests something, and if you are told to add new material.
- `app/ui/integrated_main_window.py`: main UI entry point and currently-used window
- `app/ui/search_coordinator.py`: search centralization and debounce logic
- `app/data_access/mtg_repository.py`: search implementations and FTS functions

## 📬 Handoff Notes
- If you implement compatibility breaking changes, ensure there are shims and stepwise migration.
- Add tests for each behavior change, especially UI signal changes and DB query behaviors.
 - When running tests in CI or locally, avoid modal dialog interactions by setting the environment variable `MTG_TEST_MODE=1` or configuring `ui.test_mode: true` in `config/app_config.yaml`.
- When archiving files, leave a shim that re-exports primary class to avoid breaking scripts and debug tools.

## PERSONAL NOTES AND SOME IDEAS FROM SOLO HUMAN DEV 
- check for old session summaries if you need to find out how things were done, or why they were done. context is powerful.
- keep files and file documentation consistent to keep a well maintained history of development
- context context context. this is an application for magic the gathering, and it is meant to import all info about cards, make decks, and battle with them either simulations, against ai, or in 1v1 games of any game format (with working rules) and multiplayer games (with working rules). comnbat and gameplay will be similar to that of magic the gathering arena, or hearthstone, as exampls. there are files for visuals and sounds already that can be adapated and expanded on. 
- check all of the repo when you are working. there may be something that does what you are trying to do, cause sometimes ai agents do duplicates, or weird behaviors that kind of continue. this will be a published piece of software one day. so the file content, and structure, should reflect a professional piece of software. including well documented patch notes. in app documentation. ciations where needed (many references are supplied and you are welcome to expand on them). in line code comments to provide context for future coding agents, so we dont reinvent something we already have.
- dont spend too long on one task, if its taking a long time or its getting too complicated. take a step back and think if it can be done more simply, or if its best to just move on to the next task and make note that the complex one needs to be fixed, and what your issues were, and how they may be fixed. development time is a good thing to think of. since this application is made 100% by ai agents, with a solo human testing the app for functionality. 
- oh one idea that may be nice. since we will have in app documentation somewhere, we should include the rules there, like how to play, and defintions of all key words and stuff. a bunch of in app stuff to teach the players how to use the app/play the game/refresh memory on anything they need. also make it so agents who work on this code can read/learn from this documentation as well so they keep up context. this can also be expanded to adding a very simple tutorial mode too, just to teach the user how to play/use the game engine/ui features. as we work we should update this documentation so it stays up to date for all features and content and context and anything else. 
- (this is part of a prompt) once you make note of how to do this (you dont have to do all that stuff right now, i know its a lot.) then you can continue doing any work you think we should do. this is not limited to documenation. you are free to add new features, and instruct the next agent to do the same, or you can do anything you want, and tell the next agent to do anything. what im saying is, do your work how you think you should, then hand it off to the next guy to do something. just make sure what youre doing makes sense, and youre not spinning your wheels, locked in on some random small task that doesnt need a lot of attention. 





- ### prompts ive used
   start
    okay so adding cards to the deck works now.
i just cant see the deck too well in the ui. its a list. remember this needs to be a good, clean ui designed for humans. we can get fancy with it. utilize our spacing logically. like. if we're making a deck, what do we want to see? we're searching cards at the same time, so its a lot going on at once. how do we solve this without disconnecting the two too much? 

also the view stats stuff doesnt work.
i dont think it needs to be its own tab. we could probably just merge that into the deck viewer somehow, but without taking up space and cluttering the ui.

maybe it would be easiest to seperate the search and the deck displays. im not sure. what do you think? make sure you document my questions and logic here, and how it could be useful/break thigns/work, whatever.

also the game viewer looks so weird. i get this is kind of.. low tech. but this is supposed to be a competitive game, right? consider how game boards are set up in magic. does that ui make sense? lol

also the collection tab doesnt seem to be working, or at least i cant add things to a collection. im not stressing this though, or the pricing stuff right now, because they are very very low priority things for me. 

   **Session 18 update:** See `doc/SESSION_18_SUMMARY.md` for the recent fixes (deck validation sync, add-to-deck fallback) and prioritized UI/collection tasks to follow up on.

   ---
    end


- ( a prompt to make a master guidance prompt for all future agents)
Start
1. im developing a mtg application that can pull any card/art and all data about it, including rules, and import that. we can make decks, save them, import them, and play games. we should be able to play in any and every format with working rules. you are going to outline the fundamentals of all things magic, and load it with reference sources of rules, cards, gameplay mechanics etc, and also links to githubs or other resources for making an application like that. your instructions are to be referenced each time by every agent that works on the app so they have a core understanding of the game, how to play it, what everything does and means, so that they can then develop the application and game and everything else. they should ensure everything connects to other things that are needed. the UI design should be clean and organized and human friendly. They also have a multitude of reference material and patch notes from previous ai agents. they should add to this to keep our knowledge up to date, as well as all documentation displayed in the application itself, and stuff thats stored in the repo. the game will have functioning mechanics, similar to MTG arena, and have visuals and sounds. It will support vs ai, vs player in a 1v1 of any format, and multiplayer games such as 1v1v1, 2v2, 1v2, and so on. up to... lets say 16 players total. we can update this in time if needed, but i highly doubt it. we should be able to play all game modes where possible. and all decks should be checked for legality. there is a bunch of stuff we can directly pull from if we use things like moxfields api, or scryfall, or any other large card database that can let us access their information. all coding logic should be consistent so we dont have shit breaking all the time. 
2. this is purely digital. i want a sandbox environment to make decks, search stuff, look up combos, do all the fun stuff, and also play my friends in any game size or format.
3. They should have access to content from all sets, but yes they do need to know everything about the game since they will be making the game into a digital version/library, and referencing it as they work.
4. i dont really care tbh, but if you do, make sure an ai can read it. i will be pasting this into a .md file for them to read and reference everytime they work.
5. All deck types, Commander, standard, historic, pauper, and any others. there are many but we can describe a few for now to get the ball rolling. The agents will make every format though in time so they should know how to access that information as well.
end



















## THANK YOU AGENT
Thank you — continue iterating, adding features and debugging and testign and all that jazz and keep this file updated for the next agent.

---