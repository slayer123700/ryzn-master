# Yumeko/modules/role_assign.py
import json
import os
from typing import Tuple
from config import config

OWNER_ID = config.OWNER_ID
SPECIAL_USER_ID = 7876439267  # Replace with your special user ID
sudoers_file = "sudoers.json"

def load_roles() -> dict:
    """
    Loads roles from sudoers.json.
    If file doesn't exist, returns default empty roles.
    """
    if not os.path.exists(sudoers_file):
        return {"Hokages": [], "Jonins": [], "Chunins": [], "Genins": []}
    with open(sudoers_file, "r") as f:
        return json.load(f)

def get_user_rank(user_id: int) -> str:
    """
    Returns rank based on sudoers.json.
    If user not in any role, returns 'Normal Civilian'.
    """
    roles = load_roles()
    if user_id in roles.get("Hokages", []):
        return "Hokage"
    if user_id in roles.get("Jonins", []):
        return "Jonin"
    if user_id in roles.get("Chunins", []):
        return "Chunin"
    if user_id in roles.get("Genins", []):
        return "Genin"
    return "Normal Civilian"

def get_elite_power(user_id: int) -> str:
    """
    Returns elite power.
    Only Owner or Special User get elite power.
    """
    if user_id == OWNER_ID:
        return "Elite Master ⚜️"
    if user_id == SPECIAL_USER_ID:
        return "Princess 👑"
    return "No Elite Power"

def get_hierarchy(user_id: int) -> Tuple[str, str]:
    """
    Returns a tuple (rank, elite_power)
    """
    return get_user_rank(user_id), get_elite_power(user_id)