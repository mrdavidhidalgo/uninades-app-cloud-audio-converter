FROM python:3.9.15-alpine3.16

RUN apk update
RUN apk add build-base
RUN apk add sox
RUN apk add lame
ADD requirements.txt .
RUN pip install -r ./requirements.txt

ADD . .
ENV PORT 5000
EXPOSE $PORT
#CMD ["python", "app.py"]   
ENTRYPOINT [ "./gunicorn.sh" ]