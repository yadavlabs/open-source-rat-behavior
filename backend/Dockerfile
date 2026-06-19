FROM ubuntu:20.04
#FROM python:3.8.10-slim
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.8 \
    python3-pip \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3.8 /usr/bin/python

COPY requirements.txt .

RUN pip3 install --no-cache-dir pip==22.3.1 setuptools==65.5.1 wheel==0.38.4
RUN pip3 install --no-cache-dir -r requirements.txt --no-deps
#RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel && \
#    pip3 install --no-cache-dir -r requirements.txt --no-deps
#RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
#    pip install --no-cache-dir -r requirements.txt --no-dependencies || \
#    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

#CMD ["python", "application.py", "flask", "run", "--host", "0.0.0.0", "--port", "5000"]
CMD ["flask", "run", "--host", "0.0.0.0"]