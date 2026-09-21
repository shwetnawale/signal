import subprocess, json, urllib.request

proc = subprocess.Popen(
    ['git', 'credential', 'fill'],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
out, _ = proc.communicate(b'protocol=https\nhost=github.com\n\n')
lines = {}
for l in out.decode().split('\n'):
    if '=' in l:
        k, v = l.split('=', 1)
        lines[k.strip()] = v.strip()
token = lines.get('password', '')

headers = {
    'Authorization': 'token ' + token,
    'Content-Type': 'application/json',
    'Accept': 'application/vnd.github.v3+json'
}

# Enable GitHub Pages on main branch / root
data = json.dumps({'source': {'branch': 'main', 'path': '/'}}).encode()
req = urllib.request.Request(
    'https://api.github.com/repos/shwetnawale/signal/pages',
    data=data, headers=headers, method='POST'
)
try:
    resp = urllib.request.urlopen(req)
    info = json.loads(resp.read())
    print("Pages enabled:", info.get('html_url', ''))
except urllib.request.HTTPError as e:
    body = e.read().decode()
    if 'already enabled' in body.lower() or '409' in str(e.code):
        print("Pages already enabled - checking URL...")
        # GET pages info
        req2 = urllib.request.Request(
            'https://api.github.com/repos/shwetnawale/signal/pages',
            headers=headers
        )
        try:
            r2 = urllib.request.urlopen(req2)
            info2 = json.loads(r2.read())
            print("Pages URL:", info2.get('html_url', ''))
        except Exception as e2:
            print("GET pages error:", e2)
    else:
        print("Error:", e.code, body[:400])
