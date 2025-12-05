# Data Sources Documentation

## MTGJSON

### Overview
MTGJSON is the primary data source for card and set information. All card data is sourced from MTGJSON and stored locally in SQLite for fast querying.

### Files Used

#### CSV Files (`libraries/csv/`)
Located in the `AllPrintingsCSVFiles` directory:

- **cards.csv** - Main card data
  - UUID, name, set code, collector number
  - Mana cost, mana value, colors, color identity
  - Type line, supertypes, types, subtypes
  - Rules text, flavor text, oracle text
  - Power, toughness, loyalty
  - Rarity, layout, frame information
  - EDHREC rank and saltiness
  - Artist, promo status, foil availability

- **cardIdentifiers.csv** - External identifiers
  - Scryfall ID (used for image fetching)
  - Multiverse ID
  - MTGO ID
  - TCGPlayer ID
  - Cardmarket ID

- **cardLegalities.csv** - Format legality
  - Format name (Commander, Modern, Standard, etc.)
  - Status (Legal, Banned, Restricted, Not Legal)

- **cardPrices.csv** - Historical pricing
  - Provider (tcgplayer, cardmarket, etc.)
  - Retail and buylist prices
  - Foil and non-foil prices
  - Date of price snapshot

- **sets.csv** - Set metadata (alternative source)
  - Set code, name, type
  - Release date
  - Block, parent set
  - Online/foil only status

#### JSON Files (`libraries/json/AllSetFiles/`)
Individual set files with complete set data:

- **[SETCODE].json** - Complete set information
  - Set metadata (name, code, release date, type)
  - Cards array with full card objects
  - Booster configuration
  - Tokens

Each set JSON contains:
```json
{
  "data": {
    "code": "BRO",
    "name": "The Brothers' War",
    "type": "expansion",
    "releaseDate": "2022-11-18",
    "totalSetSize": 287,
    "cards": [...]
  }
}
```

### Data Model Mapping

#### MTGJSON → SQLite Mapping

**cards table:**
- `uuid` ← MTGJSON uuid (unique identifier)
- `name` ← name
- `set_code` ← setCode
- `collector_number` ← number
- `mana_cost` ← manaCost
- `mana_value` ← manaValue (formerly CMC)
- `colors` ← colors (array joined to string)
- `color_identity` ← colorIdentity (array joined to string)
- `type_line` ← type
- `text` ← text
- `rarity` ← rarity
- `power/toughness/loyalty` ← power/toughness/loyalty

**Handling Arrays:**
MTGJSON uses JSON arrays for multi-value fields. We store these as comma-separated strings:
- Colors: `["W", "U"]` → `"W,U"`
- Types: `["Legendary", "Creature"]` → `"Legendary,Creature"`

### Version Tracking

The application tracks MTGJSON version via:
1. **meta.csv** - Contains version and build date
2. **INDEX_VERSION.json** - Stores indexed version and build timestamp

Version check on startup:
- Compare current MTGJSON version to indexed version
- Prompt user to rebuild if mismatch detected

### Update Process

To update MTGJSON data:
1. Download latest MTGJSON files
2. Replace files in `libraries/` directory
3. Run `python scripts/rebuild_index.py`
4. Application will use new data

## Scryfall

### Overview
Scryfall is used exclusively for card images. No card data is fetched from Scryfall (all comes from MTGJSON).

### Image URLs

Images accessed via CDN using the Scryfall ID from MTGJSON:

**URL Pattern:**
```
https://cards.scryfall.io/{size}/{face}/{dir1}/{dir2}/{scryfallId}.{ext}
```

**Parameters:**
- `size`: small, normal, large, png, art_crop, border_crop
- `face`: front, back (for double-faced cards)
- `dir1`: First character of Scryfall ID
- `dir2`: Second character of Scryfall ID
- `ext`: jpg (or png for 'png' size)

**Example:**
```
https://cards.scryfall.io/large/front/a/b/ab123456-1234-5678-90ab-cdef12345678.jpg
```

### Rate Limiting

Scryfall requests are rate-limited to **10 requests per second** to respect their API guidelines.

Implementation:
- Minimum 100ms between requests
- Automatic throttling in `ScryfallClient`
- Local caching to reduce requests

### Image Caching

**Cache Location:** `data/image_cache/`

**Cache Strategy:**
- Optional (configurable in `app_config.yaml`)
- Files named: `{scryfallId}_{size}_{face}.{ext}`
- No automatic cleanup (manual clear via UI)
- Configurable max size (default 500MB)

**Cache Control:**
```yaml
scryfall:
  enable_image_cache: true
  image_cache_dir: "data/image_cache"
  max_cache_size_mb: 500
```

### Optional: Live Price Fetching

While MTGJSON includes historical prices, Scryfall API can provide current prices:

**API Endpoint:**
```
GET https://api.scryfall.com/cards/{scryfallId}
```

**Response includes:**
```json
{
  "prices": {
    "usd": "1.23",
    "usd_foil": "4.56",
    "eur": "1.10",
    "tix": "0.50"
  }
}
```

This feature is **not currently implemented** but the infrastructure exists in `ScryfallClient`.

## Data Attribution

### MTGJSON
- **Website**: https://mtgjson.com/
- **License**: Creative Commons CC0
- **Attribution Required**: Yes
- **Data Source**: Wizards of the Coast

### Scryfall
- **Website**: https://scryfall.com/
- **API Documentation**: https://scryfall.com/docs/api
- **Rate Limit**: 10 requests/second
- **Attribution Required**: Recommended

### Wizards of the Coast
All card data and images are © Wizards of the Coast LLC, a subsidiary of Hasbro, Inc. Magic: The Gathering is a trademark of Wizards of the Coast.

## Data Update Frequency

### MTGJSON
- **Release Schedule**: Updates with new set releases
- **Download Location**: https://mtgjson.com/downloads/all-files/
- **Recommended Update**: After each new set release

### Scryfall Images
- **Update**: Automatic (images fetched on-demand)
- **New Printings**: Available immediately when Scryfall adds them

## Local Storage Requirements

### Initial Download
- **AllPrintingsCSVFiles.zip**: ~150MB compressed
- **AllSetFiles.zip**: ~300MB compressed

### After Index Build
- **SQLite Database**: ~500MB - 1GB (indexed)
- **Image Cache**: Configurable (default max 500MB)
- **Total**: ~1.5GB - 2GB (approximate)

## Privacy Considerations

### Data Collection
This application **does not collect or transmit** any user data.

### External Requests
The only external requests made are:
1. **Scryfall Image CDN**: For card images
2. **(Optional) Scryfall API**: For live price updates

### Offline Capability
The application can run **completely offline** except for:
- Initial image loading (images cached locally after first load)
- Optional live price updates
