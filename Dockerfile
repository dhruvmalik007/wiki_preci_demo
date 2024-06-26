

FROM python:3.11-slim as deployment

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt && pip cache purge

ARG PORT

EXPOSE ${PORT:-8000}

CMD streamlit run --server.port ${PORT:-8000} app.py

