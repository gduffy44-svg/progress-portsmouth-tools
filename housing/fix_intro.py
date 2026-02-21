with open('housing/hap-explorer.html', 'r') as f:
    c = f.read()

print('Starting size:', len(c))

ip_start = c.find("  if (activeCategory==='all' && !searchQuery && statusFilter==='all') {")
ip_end = c.find("  if (!filtered.length)", ip_start)
print('Block found:', ip_start > 0, '/ End found:', ip_end > 0)

new_block = """  if (activeCategory==='all' && !searchQuery && statusFilter==='all') {
    var alreadyActive = DATA.filter(function(d){return d.status&&d.status!=='not-started'&&d.status!=='';}).length;
    var notYet = DATA.length - alreadyActive;
    var sc = {};
    DATA.forEach(function(item){ sc[item.status] = (sc[item.status]||0)+1; });
    h += '<div class="workload-summary">';
    h += '<div class="workload-stats">';
    h += '<div class="workload-stat"><span class="ws-num">' + DATA.length + '</span><span class="ws-label">Action Items</span></div>';
    h += '<div class="workload-divider">&#183;</div>';
    h += '<div class="workload-stat"><span class="ws-num">13</span><span class="ws-label">Categories</span></div>';
    h += '<div class="workload-divider">&#183;</div>';
    h += '<div class="workload-stat"><span class="ws-num ws-active">' + alreadyActive + '</span><span class="ws-label">Already Active</span></div>';
    h += '<div class="workload-divider">&#183;</div>';
    h += '<div class="workload-stat"><span class="ws-num">' + notYet + '</span><span class="ws-label">Not Yet Started</span></div>';
    h += '</div>';
    h += '<div class="workload-status">';
    h += '<span class="ws-status-item"><span class="status-dot complete"></span> Complete (' + (sc['complete']||0) + ')</span>';
    h += '<span class="ws-status-item"><span class="status-dot in-progress"></span> In Progress (' + (sc['in-progress']||0) + ')</span>';
    h += '<span class="ws-status-item"><span class="status-dot early-stage"></span> Early Stage (' + (sc['early-stage']||0) + ')</span>';
    h += '<span class="ws-status-item"><span class="status-dot not-started"></span> Not Started (' + notYet + ')</span>';
    h += '</div>';
    h += '<div class="workload-about"><button class="about-toggle" onclick="var d=document.getElementById(\\'aboutDetail\\');if(d.style.display===\\'none\\'){d.style.display=\\'block\\';this.textContent=\\'About this module \\u25b4\\';}else{d.style.display=\\'none\\';this.textContent=\\'About this module \\u25be\\';}">About this module &#9662;</button>';
    h += '<div id="aboutDetail" style="display:none;margin-top:12px;font-size:0.82rem;color:var(--slate);line-height:1.6;">';
    h += '<p><strong>Sources:</strong> Comparable city plans (Keene, South Portland, Burien), Housing Blue Ribbon Committee work plan, Planning Board recommendations, Places to Live Dialogue, 2022 RKG Housing Market Study, reviewer feedback, and advocate input.</p>';
    h += '<p><strong>Key context:</strong> Portsmouth vacancy rate 1.86%, below the 4-6% functional threshold. RKG projects demand for 3,124 additional units, 52% at 80% AMI or below. GIS analysis shows 85.8% of residential land zoned exclusively single-family, 69.9% of parcels out of compliance.</p>';
    h += '</div></div>';
    h += '</div>';
  }
"""

workload_css = """
.workload-summary{background:var(--white);border:1px solid var(--border);border-radius:var(--radius);padding:16px 20px;margin-bottom:20px}
.workload-stats{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin-bottom:10px}
.workload-stat{display:flex;align-items:baseline;gap:5px}
.ws-num{font-family:'DM Serif Display',Georgia,serif;font-size:1.4rem;color:var(--navy)}
.ws-num.ws-active{color:var(--coral)}
.ws-label{font-size:0.72rem;color:var(--slate);text-transform:uppercase;letter-spacing:0.05em}
.workload-divider{color:#ccc;margin:0 2px}
.workload-status{display:flex;gap:16px;flex-wrap:wrap;font-size:0.8rem;color:var(--slate);margin-bottom:10px;border-top:1px solid var(--border);padding-top:10px}
.ws-status-item{display:flex;align-items:center;gap:5px}
.workload-about{border-top:1px solid var(--border);padding-top:10px}
.about-toggle{background:none;border:none;font-size:0.78rem;color:var(--slate);cursor:pointer;padding:0;font-family:inherit}
.about-toggle:hover{color:var(--navy)}
"""

if ip_start > 0 and ip_end > 0:
    old_block = c[ip_start:ip_end]
    c = c.replace(old_block, new_block)
    c = c.replace('</style>', workload_css + '</style>', 1)
    print('Intro replaced:', 'workload-summary' in c)
else:
    print('ERROR: block not found')

with open('housing/hap-explorer.html', 'w') as f:
    f.write(c)

print('Done. Final size:', len(c))