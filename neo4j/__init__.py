
from neo4j import contextmanager as cm

apilevel = '2.0'
threadsafety = 1


def connect(dsn):
    return cm.ConnectionManager(dsn)


from error import *

