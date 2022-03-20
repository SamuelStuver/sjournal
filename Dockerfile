FROM python:3.9.10-bullseye

WORKDIR /app

ARG TEST_ENV=local_repo
ARG PYPI_REPO_USER=NOTGIVEN
ARG PYPI_REPO_PASS=NOTGIVEN
RUN echo ${TEST_ENV}

COPY requirements.txt requirements.txt
COPY developer_requirements.txt developer_requirements.txt

COPY . .

RUN if [ "$TEST_ENV" = "local_repo" ] ; then pip install -r requirements.txt -r developer_requirements.txt ; else echo "NOT LOCAL REPO" ; fi

RUN if [ "$TEST_ENV" = "local_publish" ] ; then pip install -r developer_requirements.txt ; else echo "NOT LOCAL PUBLISH" ; fi
RUN if [ "$TEST_ENV" = "local_publish" ] ; then cd publish && sh ./publish_local.sh ; else echo "NOT LOCAL PUBLISH" ; fi

RUN if [ "$TEST_ENV" = "remote_publish" ] ; then apt-get install gcc musl-dev python3-dev libffi-dev openssl-dev -y ; else echo "NOT REMOTE PUBLISH" ; fi
RUN if [ "$TEST_ENV" = "remote_publish" ] ; then python -m pip install --upgrade pip ; else echo "NOT REMOTE PUBLISH" ; fi
RUN if [ "$TEST_ENV" = "remote_publish" ] ; then pip install -r developer_requirements.txt ; else echo "NOT REMOTE PUBLISH" ; fi
RUN if [ "$TEST_ENV" = "remote_publish" ] ; then cd publish && sh ./publish_remote.sh --use_tag -f; else echo "NOT REMOTE PUBLISH" ; fi
RUN if [ "$TEST_ENV" = "remote_publish" ] ; then pip install sjournal ; else echo "NOT REMOTE PUBLISH" ; fi


CMD [ "python", "-m" , "pytest"]