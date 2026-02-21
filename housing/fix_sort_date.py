with open('housing/hap-explorer.html', 'r') as f:
    c = f.read()

print('Starting size:', len(c))

# 1. Update date
c = c.replace('Version 2 \xe2\x80\x94 February 20, 2026', 'Version 2 \xe2\x80\x94 February 21, 2026')
print('1. Date updated:', 'February 21, 2026' in c)

# 2. Add yield TH to table header
old_thead = '<thead><tr><th style="width:36px">#</th>'
new_thead = '<thead><tr><th style="width:28px;text-align:center;color:var(--gold);cursor:pointer" onclick="sortYield()" title="Sort: yield items first">&#9670;</th><th style="width:36px">#</th>'
c = c.replace(old_thead, new_thead, 1)
print('2. Yield TH added:', 'sortYield' in c)

# 3. Fix cat-row colspan 6 -> 7
c = c.replace('colspan="6"', 'colspan="7"', 1)
print('3. Colspan updated:', 'colspan="7"' in c)

# 4. Add yield cell to table rows
old_tr = '`<tr class="${rc}"><td>${tn}</td>'
new_tr = '`<tr class="${rc}"><td style="text-align:center;color:var(--gold)">${EVALUATIONS[slugify(item.action)]&&EVALUATIONS[slugify(item.action)].yieldType ? \'&#9670;\' : \'\'}</td><td>${tn}</td>'
c = c.replace(old_tr, new_tr, 1)
print('4. Yield cell in row:', c.count('&#9670;') >= 2)

# 5. Add sortYield function and yieldSortActive var
old_gf = '\nfunction getFiltered() {'
new_gf = '\nvar yieldSortActive = false;\nfunction sortYield() { yieldSortActive = !yieldSortActive; renderContent(); }\n\nfunction getFiltered() {'
c = c.replace(old_gf, new_gf, 1)
print('5. sortYield fn:', 'function sortYield' in c)

# 6. Add sort to getFiltered return
old_end = '    return true;\n  });\n}\n\nfunction setCate'
new_end = '    return true;\n  }).sort(function(a,b) {\n    if (!yieldSortActive) return 0;\n    var aY = EVALUATIONS[slugify(a.action)]&&EVALUATIONS[slugify(a.action)].yieldType ? 1 : 0;\n    var bY = EVALUATIONS[slugify(b.action)]&&EVALUATIONS[slugify(b.action)].yieldType ? 1 : 0;\n    return bY - aY;\n  });\n}\n\nfunction setCate'
c = c.replace(old_end, new_end, 1)
print('6. Sort in getFiltered:', 'yieldSortActive' in c[c.find('function getFiltered'):c.find('function getFiltered')+900])

with open('housing/hap-explorer.html', 'w') as f:
    f.write(c)

print('Done. Final size:', len(c))
