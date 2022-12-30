from collections import Counter
import numpy as np


def select_higher_freq_gender(about):
    """
    Input - 'about' section from Amazon website, 'about' column from the dataframe.
    Determine Author is a woman or a man from the about information.

    Whichever pronouns are found with more frequency, that is determinded to be the \
    gender of the author (and the name).
    """
    if not about or not isinstance(about, str):
        return None
    about = about.lower().split()
    about = [word.strip() for word in about]
    word_counter = Counter(about)
    feminine_pronouns = (
        word_counter.get('her', 0) +
        word_counter.get('she', 0) +
        word_counter.get('ms', 0) +
        word_counter.get('mrs', 0) +
        word_counter.get('miss', 0) +
        word_counter.get('ms.', 0) +
        word_counter.get('mrs.', 0)
    )

    masculine_pronouns = (
        word_counter.get('him', 0) +
        word_counter.get('he', 0) +
        word_counter.get('his', 0) +
        word_counter.get('mr', 0) +
        word_counter.get('mr.', 0)
    )

    if feminine_pronouns > masculine_pronouns:
        return 1
    elif masculine_pronouns > feminine_pronouns:
        return 0
    else:
        return np.nan


def extract_first_name(name):
    """
    Take in the whole name and extract the first name, in lower case.
    """
    if name:
        if '-' in name:
            name = ' '.join([char for char in name.split('-')])
        name = name.lower().split()
        for string in ['dr.', 'dr', 'prof', 'prof.']:
            if string in name:
                name.remove(string)
        first_name = name[0].replace('.', '')
        if len(first_name) > 1:
            return first_name
    return None
