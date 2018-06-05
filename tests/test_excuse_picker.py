import os
from twisted.trial import unittest
from talkback.excuse_picker import ExcusePicker 

class TestExcusePicker(unittest.TestCase):
    EXCUSE1 = (
        "I have to go learn some IOS"
    )
    EXCUSE2 = (
        "I actually have a test I have to go study for"
    )

    def test_pick(self):
        picker = ExcusePicker(os.path.join(os.path.dirname(__file__), "test_excuses.txt"))
        excuse = picker.pick()
        self.assertIn(quote, (self.EXCUSE1, self.EXCUSE2), "Got the wrong excuse: '%s'" % (excuse))