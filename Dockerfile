FROM python:3.6

EXPOSE 8888

ENV TZ Asia/Shanghai
RUN echo $TZ > /etc/timezone && \
    apt-get update && apt-get install -y tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean

# ENV PIP_INDEX_URL http://mirrors.aliyun.com/pypi/simple
# ENV PIP_TRUSTED_HOST mirrors.aliyun.com

RUN mkdir -p /var/www/lxkaka
WORKDIR /var/www/lxkaka
COPY requirements.txt /var/www/lxkaka
RUN pip install -r requirements.txt

COPY ./lxkaka/ /var/www/lxkaka/
CMD python server.py
