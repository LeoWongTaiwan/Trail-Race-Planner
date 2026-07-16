#!/usr/bin/env python3
"""Weekly Trail Planner data maintenance.

This safe first-stage updater:
1. Maintains a rolling 365-day window.
2. Recomputes registration status from open/close dates.
3. Removes races whose race date is outside the window.
4. Writes a machine-readable update summary.

External source discovery is intentionally modular. Add verified source adapters
later instead of marking uncertain events as open.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RACES_PATH = ROOT / "data" / "races.json"
CHANGES_PATH = ROOT / "data" / "changes.json"


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def computed_status(race: dict[str, Any], today: date) -> str:
    race_date = parse_date(race.get("date"))
    registration_open = parse_date(race.get("registrationOpen"))
    deadline = parse_date(race.get("deadline"))

    if race.get("cancelled"):
        return "cancelled"
    if race_date and race_date < today:
        return "finished"
    if deadline and deadline < today:
        return "closed"
    if registration_open and registration_open > today:
        return "soon"
    if deadline and deadline >= today:
        return "open"

    # Unknown dates must never be promoted to open automatically.
    return "pending"


def main() -> None:
    today = date.today()
    window_end = today + timedelta(days=365)

    payload = json.loads(RACES_PATH.read_text(encoding="utf-8"))
    previous_races = payload.get("races", [])
    previous_by_id = {race["id"]: race for race in previous_races if race.get("id")}

    kept: list[dict[str, Any]] = []
    status_changes: list[dict[str, str]] = []
    removed: list[str] = []

    for race in previous_races:
        race_date = parse_date(race.get("date"))
        if race_date and not (today <= race_date <= window_end):
            removed.append(race.get("name", race.get("id", "未命名")))
            continue

        old_status = race.get("status", "pending")
        new_status = computed_status(race, today)
        race["status"] = new_status
        race["lastProcessedAt"] = today.isoformat()

        if old_status != new_status:
            status_changes.append(
                {
                    "id": race.get("id", ""),
                    "name": race.get("name", ""),
                    "from": old_status,
                    "to": new_status,
                }
            )
        kept.append(race)

    kept.sort(key=lambda race: (race.get("date") or "9999-12-31", race.get("name") or ""))

    payload["meta"] = {
        **payload.get("meta", {}),
        "lastUpdated": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "windowStart": today.isoformat(),
        "windowEnd": window_end.isoformat(),
        "raceCount": len(kept),
        "updateMode": "scheduled-status-refresh",
    }
    payload["races"] = kept
    RACES_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    changes = {
        "updatedAt": payload["meta"]["lastUpdated"],
        "windowStart": today.isoformat(),
        "windowEnd": window_end.isoformat(),
        "raceCount": len(kept),
        "statusChanges": status_changes,
        "removedOutsideWindow": removed,
        "newRaces": [],
        "note": (
            "This stage automatically maintains dates and statuses. "
            "Verified external source adapters can be added later."
        ),
    }
    CHANGES_PATH.write_text(
        json.dumps(changes, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"Updated {len(kept)} races; "
        f"{len(status_changes)} status changes; "
        f"{len(removed)} removed."
    )


if __name__ == "__main__":
    main()
