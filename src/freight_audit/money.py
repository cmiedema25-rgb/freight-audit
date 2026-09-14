from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

UTC = ZoneInfo("UTC")
CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def money(value) -> Decimal:
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def record_time(row: dict, iana_tz: str) -> datetime:
    if row.get("timestamp_basis") == "OFFSET":
        return instant(row["recorded_at"])
    naive = datetime.strptime(row["recorded_at"], "%Y-%m-%d %H:%M:%S")
    offset = row.get("utc_offset_minutes")
    if offset is not None:
        return (naive - timedelta(minutes=int(offset))).replace(tzinfo=UTC)
    return naive.replace(tzinfo=ZoneInfo(iana_tz)).astimezone(UTC)


def appointment_time(value: str, iana_tz: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(
        tzinfo=ZoneInfo(iana_tz)
    ).astimezone(UTC)


def in_service_interval(at: datetime, row: dict) -> bool:
    return instant(row["valid_from_utc"]) <= at and (
        not row.get("valid_to_utc") or at < instant(row["valid_to_utc"])
    )


def rounded_minutes(minutes: int, increment: int, mode: str):
    if minutes <= 0 or increment <= 0:
        return 0
    if mode == "CEILING_TO_INCREMENT":
        units = (minutes + increment - 1) // increment
    elif mode == "FLOOR_TO_INCREMENT":
        units = minutes // increment
    elif mode == "HALF_UP_TO_INCREMENT":
        units = (2 * minutes + increment) // (2 * increment)
    else:
        return None
    return units * increment
