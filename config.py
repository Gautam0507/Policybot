import os


class Config:
    ALLOWED_EXTENSIONS = ["pdf"]

    BASE_DIR = os.path.dirname(__file__)
    DATA_DIR = os.path.join(BASE_DIR, "data")
    DB_DIR = os.path.join(BASE_DIR, "db")

