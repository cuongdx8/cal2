import bcrypt
import string
import random


def compare_password(str_password, encoded_password):
    b_password = str_password.encode('utf-8')
    b_encoded_password = encoded_password.encode('utf-8')
    return bcrypt.checkpw(b_password, b_encoded_password)


def encode_password(password):
    b_password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(b_password, salt).decode('utf-8')


def generate_random_password():
    characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")

    ## length of password from the user
    length = 10

    ## shuffling the characters
    random.shuffle(characters)

    ## picking random characters from the list
    password = []
    for i in range(length):
        password.append(random.choice(characters))

    ## shuffling the resultant password
    random.shuffle(password)

    ## converting the list to string
    ## printing the list
    return "".join(password)
