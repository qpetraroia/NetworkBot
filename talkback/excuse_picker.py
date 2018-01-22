from random import choice 

class ExcusePicker(object):

    def __init__(self, excuse_filename):
        """
        Initialize our excuses
        """
        with open(excuse_filename) as textFilename:
            self.excuses = excuse_filename.readlines()

    def pick(self):
        """
        Pick a excuse
        """
        return choice(self.excuses).strip()