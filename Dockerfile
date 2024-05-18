FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt && pip cache purge

ARG PORT

EXPOSE ${PORT:-8501}

CMD streamlit run --server.port ${PORT:-8501} src/app.py