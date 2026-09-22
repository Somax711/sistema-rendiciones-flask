import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Rate Limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "100 per hour"],
    storage_uri=os.environ.get("RATELIMIT_STORAGE_URL", "memory://"),
    strategy="fixed-window",
)