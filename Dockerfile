FROM python:3

ADD ts3bot.py /

RUN pip install ts3

CMD ["python3", "./ts3bot.py"]

