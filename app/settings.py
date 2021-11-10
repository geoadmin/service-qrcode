import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
ENV_FILE = os.getenv('ENV_FILE', None)
if ENV_FILE:
    from dotenv import load_dotenv
    print(f"Running locally hence injecting env vars from {ENV_FILE}")
    load_dotenv(ENV_FILE, override=True, verbose=True)

# Definition of the allowed domains for CORS implementation
ALLOWED_DOMAINS_STRING = os.getenv('ALLOWED_DOMAINS')
if ALLOWED_DOMAINS_STRING is None or ALLOWED_DOMAINS_STRING == "":
    logger.error("No allowed domains pattern from env was found")
    raise RuntimeError("Environment variable $ALLOWED_DOMAINS was not set")

ALLOWED_DOMAINS = ALLOWED_DOMAINS_STRING.split(',')
TRAP_HTTP_EXCEPTIONS = True

CACHE_CONTROL = os.getenv('CACHE_CONTROL', 'public, max-age=31536000')
