import sys, time, requests

PROXY = 'http://gceevnmy:fsw0vdnivpwv@31.59.20.176:6754'
IG_USER = 'we_are_here_07'
IG_PASS = 'Navya2012'

# ── 1. Check if account exists publicly ───────────────────────────────────────
print('=' * 50)
print('Step 1: Checking if account exists publicly...')
try:
    r = requests.get(
        f'https://www.instagram.com/{IG_USER}/',
        proxies={'http': PROXY, 'https': PROXY},
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
        timeout=15,
        allow_redirects=True
    )
    if r.status_code == 404:
        print('RESULT: Account NOT FOUND - Instagram returned 404 for this username')
        print('        This means the account @we_are_here_07 does not exist on Instagram')
    elif r.status_code == 200:
        if 'username' in r.text.lower():
            print('RESULT: Account EXISTS - public profile page found')
        else:
            print(f'RESULT: HTTP 200 but could not confirm account data')
    else:
        print(f'RESULT: HTTP {r.status_code}')
    print(f'        URL: {r.url}')
except Exception as e:
    print(f'Public check error: {e}')

# ── 2. Direct login attempt ────────────────────────────────────────────────────
print()
print('=' * 50)
print('Step 2: Trying direct Instagram login with proxy...')
from instagrapi import Client

cl = Client()
cl.set_proxy(PROXY)
cl.set_device(cl.device_settings)
time.sleep(3)

try:
    cl.login(IG_USER, IG_PASS)
    print('LOGIN SUCCESS!')
    cl.dump_settings('session_ig.json')
    print('Session saved to session_ig.json')
except Exception as e:
    print(f'ERROR TYPE : {type(e).__name__}')
    print(f'FULL ERROR : {str(e)[:400]}')

print()
print('=' * 50)
print('Done.')
