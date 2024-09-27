FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    openssh-client \
    openssl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-c"]
WORKDIR /quantum
COPY requirements.txt main.py service.ipynb ./
RUN pip install -r requirements.txt

ENV FLASK_APP="main.py"

CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0"]
