import os
import time
from enum import Enum
from collections import Iterable


class FileType(Enum):
    IN_FILE = 1,
    OUT_FILE = 2,
    WIN_FILE = 3
    BEST_FILE = 4
    SCORE_FILE = 5


def __get_extension(file_type):
    if file_type == FileType.IN_FILE:
        return ".in"
    elif file_type == FileType.OUT_FILE:
        return ".out"
    elif file_type == FileType.WIN_FILE:
        return ".win"
    elif file_type == FileType.BEST_FILE:
        return ".best"
    elif file_type == FileType.SCORE_FILE:
        return ".score"


def __file_path_stamped(path, filename, file_extension, number):
    time_str = time.strftime("%Y%m%d-%H%M%S")
    temp_filename = '{}_{}_{}'.format(filename, number, time_str)
    return os.path.join(path, temp_filename + file_extension)


def build_filename(experiment, file_type, number, method=None):
    file_extension = __get_extension(file_type)
    if file_type in [FileType.WIN_FILE, FileType.SCORE_FILE]:
        return '{}_{}_{}{}'.format(experiment.filename, method, number, file_extension)
    else:
        return '{}_{}{}'.format(experiment.filename, number, file_extension)


def save_to_file(experiment, file_type, number, candidates, voters, preferences=None, winners=None):
    filename = experiment.filename
    path = experiment.get_generated_dir_path()
    k = experiment.k
    file_extension = __get_extension(file_type)

    m = len(candidates)
    n = len(voters)

    file_path = __file_path_stamped(path, filename, file_extension, number)

    with open(file_path, 'w') as file:
        if file_type == FileType.IN_FILE:
            file.write('{} {}\n'.format(m, n))
            __save_content(file, candidates)
            __save_content(file, voters)
        else:
            file.write('{} {} {}\n'.format(m, n, k))
            __save_candidates(file, candidates)
            __save_preferences(file, voters, preferences)
            if file_type == FileType.WIN_FILE:
                __save_winners(file, winners, candidates)


def multigoal_save_to_file(experiment, file_type, number, candidates, voters, preferences=None, winners=None,
                           method=None, overwrite=True):
    path = experiment.get_generated_dir_path()
    k = experiment.k

    m = len(candidates)
    n = len(voters)

    filename = build_filename(experiment, file_type, number, method=method)
    file_path = os.path.join(path, filename)
    if not overwrite and os.path.isfile(file_path):
        return

    with open(file_path, 'w') as file:
        if file_type == FileType.IN_FILE:
            file.write('{} {}\n'.format(m, n))
            __save_content(file, candidates)
            __save_content(file, voters)
        elif file_type in [FileType.OUT_FILE, FileType.WIN_FILE]:
            file.write('{} {} {}\n'.format(m, n, k))
            __save_candidates(file, candidates)
            __save_preferences(file, voters, preferences)
            if file_type == FileType.WIN_FILE:
                __save_winners(file, winners, candidates)
        else:
            raise ValueError


def multigoal_save_scores(experiment, file_type, number, scores, method=None):
    filename = experiment.filename
    path = experiment.get_generated_dir_path()
    file_extension = __get_extension(file_type)

    if file_type == FileType.SCORE_FILE:
        filename = '{}_{}_{}{}'.format(filename, method, number, file_extension)
    else:
        filename = '{}_{}{}'.format(filename, number, file_extension)
    file_path = os.path.join(path, filename)

    with open(file_path, 'w') as file:
        __save_scores(file, scores)


def __save_content(file, content):
    for i in range(len(content)):
        result = __get_content_string(content[i])
        file.write(result + '\n')


def __save_candidates(file, candidates):
    for i in range(len(candidates)):
        candidates_string = __get_content_string(candidates[i])
        result = '{} {}\n'.format(i, candidates_string)
        file.write(result)


def __save_preferences(file, voters, preferences):
    for i in range(len(preferences)):
        preference = __get_content_string(preferences[i].order)
        voter = __get_content_string(voters[i][:-1])
        result = '{} {}\n'.format(preference, voter)
        file.write(result)


def __save_scores(file, scores):
    file.write(' '.join([str(s) for s in scores]))


def __save_winners(file, winners, candidates):
    for i in winners:
        candidate = __get_content_string(candidates[i])
        result = '{} {}\n'.format(i, candidate)
        file.write(result)


def __get_content_string(content):
    if isinstance(content, Iterable):
        return ' '.join(map(str, content))
    return str(content)
