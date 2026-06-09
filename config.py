import os


class Config:
  DEBUG = False
  TESTING = False
  CACHE_DEFAULT_TIMEOUT = 300

  #use RedisCache
  CACHE_TYPE = "RedisCache"
  CACHE_REDIS_PORT = 6379
  CACHE_REDIS_DB = 0
  CACHE_REDIS_HOST = "host.docker.internal"  # Use host.docker.internal to connect to Redis on the host machine
  CACHE_REDIS_URL = "redis://host.docker.internal:6379/0"  # Redis URL for Flask-Caching
