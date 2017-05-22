FROM python:2
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
EXPOSE 7080
CMD [ "python", "./app.py" ]
