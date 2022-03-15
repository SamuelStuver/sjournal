FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
COPY developer_requirements.txt developer_requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r developer_requirements.txt

COPY . .

CMD [ "python", "-m" , "pytest"]