

FROM python:3.11-slim as deployment

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt && pip cache purge

ARG PORT

EXPOSE 8501

CMD streamlit run --server.port 8501 src/app.py

