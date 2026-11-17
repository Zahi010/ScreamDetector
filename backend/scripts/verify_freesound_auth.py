"""Verify Freesound API Authentication (Stage 8.8 Part A).

Securely tests:
1. Loading FREESOUND_API_KEY from .env / environment without printing or leaking secrets.
2. Live minimal API request to Freesound API v2 with Token authentication.
3. Diagnostic reporting for missing, invalid, or working credentials.

Usage:
  python scripts/verify_freesound_auth.py
"""

from __future__ import annotations

import json
import logging
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.config import BACKEND_DIR, PROJECT_ROOT, get_freesound_api_key, load_project_env

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("verify_freesound_auth")


def verify_freesound_access() -> dict:
    """Verify Freesound API key and perform minimal live authenticated request."""
    # Ensure environment is loaded from project-root .env without overriding active env vars
    loaded_env = load_project_env(override=False)
    key = get_freesound_api_key()

    result = {
        "key_present": bool(key),
        "key_length": len(key) if key else 0,
        "env_file_loaded": str(loaded_env) if loaded_env else None,
        "auth_succeeded": False,
        "auth_method_used": None,
        "http_status": None,
        "diagnostic_status": "UNKNOWN",
        "diagnostic_message": "",
        "api_response_summary": None,
    }

    if not key:
        result["diagnostic_status"] = "MISSING_KEY"
        result["diagnostic_message"] = (
            f"FREESOUND_API_KEY is not configured or empty in project-root .env.\n"
            f"Expected file: {PROJECT_ROOT / '.env'}\n"
            "Action required: Add 'FREESOUND_API_KEY=<your_api_key>' to your project-root .env file "
            "and save the file."
        )
        return result

    # 1. Test standard Freesound API v2 Token authentication via Authorization header
    # Endpoint: /apiv2/search/text/ with minimal payload (page_size=1)
    test_url = "https://freesound.org/apiv2/search/text/?query=festival&page_size=1&fields=id,name,license"
    headers = {
        "Authorization": f"Token {key}",
        "User-Agent": "FestivalScreamDetector/1.0",
    }
    req = urllib.request.Request(test_url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result["http_status"] = resp.status
            if resp.status == 200:
                result["auth_succeeded"] = True
                result["auth_method_used"] = "Authorization Header (Token <key>)"
                result["diagnostic_status"] = "AUTHENTICATION_SUCCESS"
                data = json.loads(resp.read().decode("utf-8"))
                result["api_response_summary"] = {
                    "total_results_accessible": data.get("count", 0),
                    "query_returned_results": len(data.get("results", [])),
                    "sample_sound_id": data.get("results", [{}])[0].get("id") if data.get("results") else None,
                }
                result["diagnostic_message"] = "Freesound API v2 authentication verified successfully via Authorization header."
                return result
    except urllib.error.HTTPError as e:
        result["http_status"] = e.code
        if e.code == 401:
            # Try query param fallback ?token=<key>
            pass
        elif e.code == 429:
            result["diagnostic_status"] = "RATE_LIMITED"
            result["diagnostic_message"] = "HTTP 429: Rate limit exceeded on Freesound API. Please back off before retrying."
            return result
        else:
            result["diagnostic_status"] = "HTTP_ERROR"
            result["diagnostic_message"] = f"HTTP {e.code}: {e.reason}"
            return result
    except Exception as e:
        result["diagnostic_status"] = "NETWORK_ERROR"
        result["diagnostic_message"] = f"Network connection failed: {e}"
        return result

    # 2. Test query parameter fallback: ?token=<key>
    param_url = f"https://freesound.org/apiv2/search/text/?query=festival&page_size=1&fields=id,name,license&token={key}"
    req_param = urllib.request.Request(param_url, headers={"User-Agent": "FestivalScreamDetector/1.0"})

    try:
        with urllib.request.urlopen(req_param, timeout=10) as resp:
            result["http_status"] = resp.status
            if resp.status == 200:
                result["auth_succeeded"] = True
                result["auth_method_used"] = "Query Parameter (?token=<key>)"
                result["diagnostic_status"] = "AUTHENTICATION_SUCCESS"
                data = json.loads(resp.read().decode("utf-8"))
                result["api_response_summary"] = {
                    "total_results_accessible": data.get("count", 0),
                    "query_returned_results": len(data.get("results", [])),
                    "sample_sound_id": data.get("results", [{}])[0].get("id") if data.get("results") else None,
                }
                result["diagnostic_message"] = "Freesound API v2 authentication verified successfully via query parameter."
                return result
    except urllib.error.HTTPError as e:
        result["http_status"] = e.code
        if e.code == 401:
            result["diagnostic_status"] = "INVALID_CREDENTIALS"
            result["diagnostic_message"] = (
                "HTTP 401 Unauthorized: The configured FREESOUND_API_KEY was rejected by Freesound.org.\n"
                "Please verify your API key at https://freesound.org/help/developers/."
            )
        else:
            result["diagnostic_status"] = "HTTP_ERROR"
            result["diagnostic_message"] = f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        result["diagnostic_status"] = "NETWORK_ERROR"
        result["diagnostic_message"] = f"Network connection failed: {e}"

    return result


def main() -> int:
    print("=" * 80)
    print("STAGE 8.8 PART A — FREESOUND API AUTHENTICATION VERIFICATION")
    print("=" * 80)
    res = verify_freesound_access()

    print(f"Project Root       : {PROJECT_ROOT}")
    if res.get("env_file_loaded"):
        print(f"Env File Loaded    : {res['env_file_loaded']}")
    print(f"Key Present        : {res['key_present']}")
    print(f"Key Length         : {res['key_length']} characters (Secret masked)")
    print(f"Authentication OK  : {res['auth_succeeded']}")
    if res["auth_method_used"]:
        print(f"Auth Method Used   : {res['auth_method_used']}")
    if res["http_status"]:
        print(f"HTTP Status Code   : {res['http_status']}")
    print(f"Diagnostic Status  : {res['diagnostic_status']}")
    print(f"Diagnostic Detail  :\n  {res['diagnostic_message']}")

    if res["api_response_summary"]:
        print("\nLive Freesound Query Results:")
        print(f"  Total Sounds Accessible : {res['api_response_summary']['total_results_accessible']}")
        print(f"  Returned In Test Query  : {res['api_response_summary']['query_returned_results']}")
        print(f"  Sample Sound ID         : {res['api_response_summary']['sample_sound_id']}")

    print("=" * 80)
    return 0 if res["auth_succeeded"] else 1


if __name__ == "__main__":
    sys.exit(main())
