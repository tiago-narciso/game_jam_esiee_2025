import csv
import os
from dataclasses import dataclass
from typing import List, Tuple


LEADERBOARD_FILENAME = "leaderboard.csv"


def _get_storage_path() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..")
    # Store at project root alongside game_jam.py for simplicity
    root_dir = os.path.abspath(os.path.join(base_dir, ".."))
    return os.path.join(root_dir, LEADERBOARD_FILENAME)


@dataclass
class LeaderboardEntry:
    username: str
    score: int


def load_entries() -> List[LeaderboardEntry]:
    path = _get_storage_path()
    if not os.path.exists(path):
        return []
    entries: List[LeaderboardEntry] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 2:
                continue
            name = row[0]
            try:
                score = int(row[1])
            except ValueError:
                continue
            entries.append(LeaderboardEntry(name, score))
    return entries


def save_entries(entries: List[LeaderboardEntry]) -> None:
    path = _get_storage_path()
    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for e in entries:
            writer.writerow([e.username, e.score])


def add_score(username: str, score: int) -> Tuple[int, List[LeaderboardEntry]]:
    """Add a score, sort descending by score, persist, and return the 1-based rank.

    Returns (rank, sorted_entries).
    """
    entries = load_entries()
    entries.append(LeaderboardEntry(username=username, score=score))
    # Sort by score desc, then username asc for stability
    entries.sort(key=lambda e: (-e.score, e.username.lower()))
    save_entries(entries)
    # Compute rank (first matching occurrence)
    rank = 1
    for idx, e in enumerate(entries, start=1):
        if e.username == username and e.score == score:
            rank = idx
            break
    return rank, entries


