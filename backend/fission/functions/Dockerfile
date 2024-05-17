FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY sudodataexporter/sudodataexporter.py /app/
COPY bpdataexporter/bpdataexporter.py /app/

COPY sudodataexporter/test_sudodataexporter.py /app/
COPY bpdataexporter/test_bpdataexporter.py /app/

CMD ["bash", "-c", "coverage run -m unittest && coverage report"]

RUN mkdir /coverage

RUN coverage html -d /coverage

RUN cp -r /coverage/* /Users/hkannan/.jenkins/workspace/Team-CCC-72/

