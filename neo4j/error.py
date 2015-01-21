"""
Neo4J errors.
"""

try:
    StandardError = Exception
except ImportError:
    from exceptions import StandardError


class Error(StandardError):
    rollback = True


class Warning(StandardError):
    rollback = False


class InterfaceError(Error):
    pass


class DatabaseError(Error):
    pass


class InternalError(DatabaseError):
    pass


class OperationalError(DatabaseError):
    pass


class ProgrammingError(DatabaseError):
    rollback = False


class IntegrityError(DatabaseError):
    rollback = False


class DataError(DatabaseError):
    pass


class NotSupportedError(DatabaseError):
    pass

