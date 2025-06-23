from fastapi import APIRouter, Request


router = APIRouter(
    tags=["Connector"],
    prefix="/connector_website",
)


@router.post("/")
async def resend_to_rasa(request: Request) -> None:
    """Пересылка сообщения в Расу."""
    return None
