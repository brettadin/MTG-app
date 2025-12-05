# MTG Deck Builder - Getting Started Guide

## Quick Start

### Prerequisites Check
✅ Python 3.11+ installed  
✅ ~2GB free disk space  
✅ MTGJSON data in `libraries/` folder  
✅ Internet connection (for initial setup)

### 5-Minute Setup

1. **Install Dependencies**
   ```powershell
   cd mtg-app/MTG-app
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Build Database Index**
   ```powershell
   python scripts/build_index.py
   ```
   ⏱️ Takes 2-5 minutes. Creates searchable database from MTGJSON.

3. **Launch Application**
   ```powershell
   python main.py
   ```

## First Use

### Search for Cards
1. Type card name in left panel (e.g., "Lightning Bolt")
2. Press Enter or click Search
3. Click a result to see details
4. View alternative printings in right panel

### Create Your First Deck
1. Go to Decks tab
2. Click "New Deck"
3. Search for cards
4. Add to deck
5. View statistics

### Manage Favorites
1. Search for a card
2. Click ⭐ to favorite
3. View all favorites in Favorites tab

## Configuration

Edit `config/app_config.yaml` for:

### Change Data Paths
```yaml
mtgjson:
  csv_directory: "path/to/csv"
  json_sets_directory: "path/to/sets"
```

### Adjust Image Cache
```yaml
scryfall:
  enable_image_cache: true
  max_cache_size_mb: 500
```

### Logging Level
```yaml
logging:
  level: "DEBUG"  # or INFO, WARNING, ERROR
```

## Common Tasks

### Update Card Data
```powershell
# 1. Download new MTGJSON files
# 2. Replace in libraries/ folder
# 3. Rebuild index
python scripts/rebuild_index.py
```

### Clear Image Cache
UI Menu: Tools → Clear Image Cache

Or manually:
```powershell
Remove-Item -Recurse data/image_cache/*
```

### Export Deck
1. Open deck
2. File → Export Deck
3. Choose format (Text or JSON)

### Import Deck
1. File → Import Deck
2. Select file
3. Review and save

## File Locations

### Important Files
- **Database**: `data/mtg_index.sqlite`
- **Config**: `config/app_config.yaml`
- **Logs**: `logs/app.log`
- **Cache**: `data/image_cache/`

### MTGJSON Data
- **CSV**: `libraries/csv/*.csv`
- **Sets**: `libraries/json/AllSetFiles/*.json`

### Documentation
- **Architecture**: `doc/ARCHITECTURE.md`
- **Data Sources**: `doc/DATA_SOURCES.md`
- **Deck System**: `doc/DECK_MODEL.md`
- **Changes**: `doc/CHANGELOG.md`

## Troubleshooting

### "Database not found"
**Solution**: Run `python scripts/build_index.py`

### Slow Performance
**Check**: 
- Database indexes created? Look for "Creating database indexes..." in logs
- Too many results? Reduce search limit in config
- Disk space? Database needs ~1GB

### Images Not Loading
**Check**:
- Internet connection
- Scryfall rate limit (wait a moment)
- Check logs for errors

### Search Returns Nothing
**Check**:
- Database built successfully?
- Spelling of card name
- Try simpler search (just name, no other filters)

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Execute search |
| Ctrl+N | New deck |
| Ctrl+O | Import deck |
| Ctrl+S | Export deck |
| F5 | Refresh |

## Tips & Tricks

### Faster Searches
- Use partial names ("bolt" finds Lightning Bolt)
- Fewer filters = faster results
- Results are limited (default 100)

### Better Deck Building
- Add set codes to specify printings
- Use tags to organize decks
- Export regularly as backup

### Image Caching
- Images cache automatically if enabled
- Cache size limit prevents unlimited growth
- Clear cache if running low on space

## Next Steps

1. **Read Documentation**: Check `doc/` folder for detailed info
2. **Build a Deck**: Try creating a Commander deck
3. **Explore Filters**: Advanced search options available
4. **Customize**: Edit config file to suit your needs

## Getting Help

### Check Logs
```powershell
cat logs/app.log
```

### Debug Mode
In `config/app_config.yaml`:
```yaml
logging:
  level: "DEBUG"
```

### Common Issues
- Check `doc/ARCHITECTURE.md` for system overview
- Review `doc/DEVLOG.md` for known limitations
- See `doc/DATA_SOURCES.md` for data format info

## Project Status

### ✅ Working Features
- Card search with filters
- Card detail display
- Database indexing
- Image loading from Scryfall
- Configuration system
- Logging

### 🚧 In Progress
- Full deck builder UI
- Deck statistics visualization
- Favorites grid view
- Import/export dialogs

### 📋 Planned
- Collection management
- Price tracking
- Advanced filters
- Format validation
- Deck comparison

## Support

For questions or issues:
1. Check documentation in `doc/`
2. Review log files in `logs/`
3. Check configuration in `config/`
4. Search existing GitHub issues
5. Open new issue with logs attached

## Updates

Check for updates:
1. Pull latest code
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Rebuild index if MTGJSON updated
4. Check CHANGELOG.md for changes

---

**Version**: 0.1.0  
**Last Updated**: 2024-12-04  
**Status**: Alpha - Core features functional, UI in progress
