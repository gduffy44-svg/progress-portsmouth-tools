with open('housing/hap-explorer.html', 'r') as f:
    c = f.read()

print('Starting size:', len(c))

# Step 1: Replace header - remove stat pills, add toolbar inline
old_header = '<header class="site-header">'
old_header_end = '</header>'
h_start = c.find(old_header)
h_end = c.find(old_header_end) + len(old_header_end)
old_header_block = c[h_start:h_end]

new_header_block = '''<header class="site-header">
  <div class="header-top">
    <div class="header-brand">
      <h1>Portsmouth <span>Housing Action Plan</span></h1>
      <span class="header-badge">Action Explorer</span>
    </div>
    <div class="header-toolbar">
      <div class="search-box">
        <input type="text" id="searchInput" placeholder="Search action items..." />
      </div>
      <div class="status-filter" id="statusFilter">
        <button class="status-filter-btn active" data-filter="all" onclick="setStatusFilter('all')">All</button>
        <button class="status-filter-btn" data-filter="complete" onclick="setStatusFilter('complete')">&#10003; Complete</button>
        <button class="status-filter-btn" data-filter="in-progress" onclick="setStatusFilter('in-progress')">&#9680; In Progress</button>
        <button class="status-filter-btn" data-filter="early-stage" onclick="setStatusFilter('early-stage')">&#9675; Early Stage</button>
        <button class="status-filter-btn" data-filter="not-started" onclick="setStatusFilter('not-started')">&#8212; Not Started</button>
      </div>
      <div class="view-toggle">
        <button class="view-btn" onclick="openGlossary()">&#128218; Glossary</button>
        <button class="view-btn active" id="cardsBtn" onclick="setView('cards')">&#9783; Cards</button>
        <button class="view-btn" id="tableBtn" onclick="setView('table')">&#9776; Table</button>
      </div>
    </div>
  </div>
</header>'''

c = c.replace(old_header_block, new_header_block)
print('1. Header replaced:', 'header-toolbar' in c)
print('   Stat pills gone:', 'stat-pill' not in c[:c.find('main-layout')])

# Step 2: Remove old standalone toolbar div
old_toolbar = c[c.find('<div class="toolbar">'):c.find('</div>\n\n<div class="main-layout">') + 6]
if '<div class="toolbar">' in c:
    c = c.replace(old_toolbar, '')
    print('2. Old toolbar removed:', '<div class="toolbar">' not in c)
else:
    print('2. Old toolbar already gone')

# Step 3: Add/update CSS for header toolbar
header_toolbar_css = '''
.header-top { display: flex; align-items: center; justify-content: space-between; padding: 10px 24px; gap: 16px; flex-wrap: wrap; }
.header-toolbar { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; flex: 1; justify-content: flex-end; }
.header-toolbar #searchInput { width: 200px; padding: 6px 12px; border: 1px solid rgba(255,255,255,0.25); border-radius: 20px; font-size: 0.8rem; background: rgba(255,255,255,0.12); color: var(--white); outline: none; }
.header-toolbar #searchInput::placeholder { color: rgba(255,255,255,0.5); }
.header-toolbar .status-filter-btn { background: none; border: 1px solid rgba(255,255,255,0.2); border-radius: 20px; padding: 4px 10px; font-size: 0.75rem; cursor: pointer; color: rgba(255,255,255,0.65); transition: var(--transition); white-space: nowrap; }
.header-toolbar .status-filter-btn:hover { background: rgba(255,255,255,0.1); color: var(--white); }
.header-toolbar .status-filter-btn.active { background: var(--gold); border-color: var(--gold); color: var(--navy); font-weight: 600; }
.header-toolbar .view-toggle { display: flex; gap: 4px; }
.header-toolbar .view-btn { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); border-radius: 6px; padding: 5px 10px; font-size: 0.78rem; cursor: pointer; color: rgba(255,255,255,0.7); white-space: nowrap; }
.header-toolbar .view-btn.active { background: var(--gold); border-color: var(--gold); color: var(--navy); font-weight: 600; }
.toolbar { display: none; }
'''

c = c.replace('</style>', header_toolbar_css + '</style>', 1)
print('3. Header toolbar CSS added')

# Step 4: Sidebar tooltip
old_cat_render = 'h += `<div class="cat-nav-item ${activeCategory===cat?\'active\':\'\'}" onclick='
new_cat_render = 'h += `<div class="cat-nav-item ${activeCategory===cat?\'active\':\'\'}" title="${cat}" onclick='
if old_cat_render in c:
    c = c.replace(old_cat_render, new_cat_render, 1)
    print('4. Sidebar tooltip added')
else:
    print('4. Sidebar tooltip: already present or pattern not found')

with open('housing/hap-explorer.html', 'w') as f:
    f.write(c)

print('Done. Final size:', len(c))
