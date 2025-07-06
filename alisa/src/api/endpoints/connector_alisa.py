from fastapi import APIRouter, Request, Depends

from dependencies import get_rasa_service
from schemas.alisa import Alisa, TextAlisa
from services.rasa import RasaService

router = APIRouter(tags=["Connector"], prefix="/connector-alisa")


@router.post("/")
async def resend_to_rasa(
    request: Request, rasa: RasaService = Depends(get_rasa_service)
) -> Alisa:
    """Алиса"""
    data = await request.json()
    alisa_request = data.get("request", {})
    alisa_session = data.get("session", {})
    if alisa_request["command"].lower() == "стоп":
        return Alisa(
            response=TextAlisa(
                text="До свидания! Если что-то понадобится, обращайтесь!"
            ),
            end_session=True,
        )
    user_id = alisa_session.get("user_id", ""),
    user_message =  alisa_request.get("original_utterance", "")
    if alisa_session and alisa_session.get("new"):
        rasa_response = await rasa.get_rasa(user_id=user_id, message="/greet")
    else:
        rasa_response = await rasa.get_rasa(user_id=user_id, message=user_message)
    list_output = []
    if rasa_response:
        for msg in rasa_response:
            list_output.append(msg.get("text"))
        result = "\n".join(list_output)
        return Alisa(response=TextAlisa(text=result))
    return Alisa(response=TextAlisa(text="Извините, произошла ошибка"))
