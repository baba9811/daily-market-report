"""Export OpenAPI JSON spec from the FastAPI app without running the server."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    """Generate openapi.json from the FastAPI app."""
    from daily_scheduler.entrypoints.api.app import create_app

    app = create_app()
    spec = app.openapi()
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("openapi.json")
    output.write_text(json.dumps(spec, indent=2, ensure_ascii=False))
    print(f"OpenAPI spec written to {output}")


if __name__ == "__main__":
    main()
