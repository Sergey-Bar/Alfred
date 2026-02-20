FROM golang:1.21-alpine AS build
WORKDIR /src
COPY . ./
RUN go build -o /bin/gateway ./

FROM alpine:3.18
COPY --from=build /bin/gateway /bin/gateway
EXPOSE 8080
ENTRYPOINT ["/bin/gateway"]
