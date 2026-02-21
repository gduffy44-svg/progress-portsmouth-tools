with open('housing/hap-explorer.html', 'r') as f:
    c = f.read()

print('Starting size:', len(c))

# Step 1: Add yield indicator to card header
# Find the card header line and add yield pill before card-arrow
old_card_head = '${badge}<span class="card-arrow">&#9660;</span>'
new_card_head = '${badge}${EVALUATIONS[slugify(item.action)]&&EVALUATIONS[slugify(item.action)].yieldType ? \'<span class="yield-pill">&#9670; Yield Est.</span>\' : \'\'}<span class="card-arrow">&#9660;</span>'
c = c.replace(old_card_head, new_card_head, 1)
print('1. Card yield pill:', 'yield-pill' in c)

# Step 2: Add yield column to table view
# Find table header row
old_th = '<th style="width:36px">#</th>'
new_th = '<th style="width:32px" onclick="sortTable(\'yield\')" style="cursor:pointer" title="Sort by yield estimate">&#9670;</th><th style="width:36px">#</th>'
c = c.replace(old_th, new_th, 1)
print('2. Table header yield col:', '&#9670;</th><th style="width:36px">' in c)

# Find table row rendering to add yield cell
old_tr_start = 'h += `<tr class="${trClass}" onclick='
idx = c.find(old_tr_start)
print('   Table row at:', idx)
if idx > 0:
    # Find what's in the first td (the number cell)
    row_section = c[idx:idx+400]
    print('   Row section:', row_section[:200])

# Step 3: Add yield indicator legend above content
old_legend_spot = '  if (!filtered.length) {'
new_legend = '''  // Yield legend if any items have yield data
  const hasYield = filtered.some(item => EVALUATIONS[slugify(item.action)] && EVALUATIONS[slugify(item.action)].yieldType);
  if (hasYield) {
    h += '<div class="yield-legend">&#9670; Gold diamond = housing yield estimate available &mdash; expand card for details</div>';
  }
  if (!filtered.length) {'''
c = c.replace(old_legend_spot, new_legend, 1)
print('3. Yield legend:', 'yield-legend' in c)

# Step 4: Add CSS
yield_css = """
.yield-pill { display: inline-block; background: var(--gold); color: var(--navy); font-size: 0.65rem; font-weight: 700; padding: 2px 7px; border-radius: 10px; margin-left: 6px; vertical-align: middle; letter-spacing: 0.04em; white-space: nowrap; }
.yield-legend { font-size: 0.75rem; color: var(--slate); padding: 6px 0 10px 0; }
.yield-legend-icon { color: var(--gold); }
.yield-col { color: var(--gold); font-size: 1rem; text-align: center; }
"""
c = c.replace('</style>', yield_css + '</style>', 1)
print('4. CSS added:', '.yield-pill' in c)

with open('housing/hap-explorer.html', 'w') as f:
    f.write(c)

print('Done. Final size:', len(c))
