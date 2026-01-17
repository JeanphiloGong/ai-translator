from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_utc_timestamp(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).replace(microsecond=0)


def format_utc_timestamp(value: datetime) -> str:
    normalized = normalize_utc_timestamp(value)
    return normalized.isoformat().replace("+00:00", "Z")


def parse_utc_timestamp(value: str) -> datetime:
    if value.endswith("Z"):
        value = f"{value[:-1]}+00:00"
    return normalize_utc_timestamp(datetime.fromisoformat(value))
