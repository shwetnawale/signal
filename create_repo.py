import subprocess, json, urllib.request, sys

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
print("Token found:", bool(token), "Len:", len(token))
if not token:
    sys.exit(1)

data = json.dumps({
    'name': 'signal',
    'private': False,
    'description': 'Daily Trading Signal - BUY or SELL',
    'auto_init': False
}).encode()

req = urllib.request.Request(
    'https://api.github.com/user/repos', data=data,
    headers={
        'Authorization': 'token ' + token,
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github.v3+json'
    }
)
try:
    resp = urllib.request.urlopen(req)
    info = json.loads(resp.read())
    print("Repo created:", info.get('html_url', ''))
    print("Clone URL:", info.get('clone_url', ''))
except urllib.request.HTTPError as e:
    body = e.read().decode()
    print("API error:", e.code, body[:400])
