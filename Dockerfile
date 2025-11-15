FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip

# 1) requirements.txt 먼저 복사
COPY requirements.txt .

RUN pip install -r requirements.txt

# 2) web 폴더 전체 복사
COPY web/ .

EXPOSE 5001

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]
