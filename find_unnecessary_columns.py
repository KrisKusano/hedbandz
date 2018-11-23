from hedbandz import CARDS_CSV, unnecessary_columns

if __name__ == '__main__':
    crap_columns = unnecessary_columns()
    print('You can remove these columns: {}'.format(crap_columns))
