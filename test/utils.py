import random
import string


def random_word(word_length=None):
	if word_length is None:
		word_length = random.randrange(2, 10)
	return "".join(random.choice(string.ascii_lowercase) for i in range(word_length))


def random_sentence(sentence_length=None):
	if sentence_length is None:
		sentence_length = random.randrange(4, 8)
	
	return random.choice(string.ascii_uppercase) + \
	       " ".join(random_word() for i in range(sentence_length))


def random_paragraph(paragraph_length=None):
	if paragraph_length is None:
		paragraph_length = random.randrange(2, 4)
	
	return ". ".join(random_sentence() for i in range(paragraph_length)) + "."


def random_prose(prose_length=None):
	if prose_length is None:
		prose_length = 6
	
	return "\n\n".join(random_paragraph() for i in range(prose_length))
