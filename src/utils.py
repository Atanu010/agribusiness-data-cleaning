"""
Utility module for logging, cryptographic file hashing, directory management,
and data validation formatting across the agribusiness data cleaning framework.
"""

import hashlib
import logging
import os
import sys
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional


def setup_logger(
    name: str = "agribusiness_cleaner",
    log_file: Optional[Path] = None,
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Configures and returns a centralized, standardized logger.

    Args:
        name: Name of the logger instance.
        log_file: Optional Path to log output file.
        level: Logging verbosity level (default INFO).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | [%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger


logger = setup_logger()


def calculate_sha256(filepath: Path) -> str:
    """
    Computes the SHA-256 cryptographic digest of a file to ensure provenance.

    Args:
        filepath: Path to the target file.

    Returns:
        str: Hexadecimal SHA-256 hash string.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Target file not found: {filepath}")

    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def ensure_directory(path: Path) -> Path:
    """
    Ensures that a specified directory path exists, creating it if needed.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def timeit(func: Callable) -> Callable:
    """
    Decorator to measure and log the execution runtime of a function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Executing '{func.__name__}'...")
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        logger.info(f"Finished '{func.__name__}' in {elapsed:.4f} seconds.")
        return result
    return wrapper
