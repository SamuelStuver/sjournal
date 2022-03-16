FROM python:3.9.10-bullseye

WORKDIR /app

ARG TEST_ENV=local_repo
RUN echo ${TEST_ENV}

COPY requirements.txt requirements.txt
COPY developer_requirements.txt developer_requirements.txt

COPY . .

RUN if [ "TEST_ENV" = "local_repo" ] ; then pip install -r requirements.txt -r developer_requirements.txt ; fi

RUN if [ "TEST_ENV" = "local_publish" ] ; then cd publish && sh ./publish_local.sh ; else echo "failed" ; fi

RUN if [ "TEST_ENV" = "remote_publish" ] ; then cd publish && sh ./publish_remote.sh && pip install sjournal; else echo "failed" ; fi


ENTRYPOINT [ "python", "-m" , "pytest"]