FROM python:3.10.14-alpine3.19

WORKDIR /opt/python_server

COPY ./requirements.txt .

# Install dependencies
COPY requirements.txt .
RUN <<EOF
set -e
pip install -r requirements.txt --no-cache
find /usr/local/lib -type d -name __pycache__ -exec rm -r {} +
EOF

COPY ./server.py .

ENV SECRET "amazing"

CMD [ "python",  "server.py" ]