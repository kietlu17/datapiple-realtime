FROM python:3.10-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "sleep 60 && python -m scrapy runspider goodread/spiders/goodreadcrawl.py"]