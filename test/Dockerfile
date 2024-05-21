FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY sudodataexporter.py /app/
COPY bpdataexporter.py /app/
COPY radataexporter.py /app/
COPY lidataexporter.py /app/

COPY test_sudodataexporter.py /app/
COPY test_bpdataexporter.py /app/
COPY test_radataexporter.py /app/
COPY test_lidataexporter.py /app/

CMD ["bash", "-c", "coverage run -m unittest && coverage report -m && coverage html && cp -r htmlcov /workspace/ && pytest --cov=/app --junitxml=./xmlReport/coverage.xml && python -m coverage xml && cp -r coverage.xml /workspace/"]
