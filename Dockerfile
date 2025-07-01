FROM python:3.12-slim

WORKDIR /app

# Set timezone to Asia/Shanghai (UTC+8)
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y && \
apt-get clean && \
rm -rf /var/lib/apt/lists/* && \
pip install --no-cache-dir uv

COPY pyproject.toml .

RUN uv pip install --system .

COPY . .

EXPOSE 8001

CMD ["python", "main.py"]
