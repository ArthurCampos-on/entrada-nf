"""logger.py — log colorido no terminal + arquivo rotacionado."""
import sys
from pathlib import Path
from loguru import logger

def configurar(nivel="INFO", arquivo="data/logs/nbs_agent.log"):
    logger.remove()
    logger.add(sys.stderr, level=nivel, colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:<7}</level> | <level>{message}</level>")
    Path(arquivo).parent.mkdir(parents=True, exist_ok=True)
    logger.add(arquivo, level=nivel, rotation="5 MB", retention="15 days",
        encoding="utf-8", format="{time:YYYY-MM-DD HH:mm:ss} | {level:<7} | {message}")

log = logger
