import re

GITHUB_TOKEN = "STORED_IN_BROWSER"
REPO = "gduffy44-svg/progress-portsmouth-tools"

new_export = '''function doExport() {
  // Fix pros/cons: split strings into arrays
  const cleanActions = ACTIONS.map(a => {
    const c = {...a};
    delete c._isNew;
    ['pros','cons'].forEach(f => {
      if (typeof c[f] === 'string') {
        c[f] = c[f].split('\\n').map(s => s.replace(/^[-•*]\\s*/, '').trim()).filter(Boolean);
      } else if (!Array.isArray(c[f])) {
        c[f] = [];
      }
    });
    return c;
  });
  const evals = Object.values(EVALS).sort((a,b) => a.id < b.id ? -1 : 1);

  // Validate
  const errors = [];
  cleanActions.forEach(a => {
    if (!Array.isArray(a.pros)) errors.push(a.action + ': pros not array');
    if (!Array.isArray(a.cons)) errors.push(a.action + ': cons not array');
  });
  if (errors.length) {
    alert('Validation errors:\\n' + errors.join('\\n'));
    return;
  }

  const actionsJson = JSON.stringify(cleanActions, null, 2);
  const evalsJson = JSON.stringify(evals, null, 2);

  setStatus('Pushing to GitHub...');
  closeModal('export-modal');

  pushToGitHub('housing/hap-actions.json', actionsJson)
    .then(() => pushToGitHub('housing/hap-evaluations.json', evalsJson))
    .then(() => {
      setStatus('Deployed. Live in ~30 seconds.');
      DIRTY.clear();
    })
    .catch(err => {
      setStatus('GitHub push failed: ' + err.message);
      alert('Push failed: ' + err.message + '\\n\\nFalling back to download.');
      downloadJSON(cleanActions, 'hap-actions.json');
      setTimeout(() => downloadJSON(evals, 'hap-evaluations.json'), 400);
    });
}

async function pushToGitHub(path, content) {
  const token = "''' + GITHUB_TOKEN + '''";
  const repo = "''' + REPO + '''";
  const apiUrl = `https://api.github.com/repos/${repo}/contents/${path}`;

  // Get current SHA
  const getRes = await fetch(apiUrl, {
    headers: { 'Authorization': 'token ' + token, 'Accept': 'application/vnd.github.v3+json' }
  });
  if (!getRes.ok) throw new Error(`GET ${path} failed: ${getRes.status}`);
  const getData = await getRes.json();
  const sha = getData.sha;

  // Commit updated file
  const putRes = await fetch(apiUrl, {
    method: 'PUT',
    headers: {
      'Authorization': 'token ' + token,
      'Accept': 'application/vnd.github.v3+json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: `HAP admin update: ${path}`,
      content: btoa(unescape(encodeURIComponent(content))),
      sha: sha
    })
  });
  if (!putRes.ok) {
    const err = await putRes.json();
    throw new Error(err.message || putRes.status);
  }
}
'''

c = open('housing/hap-admin.html').read()
old = re.search(r'function doExport\(\) \{.*?(?=\nfunction downloadJSON)', c, re.DOTALL).group(0)
c = c.replace(old, new_export)
open('housing/hap-admin.html', 'w').write(c)
print('Done')