from typing import Any, Dict
from uvicorn.workers import UvicornWorker


class KiUvicornWorker(UvicornWorker):
    CONFIG_KWARGS: Dict[str, Any] = {"loop": "auto", "http": "auto", "lifespan": "off", "ws": "websockets"}
