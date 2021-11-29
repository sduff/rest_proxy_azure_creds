FROM confluentinc/cp-kafka-rest:7.0.0


WORKDIR /app
ADD requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

ADD config.py launcher.sh /app

CMD [ "sh", "./launcher.sh" ]
