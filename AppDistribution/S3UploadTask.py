from __future__ import absolute_import

from AppDistribution.CeleryApp import app

@app.task
def add(x, y):
    return x + y

@app.task
def mult(x, y):
    return x * y 
