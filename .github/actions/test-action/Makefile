BINARY_NAME=test-action

build:
	GOARCH=amd64 GOOS=linux CGO_ENABLED=0 go build -o ./bin/${BINARY_NAME} .
clean:
	go clean
	rm -rf ../build