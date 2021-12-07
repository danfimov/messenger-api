FROM python:3

WORKDIR /usr/src/messenger

COPY ./ .

RUN pip install --no-cache-dir -r src/requirements.txt
RUN pip install src/
RUN pip install --no-cache-dir -r tests/requirements.txt

CMD ["pytest", "tests"]