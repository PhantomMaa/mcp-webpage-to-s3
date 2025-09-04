# FROM python:3.12-slim
FROM hub.byted.org/base/debian.bookworm.python312:latest

WORKDIR /app

# Set timezone to Asia/Shanghai (UTC+8)
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* && \
  pip install --no-cache-dir uv

COPY . .

RUN uv pip install --system .

EXPOSE 8001

CMD ["python", "main.py"]
