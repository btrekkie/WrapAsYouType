class UserFacingError(Exception):
    """An error suitable for presenting to the user.

    The message of a UserFacingError must be appropriate for displaying
    to the end user, e.g. it should not reference class or method names.
    An example of a UserFacingError is a setting value that has the
    wrong type.
    """
    pass
