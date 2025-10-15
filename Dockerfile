FROM python:3.11.14-alpine

WORKDIR /app/backend

run pip install --no-cache -r requirements.txt

CMD [ "fastapi", "run", "src/main.py" ]
