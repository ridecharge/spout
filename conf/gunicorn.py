import os
import multiprocessing
import sys

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
sys.path.append(PROJECT_PATH + "/../Spout")
