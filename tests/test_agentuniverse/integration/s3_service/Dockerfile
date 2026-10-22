# Disposable local compatibility fixture, not a production deployment image.
FROM golang:1.27.1-bookworm@sha256:8d48e12ec56735e9358640898b9d9b9fcca110612ed8a5567438c0a1baa24e66
RUN GOBIN=/usr/local/bin go install github.com/minio/minio@9e49d5e7a648f00e26f2246f4dc28e6b07f8c84a
ENTRYPOINT ["/usr/local/bin/minio"]
