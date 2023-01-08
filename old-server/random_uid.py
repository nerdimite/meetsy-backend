from words import ADJECTIVES, POLITE_ADJECTIVES, NOUNS, ANIMALS
import random

def random_noun():
    return random.choice(NOUNS).lower()

def random_animal():
    return random.choice(ANIMALS).lower()

def random_adjective():
    return random.choice(ADJECTIVES).lower()

def random_polite_adjective():
    return random.choice(POLITE_ADJECTIVES).lower()

def random_namepair():
    return "{}-{}".format(random_adjective(), random_noun())

def random_polite_animalpair():
    return "{}-{}".format(random_polite_adjective(), random_animal())

def generate_random_uid():
    if random.random() < 0.5:
        adjective_noun_pair = random_namepair()
    else:
        adjective_noun_pair = random_polite_animalpair()

    return "{}-{}".format(adjective_noun_pair, random.randint(100, 999))