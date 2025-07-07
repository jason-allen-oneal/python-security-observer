#!/usr/bin/env python3

"""
Configuration settings for HTTP Security Observer
"""

# API Configuration
API_BASE_URL = 'https://http-observatory.security.mozilla.org/api/v1/'
API_TIMEOUT = 30  # seconds
API_RETRY_ATTEMPTS = 3

# Scan Configuration
SCAN_CHECK_INTERVAL = 5  # seconds between status checks
SCAN_COOLDOWN_WAIT = 180  # seconds to wait during cooldown

# Output Configuration
MAX_DESCRIPTION_LENGTH = 80
DEFAULT_OUTPUT_FORMAT = 'table'  # 'table', 'json', 'csv'

# Validation
ALLOWED_DOMAINS = []  # Empty list means all domains allowed
BLOCKED_DOMAINS = []  # Domains to block

# Logging
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = None  # None means console only 