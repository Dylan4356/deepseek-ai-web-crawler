import csv

from models.fellowship import Fellowship

import csv

from typing import List, Set, Dict

def is_complete_fellowship(fellowship: Dict, required_keys: List[str]) -> bool:
    """
    Check if the fellowship dictionary contains all required keys and non-empty values.
    """
    for key in required_keys:
        if key not in fellowship or not fellowship[key]:
            return False
    return True

def is_duplicate_fellowship(program_name: str, seen_programs: Set[str]) -> bool:
    """
    Check if this fellowship program has already been seen.
    """
    return program_name in seen_programs

def save_fellowships_to_csv(fellowships, path="complete_fellowships.csv"):
    if not fellowships:
        print("No fellowships to save.")
        return

    # Use the keys from the first item
    keys = fellowships[0].keys() if isinstance(fellowships[0], dict) else fellowships[0].__dict__.keys()

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for fship in fellowships:
            writer.writerow(fship if isinstance(fship, dict) else fship.__dict__)

def load_fellowships(path="fellowships.csv") -> list[Fellowship]:
    """
    Load fellowship data from a CSV file.
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [Fellowship(**row) for row in reader]
