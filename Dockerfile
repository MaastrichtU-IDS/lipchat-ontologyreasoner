FROM python:3.6

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt && \
  python -m spacy download en_core_web_sm && \
  python -m spacy link en_core_web_sm en_default

ENTRYPOINT ["python", "server.py"]

