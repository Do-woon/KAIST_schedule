
#raised if parsing fails because of page scheme is changed
class PageSchemeException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


#raised if argument of the parser function is not valid
class ArgumentError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value
