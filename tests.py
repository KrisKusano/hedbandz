import copy
from unittest import TestCase

from hedbandz import load_cards, auto_solve


class TestHedbandz(TestCase):
    def setUp(self):
        self.df = load_cards('cards.csv')

    def testAllSolvable(self):
        """
        Check that all cards have a unique solution
        """
        for object, props in self.df.iterrows():
            print('Starting: {}'.format(object))
            df = copy.deepcopy(self.df)
            ans, _ = auto_solve(df, object)
            self.assertTrue(object, ans)
