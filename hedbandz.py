import copy
from enum import Enum
import json
from typing import Tuple, List

import numpy as np
import pandas as pd

WORD_ALIVE_COL = 'word_alive'
CARDS_CSV = 'cards.csv'


class Response(Enum):
    NO = 0
    YES = 1
    MAYBE = 2


def load_cards(cards_csv_path: str) -> pd.DataFrame:
    """
    Load card information file
    :param cards_csv_path: path to cards
    :return: cards_df
    """
    return pd.read_csv(cards_csv_path, index_col='word')


def step(df_in: pd.DataFrame,
         key: str,
         ans: Response) -> Tuple[pd.DataFrame, str]:
    """
    Update data
    :param df_in: card data input
    :param key: question under test
    :param ans: answer
    :return: df_updated, next_q
    """
    if WORD_ALIVE_COL not in df_in:
        df_in[WORD_ALIVE_COL] = True

    if ans == Response.MAYBE:
        # raise NotImplementedError('Not implemented yet...')
        df_in = df_in.drop(key, axis=1)
        key = ''

    if key:
        # APPLY QUESTION
        idx_alive = df_in[WORD_ALIVE_COL]
        idx_match = np.logical_and(idx_alive,
                                   df_in.loc[:, key] == ans.value)
        df_in.loc[~idx_match, WORD_ALIVE_COL] = False

    # DECIDE NEXT QUESTION
    idx_alive = df_in[WORD_ALIVE_COL]
    df_exclude = df_in.drop([WORD_ALIVE_COL], axis=1)
    divider = df_exclude.loc[idx_alive, :].sum(axis=0) / idx_alive.sum() - 0.5

    next_question = divider.abs().idxmin()

    return df_in, next_question


def dump_cards_to_json():
    """
    Dump attributes to JSON
    """
    df = load_cards(CARDS_CSV)
    out = {}
    for word, props in df.iterrows():
        out[word] = props.index.values[props == 1].tolist()
    with open('cards.json', 'w') as f_cards:
        json.dump(out, f_cards, indent=4)
    with open('questions.json', 'w') as f_q:
        json.dump(df.columns.values.tolist(), f_q, indent=4)


def auto_solve(df: pd.DataFrame,
               word: str,
               max_tries: int=20) -> Tuple[str, int]:
    """
    Automatically solve for a word

    :param df: cards CSV
    :param word: the word to solve (should be in index of df)
    :param max_tries: maximum tries (questions) before giving up
    :return: answer_word, n_tries
    """
    next_q = ''
    count = 0
    failed = False
    while True:
        if count >= max_tries:
            failed = True
            break

        if not next_q:
            answer = None
        else:
            answer = Response(df.loc[word, next_q])
        df, next_q = step(df, next_q, answer)
        if df.loc[:, WORD_ALIVE_COL].sum() == 1:
            break
        print('Question: {}, Answer: {}'.format(next_q, answer))
        count += 1

    n_alive = df.loc[:, WORD_ALIVE_COL].sum()
    if failed:
        f_str = 'Failed to find an answer for "{}" after {} tries'
        raise ValueError(f_str.format(word, count))
    elif n_alive > 1:
        f_str = 'Failed to find a unique answer for "{}"'
        raise ValueError(f_str.format(word))
    return df.index.values[df.loc[:, WORD_ALIVE_COL]][0], count


def unnecessary_columns() -> List[str]:
    """
    Find columns that are not needed to have a unique solution
    :return:
    """
    df = load_cards(CARDS_CSV)
    remove_cols = []
    for col in df.columns.values:
        df_i = copy.deepcopy(df)
        df_i = df_i.drop(col, axis=1)
        necessary = False
        for word, _ in df_i.iterrows():
            try:
                solve_ans, solve_count = auto_solve(df_i, word)
                assert solve_ans == word
            except (ValueError, AssertionError):
                necessary = True
                break

        if not necessary:
            remove_cols.append(col)

    return remove_cols


def play():
    """
    Play the game with input
    """
    df = load_cards(CARDS_CSV)
    next_q = ''
    while True:
        if next_q:
            f_str = 'Am I (a) {} (1 = yes, 0 = no, 2 = maybe/could be): '
            text_in = input(f_str.format(next_q))
            try:
                answer = Response(int(text_in))
            except ValueError:
                e_str = 'Invalid input "{}", try again...'
                print(e_str.format(text_in))
                answer = Response(0)
        else:
            answer = Response(0)

        df, next_q = step(df, next_q, answer)

        n_alive = df.loc[:, WORD_ALIVE_COL].sum()
        if n_alive == 1:
            solved_ans = df.index.values[df.loc[:, WORD_ALIVE_COL]][0]
            f_str = 'Solved! I am a {}'
            print(f_str.format(solved_ans))
            solved_text = input('anything to exit, enter to undo last: ')
            if not solved_text:
                break
        elif n_alive == 0:
            e_str = 'Could not solve! :('
            raise ValueError(e_str)


if __name__ == '__main__':
    play()
