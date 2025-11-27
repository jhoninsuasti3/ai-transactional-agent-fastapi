"""Application constants.

This module contains true constants - values that never change throughout
the application lifecycle. For messages, see messages.py module.
"""

# ============================================================================
# ENVIRONMENT NAMES
# ============================================================================

ENV_DEVELOPMENT = "development"
ENV_PRODUCTION = "production"
ENV_TEST = "test"

# ============================================================================
# HTTP STATUS CODES
# ============================================================================

HTTP_STATUS_OK = 200
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_CONFLICT = 409
HTTP_STATUS_INTERNAL_ERROR = 500
HTTP_STATUS_SERVICE_UNAVAILABLE = 503
