FROM python:3.9.10-bullseye

WORKDIR /app

ARG TEST_ENV=local_repo
RUN echo ${TEST_ENV}

COPY requirements.txt requirements.txt
COPY developer_requirements.txt developer_requirements.txt
RUN pip install -r requirements.txt
RUN pip install -r developer_requirements.txt

COPY . .

CMD [ "python", "-m" , "pytest", "--test_environment", ${TEST_ENV}]