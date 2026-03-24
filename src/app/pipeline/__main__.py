"""`python -m app.pipeline` — mesmo CLI que `app.pipeline.runner`."""
from __future__ import annotations

from app.pipeline.runner import main

if __name__ == "__main__":
    main()
