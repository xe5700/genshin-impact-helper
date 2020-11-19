FROM python:3-alpine
ENV CRON_DICT_UPDATE='9 30 * * *'
ENV TZ=Asia/Shanghai
RUN adduser app -D
RUN apk add --no-cache tzdata
WORKDIR /tmp
ADD requirements.txt ./
RUN pip3 install -r requirements.txt && rm requirements.txt
USER app
WORKDIR /app
ADD *.py ./
CMD ["python3", "./docker.py" ]