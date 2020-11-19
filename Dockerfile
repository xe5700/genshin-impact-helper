FROM alpine:lts
RUN adduser app -D
RUN apk add --no-cache python3 py3-pip tzdata
USER app
WORKDIR /app
ADD *.py ./
ADD requirements.txt ./
RUN pip3 install -r requirements.txt
CMD ["./docker.py" ]
ENV TZ=Asia/Shanghai