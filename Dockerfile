FROM python:3.6

WORKDIR /app

COPY . .

RUN apt-get update && \
  apt-get install -y default-jdk && \
  pip install -r requirements.txt && \
  python -m spacy download en_core_web_sm && \
  python -m spacy link en_core_web_sm en_default && \
  python -c "import nltk; nltk.download('stopwords');"

ENTRYPOINT ["python", "server.py"]

