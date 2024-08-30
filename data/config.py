# API credentials
API_ID = 1234  # Replace with your actual API ID
API_HASH = 'BOTPROD!'  # Replace with your actual API Hash

# Delays configuration
DELAYS = {
    'ACCOUNT': [5, 15],  # Delay between connections to accounts (more accounts = longer delay)
    'TASK': [5, 10],  # Delay after completing a task
}

# Referral ID
REF = 'iR4blXAGmd0CIEPNJ-5ts'  # Your referral ID

# Proxy configuration
PROXY = {
    "USE_PROXY_FROM_FILE": False,  # True: use proxy from file, False: use proxy from accounts.json
    "PROXY_PATH": "data/proxy.txt",  # Path to the proxy file
    "TYPE": {
        "TG": "http",  # Proxy type for Telegram client. Options: "socks4", "socks5", "http"
        "REQUESTS": "http"  # Proxy type for requests. "http" for HTTP/HTTPS, "socks5" for SOCKS5
    }
}

# Directory for session files (do not change)
WORKDIR = "sessions/"

# Timeout configuration
TIMEOUT = 30  # Timeout in seconds for checking accounts validity

SOFT_INFO = 'Fixed by botprod!'
