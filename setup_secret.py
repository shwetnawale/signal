import subprocess, json, urllib.request, base64, sys

# Get token from credential store
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
if not token:
    print("No token found")
    sys.exit(1)

headers = {
    'Authorization': 'token ' + token,
    'Content-Type': 'application/json',
    'Accept': 'application/vnd.github.v3+json'
}

# Step 1: Get nawale_mint repo public key (needed to encrypt the secret)
req = urllib.request.Request(
    'https://api.github.com/repos/shwetnawale/nawale_mint/actions/secrets/public-key',
    headers=headers
)
resp = urllib.request.urlopen(req)
pk_info = json.loads(resp.read())
key_id  = pk_info['key_id']
pub_key = pk_info['key']
print("Got public key, key_id:", key_id)

# Step 2: Encrypt the token using PyNaCl (libsodium)
try:
    from nacl import encoding, public
    pk_bytes = base64.b64decode(pub_key)
    sealed   = public.SealedBox(public.PublicKey(pk_bytes))
    encrypted = base64.b64encode(sealed.encrypt(token.encode())).decode()

    # Step 3: Store as secret SIGNAL_PAT in nawale_mint repo
    data = json.dumps({'encrypted_value': encrypted, 'key_id': key_id}).encode()
    req2 = urllib.request.Request(
        'https://api.github.com/repos/shwetnawale/nawale_mint/actions/secrets/SIGNAL_PAT',
        data=data, headers=headers, method='PUT'
    )
    resp2 = urllib.request.urlopen(req2)
    print("Secret SIGNAL_PAT stored in nawale_mint. Status:", resp2.status)

except ImportError:
    print("PyNaCl not installed - installing...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'PyNaCl', '-q'])
    print("Installed. Run script again.")
except Exception as e:
    print("Error:", e)
