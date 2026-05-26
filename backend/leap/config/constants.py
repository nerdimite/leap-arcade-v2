"""Application constants.

Values that are config-shaped but not env-driven — kept in code so changes are reviewable.
Single source of truth for the game registry; consumed by the lobby service and by the
``game_sessions.game_id`` CHECK constraint.
"""

from typing import Dict, List

GAMES: List[Dict[str, str]] = [
    {"id": "wiki", "display_name": "Wikipedia Speed Run"},
    {"id": "rapid_fire", "display_name": "Rapid Fire Quiz"},
    {"id": "pinpoint", "display_name": "Pinpoint"},
    {"id": "picture", "display_name": "Picture Illustration"},
    {"id": "four_pics", "display_name": "Four Pics One Lie"},
    {"id": "crossword", "display_name": "Crossword"},
]

GAME_IDS: List[str] = [game["id"] for game in GAMES]

# Picture Illustration — global session timer (ms). Consumed by PictureService + client display.
PICTURE_TIME_LIMIT_MS: int = 300_000

