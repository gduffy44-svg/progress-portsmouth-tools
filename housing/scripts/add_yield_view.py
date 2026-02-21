with open('housing/hap-explorer.html', 'r') as f:
    c = f.read()

print('Starting size:', len(c))

# 1. Add Yield View button to header toolbar
old_btn = 'onclick="setView(\'table\')">&#9776; Table</button>'
new_btn = 'onclick="setView(\'table\')">&#9776; Table</button>\n        <button class="view-btn" id="yieldBtn" data-view="yield" onclick="setView(\'yield\')">&#9670; Yield</button>'
c = c.replace(old_btn, new_btn, 1)
print('1. Yield btn added:', 'yieldBtn' in c)

# 2. Add yield view render block after table view
old_table_end = 'h += `</tbody></table></div>`;\n\n  h += `<div class="version-note">'
new_table_end = '''h += `</tbody></table></div>`;

  // Yield view
  const yieldItems = filtered.filter(function(item) {
    var ev = EVALUATIONS[slugify(item.action)];
    return ev && ev.yieldType;
  });
  if (currentView === 'yield') {
    var yLow = 0, yHigh = 0, yCount = yieldItems.length;
    yieldItems.forEach(function(item) {
      var ev = EVALUATIONS[slugify(item.action)];
      var nums = (ev.yieldEstimate||'').match(/\\d+/g);
      if (nums && nums.length >= 2) { yLow += parseInt(nums[0]); yHigh += parseInt(nums[1]); }
    });
    h += '<div class="yield-view">';
    h += '<div class="yield-view-header">';
    h += '<div class="yield-view-title">&#9670; Housing Yield Estimates</div>';
    h += '<div class="yield-view-meta">' + yCount + ' of ' + filtered.length + ' items evaluated';
    if (yCount > 0) h += ' &nbsp;·&nbsp; Estimated potential: <strong>' + yLow + '&ndash;' + yHigh + ' units</strong> <span class="yield-caveat">(varying timeframes &mdash; not directly additive)</span>';
    h += '</div>';
    h += '<div class="yield-view-note">Based on Byron Matto GIS parcel analysis (Jan 2026) and RKG Housing Market Study (2022). High/medium confidence items use parcel-level data; speculative items are enabling actions without direct unit counts.</div>';
    h += '</div>';
    if (yieldItems.length === 0) {
      h += '<div class="no-results"><div class="icon">&#9670;</div><div>No yield estimates in current filter.</div></div>';
    } else {
      h += '<table class="yield-table"><thead><tr>';
      h += '<th>Action Item</th><th style="width:110px">Yield Type</th><th style="width:160px">Estimate</th><th style="width:100px">Timeframe</th><th style="width:100px">Confidence</th><th style="width:140px">Responsible Party</th>';
      h += '</tr></thead><tbody>';
      yieldItems.forEach(function(item) {
        var ev = EVALUATIONS[slugify(item.action)];
        var conf = ev.yieldConfidence || '';
        var confClass = conf === 'high' ? 'conf-high' : conf === 'medium' ? 'conf-medium' : 'conf-speculative';
        h += '<tr>';
        h += '<td><strong>' + item.action + '</strong>';
        if (ev.keyConcern) h += '<div class="yield-concern">&#9888; ' + ev.keyConcern + '</div>';
        if (ev.yieldNotes) h += '<div class="yield-notes-row">' + ev.yieldNotes + '</div>';
        h += '</td>';
        h += '<td><span class="yield-type-badge">' + (ev.yieldType||'') + '</span></td>';
        h += '<td><strong>' + (ev.yieldEstimate||'&mdash;') + '</strong></td>';
        h += '<td>' + (ev.yieldTimeframe||'&mdash;') + '</td>';
        h += '<td><span class="conf-badge ' + confClass + '">' + (conf||'&mdash;') + '</span></td>';
        h += '<td>' + (ev.responsibleParty||'&mdash;') + '</td>';
        h += '</tr>';
      });
      h += '</tbody></table>';
    }
    h += '</div>';
  }

  h += `<div class="version-note">'''
c = c.replace(old_table_end, new_table_end, 1)
print('2. Yield view render:', 'yield-view' in c)

# 3. Add yield view CSS
yield_view_css = """
.yield-view { padding: 4px 0; }
.yield-view-header { background: var(--white); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px 20px; margin-bottom: 16px; }
.yield-view-title { font-family: 'DM Serif Display', Georgia, serif; font-size: 1.1rem; color: var(--navy); margin-bottom: 6px; }
.yield-view-meta { font-size: 0.85rem; color: var(--slate); margin-bottom: 8px; }
.yield-caveat { font-size: 0.78rem; color: var(--slate); font-style: italic; }
.yield-view-note { font-size: 0.75rem; color: var(--slate); border-top: 1px solid var(--border); padding-top: 8px; margin-top: 8px; font-style: italic; }
.yield-table { width: 100%; border-collapse: collapse; font-size: 0.83rem; background: var(--white); border-radius: var(--radius); overflow: hidden; border: 1px solid var(--border); }
.yield-table thead th { background: var(--navy); color: var(--white); padding: 10px 12px; text-align: left; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; }
.yield-table tbody tr { border-bottom: 1px solid var(--border); }
.yield-table tbody tr:hover { background: #f8f7f4; }
.yield-table tbody td { padding: 12px; vertical-align: top; color: var(--navy); }
.yield-concern { font-size: 0.76rem; color: var(--coral); margin-top: 4px; font-style: italic; }
.yield-notes-row { font-size: 0.74rem; color: var(--slate); margin-top: 4px; line-height: 1.5; }
.yield-type-badge { background: rgba(201,168,76,0.15); color: #8a6f1a; font-size: 0.72rem; font-weight: 700; padding: 3px 8px; border-radius: 10px; white-space: nowrap; }
.conf-badge { font-size: 0.72rem; font-weight: 700; padding: 3px 8px; border-radius: 10px; white-space: nowrap; }
.conf-high { background: #e8f5e9; color: #2e7d32; }
.conf-medium { background: #e3f2fd; color: #1565c0; }
.conf-speculative { background: #f3f3f3; color: #757575; }
"""
c = c.replace('</style>', yield_view_css + '</style>', 1)
print('3. Yield view CSS added:', '.yield-view' in c)

# 4. Remove gold diamond from card header pill - replace with subtler approach
# The yield-pill on cards can stay but simplify label
old_pill = '\'<span class="yield-pill">&#9670; Yield Est.</span>\''
new_pill = '\'<span class="yield-pill">&#9670;</span>\''
c = c.replace(old_pill, new_pill, 1)
print('4. Card pill simplified:', c.count('"yield-pill">&#9670;</span>') >= 1)

with open('housing/hap-explorer.html', 'w') as f:
    f.write(c)

print('Done. Final size:', len(c))
