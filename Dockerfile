FROM python:3.9-alpine
FROM python:3.9-alpine AS builder
RUN apk add -u gcc libc-dev linux-headers libffi-dev python3-dev musl-dev make
RUN pip3 install --upgrade pip
COPY requirements.txt .
RUN pip3 install --user -r requirements.txt
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app

FROM python:3.9-alpine AS execution

WORKDIR /usr/src/app

COPY --from=builder /root/.local /root/.local
COPY --from=builder /usr/src/app .

EXPOSE 8080
ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT [ "python3", "-m", "swagger_server" ]
