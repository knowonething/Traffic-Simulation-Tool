# a container with mysql-connector-python and your app

FROM python:3.8.0

WORKDIR /usr/somebody/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY docker-entrypoint.sh ./

ENTRYPOINT ["/usr/somebody/docker-entrypoint.sh"]