# Progress Portsmouth Tools — Maintenance Reference

Operational notes for maintaining the tools in this repository.
Keep this file updated as workflows change.

---

## Repository Structure

```
progress-portsmouth-tools/
├── housing/
│   ├── housing-pipeline.html       # Housing Pipeline module
│   └── hap-explorer.html           # HAP Explorer module
├── MAINTENANCE.md                  # This file
```

**Live URL base:** `progress-portsmouth-tools.vercel.app`
**Deployment:** GitHub → Vercel (auto-deploys on push to main, ~30 second propagation)

---

## Housing Pipeline

**Live URL:** `progress-portsmouth-tools.vercel.app/housing/housing-pipeline.html`

### Data
Project data is embedded directly in the HTML file as a `PIPELINE_DATA` constant near the top of the `<script>` block. There is no separate JSON file — everything is in the one HTML file.

**To update project data:**
1. Open `housing/housing-pipeline.html` in VS Code
2. Find the `PIPELINE_DATA` object (search for `"projects":`)
3. Edit the relevant project record(s)
4. Validate before committing (see below)
5. Update `last_updated` date in the `meta` block at the top of `PIPELINE_DATA`
6. Commit and push

### Project record fields

| Field | Type | Notes |
|---|---|---|
| `name` | string | Display name — keep concise |
| `address` | string | Street address. Suppressed in UI if it duplicates the name |
| `status` | string | Must match exactly: `Under construction`, `Approved`, `Permitting`, `Concept`, `Potential`, `Occupied` |
| `type` | string | `market`, `mixed`, or `affordable` — internal only, not shown in UI |
| `total_units` | number | Total unit count including all types |
| `units_market` | number | Market-rate unit count |
| `units_affordable` | number | Permanently affordable (income-restricted) units only |
| `occupancy_year` | number or null | Estimated move-in year — null if unknown |
| `lat` | number | Latitude for map pin |
| `lng` | number | Longitude for map pin |
| `city_url` | string or null | City project page URL |
| `media_url` | string or null | News coverage URL |
| `map_url` | string or null | Google Maps URL |
| `notes` | string or null | Short note shown in expanded drawer |

### Status values (display order in UI)
`Under construction` → `Approved` → `Permitting` → `Concept` → `Potential` → `Occupied`

### Validate before committing
The HTML embeds JSON-like JS — check for syntax errors before every push:

```bash
node -e "
const fs = require('fs');
const html = fs.readFileSync('housing/housing-pipeline.html', 'utf8');
const m = html.match(/const PIPELINE_DATA = ({[\s\S]*?});\s*\n/);
if (!m) { console.error('PIPELINE_DATA not found'); process.exit(1); }
try { JSON.parse(m[1]); console.log('Data OK'); }
catch(e) { console.error('Data error:', e.message); process.exit(1); }
"
```

If it prints `Data OK` — safe to commit. Any other output — fix the error first.

### Geographic area thresholds (for "Where in Portsmouth" chart)
Projects are bucketed by latitude/longitude:
- **North End:** lat > 43.082
- **South & Lafayette:** lat < 43.062
- **West & Route 1:** lng ≤ -70.775
- **Downtown:** everything else

If a project seems to land in the wrong bucket, adjust its `lat`/`lng` values.

### Key data notes
- Woodbury Ave Co-Op Infill: 5 units classified as `affordable` (were in market column in source spreadsheet)
- Service Credit Union Phase 1 & 2, Lower City Lot: 0 units — speculative/unscoped, update when known
- "Permanently affordable" = all income-restricted units, including the affordable portion of mixed-income projects

---

## HAP Explorer

**Live URL:** `progress-portsmouth-tools.vercel.app/housing/hap-explorer.html`
**Data files:** `hap-actions.json`, `hap-evaluations.json`

### After any data update
After committing changes to either JSON file, manually update the HAP Explorer HTML:
1. Revision date and version number in the header
2. Any action item counts or statistics (total items, category counts)
3. Always derive counts from the live JSON — never use a memorized number

**Current version:** 2.2 · March 8, 2026 · 135 items

### Byron Matto GIS data
Parcel analysis and yield estimates: `github.com/bmatto/psm-zoing-project`
Six zoning evaluation records currently populated with GIS data.

---

## Portsmouth Zoning Ordinance

**Authoritative source URL pattern:**
```
files.portsmouthnh.gov/files/planning/ZoningOrd-[date]+ADOPTED.pdf
```

Always use the `+ADOPTED` suffix. Planning Board workshop drafts are preliminary only and have caused analytical errors in the past.

**Current adopted ordinance:** February 17, 2026
- ADUs now permitted by right in all single-family zones
- Conditional Use Permit (CUP) eliminated for ADUs

**Property tax rate:** $11.18 per $1,000 assessed value *(corrected from an earlier error of $16.79)*

---

## General Commit Workflow

```bash
# From repo root
git add [filename]
git commit -m "Description of change"
git push
```

Vercel deploys automatically. Check the live URL ~30 seconds after push.

**Never use the GitHub web interface for edits.** Always edit locally in VS Code, validate, then push.

---

## Design System Reference

| Element | Value |
|---|---|
| Navy | `#2d3e52` |
| Gold | `#f4a261` |
| Gold dark | `#c8822a` |
| Teal | `#3d7a6f` |
| Cream (background) | `#f8f4ee` |
| Heading font | DM Serif Display |
| Body font | Source Sans 3 |
| Mono font | JetBrains Mono |

All modules are standalone HTML files with zero external dependencies (exception: Leaflet CDN for map tabs).

---

*Last updated: March 2026*