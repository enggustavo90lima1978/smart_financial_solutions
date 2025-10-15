from fastapi import APIRouter, Depends, UploadFile

from src.schemas import ApiKeyInput, UserInput
from src.services import Chat, DataHandler, get_chat_service

router = APIRouter()
data_handler = DataHandler()


def get_chat_dependency() -> Chat:
    chat_service = get_chat_service()

    return chat_service


@router.post('/upload', status_code=201)
async def csv_input(
    separator: str,
    file: UploadFile,
):
    response = await data_handler.load_csv(file, separator)

    return {'data': response}


@router.post('/prompt', status_code=201)
async def prompt_model(input: UserInput, chat: Chat = Depends(get_chat_dependency)):
    response = await chat.send_prompt(input.request)
    return response


@router.put('/change-model', status_code=200)
async def change_model(model: str, chat: Chat = Depends(get_chat_dependency)):
    response = await chat.change_model(model)
    return response


@router.post('/send-key', status_code=201)
async def send_key(input: ApiKeyInput, chat: Chat = Depends(get_chat_dependency)):
    response = await chat.update_api_key(input)

    # Força a recriação da instância do chat com a nova chave
    get_chat_service(force_recreate=True)

    return response
