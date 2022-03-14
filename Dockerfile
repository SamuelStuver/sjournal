FROM python

COPY . /var/lib/jenkins/workspace/sjournal
WORKDIR /var/lib/jenkins/workspace/sjournal
CMD python -m pytest tests