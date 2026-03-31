"""
Traffic Alert Photographer (TAP) — entry point.

  python run.py

Starts the poller in a background thread and the web server in the main thread.
See .env.example for configuration options.
"""

import logging
import threading

from tap.config import load
from tap import poller, server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

if __name__ == "__main__":
    cfg = load()
    threading.Thread(target=poller.run, args=(cfg,), daemon=True, name="poller").start()
    server.serve(cfg)
