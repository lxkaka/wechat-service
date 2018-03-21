FROM python:3.6

EXPOSE 8888

ENV TZ Asia/Shanghai
# 下面设置服务器时区，以防出现本地调试和服务器时区不一致
RUN echo $TZ > /etc/timezone && \
    apt-get update && apt-get install -y tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean

# ENV PIP_INDEX_URL http://mirrors.aliyun.com/pypi/simple
# ENV PIP_TRUSTED_HOST mirrors.aliyun.com

RUN mkdir -p /var/www/lakala
WORKDIR /var/www/lakala
COPY requirements.txt /var/www/lakala
RUN pip install -r requirements.txt

COPY ./lakala/ /var/www/lakala/
CMD python server.py
