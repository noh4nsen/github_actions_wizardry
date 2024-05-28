FROM golang:1.22.3-alpine3.19 as build
WORKDIR /usr/app

RUN apk update &&\
    apk upgrade &&\
    apk add make

COPY . /usr/app/
RUN make

FROM alpine:3.18.3 as run 

COPY --from=build /usr/app/bin/test-action /usr/bin/test-action
CMD /usr/bin/test-action