"""Repair these three functions. The service and command parser are supplied."""
from datetime import datetime, timezone
from pathlib import Path
from lab01_service import utc_parse, utc_text


def resolve_paths(config, config_path):
    """
    Resolve state paths relative to the configuration file.
    
    change: the paths are now anchored to the parent path, no files are created in the process
    """
    anchor = Path(config_path).resolve().parent

    return {
        key: (anchor / Path(config[key])).resolve()
        for key in ("database", "preview_directory", "log_file")
    }


def choose_until(explicit_until=None, clock=None):
    """
    Use an explicit UTC-normalized end, or capture the current time once.
    
    change: the hardcoded datetime is gone, now the until param is taken into consideration
    and time is normalized to UTC 
    """
    if explicit_until is not None:
        return utc_text(utc_parse(explicit_until))

    current = clock() if clock is not None else datetime.now(timezone.utc)

    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("Use a timezone in every timestamp")

    return utc_text(current)


def execute_job(job, logger):
    """
    Return the actual result on success and an honest failure otherwise.
    
    change: now the success is reported only for the actual success as opposed to the previous state when
    even a failure was reported as a success, also the error message is more robust
    """
    try:
        return 0, job()
    except Exception as exc:
        logger.exception("Job failed")
        return 1, {
            "status": "failed",
            "error": f"{type(exc).__name__}: {exc}",
        }