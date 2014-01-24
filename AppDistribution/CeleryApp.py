from __future__ import absolute_import
from celery import Celery

app = Celery('AppDistribution', 
        broker='amqp://guest@localhost//',
        backend='amqp://guest@localhost//',
        include=['AppDistribution.S3UploadTask'])

if __name__ == "__main__":
    app.start()
