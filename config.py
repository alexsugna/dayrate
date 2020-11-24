import os

basedir = os.path.abspath(os.path.dirname(__file__))
ROOT_USER = "admin"
ROOT_PWD = "password"
SERVER_PUBLIC_IP = "18.221.31.5"

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = b'48hf9j98rfh_+==_98j9i'

class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
