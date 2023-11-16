FROM python:3.9-alpine
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app
RUN pip3 install -r requirements.txt
EXPOSE 8080
ENTRYPOINT [ "python3", "-m", "swagger_server" ]