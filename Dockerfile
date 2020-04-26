FROM python:3-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement=./requirements.txt

COPY bertlesherp/ ./bertlesherp/

EXPOSE 80

ENTRYPOINT ["python3", "-m", "bertlesherp"]
