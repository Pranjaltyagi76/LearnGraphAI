"""Small production measurements without request bodies, addresses, or credentials."""

import json
import sys


def emit_request_metrics(request_id: str, status: int, elapsed_ms: float, first: bool) -> None:
    metrics = {
        "event": "learngraph_request",
        "request_id": request_id,
        "status": status,
        "api_ms": round(elapsed_ms, 2),
        "instance_first_request": first,
    }
    if sys.platform == "linux":
        try:
            import resource

            # Linux reports the process high-water resident set in KiB. This is not
            # provider-billed memory or an isolated per-request allocation.
            metrics["peak_process_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        except (ImportError, OSError):
            pass
    print(json.dumps(metrics, separators=(",", ":")), flush=True)
