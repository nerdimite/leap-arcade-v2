from fastapi import Request
from leap.service.container import ServiceContainer


def get_container(request: Request) -> ServiceContainer:
    """FastAPI dependency — returns the ServiceContainer from leap.state."""
    return request.app.state.container
