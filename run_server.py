#!/usr/bin/env python
"""
Render startup script with error capture for Metabolic City API
"""

import sys
import os
import subprocess

print("=" * 80, file=sys.stdout, flush=True)
print("METABOLIC CITY API - STARTUP WRAPPER", file=sys.stdout, flush=True)
print("=" * 80, file=sys.stdout, flush=True)
print(f"Python: {sys.version}", file=sys.stdout, flush=True)
print(f"CWD: {os.getcwd()}", file=sys.stdout, flush=True)
print(f"PYTHONUNBUFFERED: {os.getenv('PYTHONUNBUFFERED', 'not set')}", file=sys.stdout, flush=True)
print("=" * 80, file=sys.stdout, flush=True)

# Verify module structure
print("\n[*] Verifying module structure...", file=sys.stdout, flush=True)
try:
    import metabolic_city
    print(f"[OK] metabolic_city package found at: {metabolic_city.__file__}", file=sys.stdout, flush=True)
    
    from metabolic_city.api import server
    print(f"[OK] metabolic_city.api.server module loaded", file=sys.stdout, flush=True)
    
    from metabolic_city.config import settings
    print(f"[OK] metabolic_city.config.settings loaded", file=sys.stdout, flush=True)
    print(f"    - Pipeline enabled: {settings.settings.pipeline_enabled}", file=sys.stdout, flush=True)
    print(f"    - API host: {settings.settings.api_host}", file=sys.stdout, flush=True)
    print(f"    - API port: {settings.settings.api_port}", file=sys.stdout, flush=True)
except Exception as e:
    print(f"[ERROR] Module verification failed: {type(e).__name__}: {str(e)}", file=sys.stdout, flush=True)
    import traceback
    traceback.print_exc(file=sys.stdout)
    sys.exit(1)

# Start uvicorn
print("\n[*] Starting uvicorn server...", file=sys.stdout, flush=True)
print(f"[*] Command: python -m uvicorn metabolic_city.api.server:app --host 0.0.0.0 --port 8000 --log-level info", file=sys.stdout, flush=True)
print("=" * 80, file=sys.stdout, flush=True)
print("", file=sys.stdout, flush=True)

sys.stdout.flush()
sys.stderr.flush()

# Run uvicorn directly in this process
try:
    import uvicorn
    uvicorn.run(
        "metabolic_city.api.server:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
except Exception as e:
    print(f"\n[ERROR] UVICORN STARTUP ERROR: {type(e).__name__}: {str(e)}", file=sys.stdout, flush=True)
    import traceback
    traceback.print_exc(file=sys.stdout)
    sys.exit(1)
