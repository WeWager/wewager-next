#!/bin/sh
cd /usr/src/app/ingest/spiders
scrapy list | grep -v datafeeds | xargs -n 1 scrapy crawl