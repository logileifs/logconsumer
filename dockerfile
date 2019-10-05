FROM python:3.7
MAINTAINER logileifs <logileifs@gmail.com>

ADD . /app

#EXPOSE 8888

WORKDIR /app
#RUN pip3 install pipenv
#RUN pipenv install --system
RUN pip install -r requirements

CMD ["python", "logconsumer.py"]