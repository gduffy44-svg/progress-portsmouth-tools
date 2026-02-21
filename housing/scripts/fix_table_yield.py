with open('housing/hap-explorer.html', 'r') as f:
    c = f.read()

print('Starting size:', len(c))

# Fix 1: Add yield cell to each table row
old_tr = 'h += `<tr class="${rc}"><td>${tn}</td>'
new_tr = 'h += `<tr class="${rc}"><td style="text-align:center;color:var(--gold)">${EVALUATIONS[slugify(item.action)]&&EVALUATIONS[slugify(item.action)].yieldType ? \'&#9670;\' : \'\'}</td><td>${tn}</td>'
c = c.replace(old_tr, new_tr, 1)
print('1. Table row yield cell:', '&#9670;' in c[c.find('data-table'):c.find('data-table')+2000])

# Fix 2: Fix the colspan on cat-row from 6 to 7
old_colspan = 'colspan="6"'
new_colspan = 'colspan="7"'
c = c.replace(old_colspan, new_colspan, 1)
print('2. Colspan updated:', 'colspan="7"' in c)

# Fix 3: Add the yield column header properly (with sort onclick)
old_th = '<th style="width:32px" onclick="sortTable(\'yield\')" style="cursor:pointer" title="Sort by yield estimate">&#9670;</th>'
new_th = '<th style="width:32px;cursor:pointer;text-align:center;color:var(--gold)" onclick="sortTable(\'yield\')" title="Sort: yield items first">&#9670;</th>'
c = c.replace(old_th, new_th, 1)
print('3. TH style fixed:', 'color:var(--gold)' in c[:c.find('</thead>')+100])

with open('housing/hap-explorer.html', 'w') as f:
    f.write(c)

print('Done. Final size:', len(c))
