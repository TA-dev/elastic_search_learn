FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y osmium-tool python3 python3-pip && \
    apt-get clean

WORKDIR /app
COPY . .

CMD ["python3", "merge_nominatim.py"]