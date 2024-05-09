FROM python:3.10.14-alpine3.19

WORKDIR /usr/app

RUN apk update &&\
    apk upgrade

COPY ./src .

CMD ["python", "/usr/app/main.py"]