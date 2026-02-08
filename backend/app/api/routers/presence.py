# from fastapi import APIRouter
# from app.core.database import SessionDep

# router = APIRouter(prefix="/presence", tags=["presence"])


# @router.post("/")
# async def mark_presence(data: PresenceCreate, session: SessionDep):
#     """
#     Salva a presença do aluno. (Aqui você criaria uma tabela 'Presence' no futuro)
#     Por enquanto, vamos apenas logar ou salvar simulado.
#     """
#     print(f"Presença marcada: {data.user_name} na rota {data.route_id}")
#     # TODO: Criar tabela de presença no database.py e salvar aqui
#     return {"message": "Presença confirmada com sucesso"}
