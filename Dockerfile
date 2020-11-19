FROM python:3-alpine
ENV TZ=Asia/Shanghai
RUN adduser app -D
RUN apk add --no-cache tzdata
USER app
WORKDIR /app
ADD *.py ./
ADD requirements.txt ./
RUN pip3 install -r requirements.txt
CMD ["./docker.py" ]