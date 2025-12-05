import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = "change_this_to_something_random"

DATABASE_PATH = os.path.join(BASE_DIR, "instance", "stroke.db")
CSV_FILE = os.path.join(BASE_DIR, "healthcare-dataset-stroke-data.csv")
