FROM python:3.9.10-bullseye

WORKDIR /app

ARG TEST_ENV=local_repo
RUN echo ${TEST_ENV}

COPY requirements.txt requirements.txt
COPY developer_requirements.txt developer_requirements.txt

COPY . .

RUN if [ "$TEST_ENV" = "local_repo" ] ; then pip install -r requirements.txt -r developer_requirements.txt ; else echo "NOT LOCAL REPO" ; fi

RUN if [ "$TEST_ENV" = "local_publish" ] ; then cd publish && sh ./publish_local.sh ; else echo "NOT LOCAL PUBLISH" ; fi
RUN if [ "$TEST_ENV" = "local_publish" ] ; then cd .. && pip install -r developer_requirements.txt ; else echo "NOT LOCAL PUBLISH" ; fi

RUN if [ "$TEST_ENV" = "remote_publish" ] ; then cd publish && sh ./publish_remote.sh ; else echo "NOT REMOTE PUBLISH" ; fi
RUN if [ "$TEST_ENV" = "remote_publish" ] ; then pip install -r developer_requirements.txt ; else echo "NOT REMOTE PUBLISH" ; fi
RUN if [ "$TEST_ENV" = "remote_publish" ] ; then pip install sjournal ; else echo "NOT REMOTE PUBLISH" ; fi


CMD [ "python", "-m" , "pytest"]