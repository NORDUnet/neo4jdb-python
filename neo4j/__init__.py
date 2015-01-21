
from neo4j import manager

apilevel = '2.0'
threadsafety = 1


def connect(dsn):
    return manager.ConnectionManager(dsn)


from error import *

