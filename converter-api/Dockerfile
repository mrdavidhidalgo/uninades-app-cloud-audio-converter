FROM python:3.9 

ADD requirements.txt .
RUN pip install -r ./requirements.txt
ADD . .
ENV PORT 5000
EXPOSE $PORT
CMD ["python", "app.py"]   