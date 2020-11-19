FROM python:3-alpine
ENV CRON_DICT_UPDATE='30 9 * * *'
ENV TZ=Asia/Shanghai
ENV USE_TELEGRAM=False
ENV TG_TOKEN=TOKEN
ENV TG_CHAT_IDS=[]
RUN adduser app -D
RUN apk add --no-cache tzdata
WORKDIR /tmp
ADD requirements.txt ./
RUN pip3 install -r requirements.txt && rm requirements.txt
USER app
WORKDIR /app
ADD *.py ./
CMD ["python3", "./docker.py" ]