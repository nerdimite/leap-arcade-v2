"""Auth service — login business logic."""

from typing import TYPE_CHECKING

from leap.core.auth import encode_token, verify_event_code
from leap.core.context_manager import ContextManager
from leap.service.exceptions import InvalidEventCodeException, PlayerNotFoundException
from leap.types.auth import LoginDTO
from leap.types.player import PlayerDTO

if TYPE_CHECKING:
    from leap.dao.player_dao import PlayerDAO


class AuthService:
    """Handles player authentication. Stateless — all identity lives in the JWT."""

    def __init__(self, context_manager: ContextManager, player_dao: "PlayerDAO") -> None:
        self.ctx = context_manager
        self.player_dao = player_dao

    async def login(self, corp_id: str, event_code: str) -> LoginDTO:
        """Normalise corp_id, verify player exists and event code matches, issue JWT.

        Raises:
            PlayerNotFoundException: corp_id not found in players table.
            InvalidEventCodeException: event code does not match settings.EVENT_CODE.
        """
        normalised_id = corp_id.strip().lower()

        async with self.ctx.session() as session:
            player: PlayerDTO | None = await self.player_dao.get_by_id(session, normalised_id)

        if player is None:
            raise PlayerNotFoundException(normalised_id)

        if not verify_event_code(event_code):
            raise InvalidEventCodeException()

        token = encode_token(player.id, player.display_name)
        return LoginDTO(access_token=token, player=player)
