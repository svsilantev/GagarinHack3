FROM python:latest

WORKDIR /api

COPY . .

RUN pip install -r requirements.txt

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
