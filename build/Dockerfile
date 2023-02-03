FROM python:3.8.16-slim as base
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["python3", "-u", "script.py"]