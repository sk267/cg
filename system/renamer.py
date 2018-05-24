import re


def hash_to_number(name_pattern):
    hashes = re.findall(r"#+", name_pattern)
    i = 1
    try:
        zeros = len(hashes[0])
    except IndexError:
        zeros = 4
    while True:
        if hashes:
            yield name_pattern.replace(hashes[0], str(i).zfill(zeros))
        else:
            yield name_pattern + str(i).zfill(zeros)
        i += 1
