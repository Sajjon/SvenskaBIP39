from wordfreq import top_n_list

def read_languages_file(file_name):
	# define empty list
	words = []

	# open file and read the content in a list
	with open(file_name, 'r') as filehandle:
	    words = [current_place.rstrip() for current_place in filehandle.readlines()]

	print("✅ Read #{} words from '{}'".format(len(words), file_name))

	return set(words)

def parse_swedish():

	czech = read_languages_file('czech.txt')
	english = read_languages_file('english.txt')
	french = read_languages_file('french.txt')
	italian = read_languages_file('italian.txt')
	spanish = read_languages_file('spanish.txt')

	requested_word_count = 5000
	swedish_unfiltered = top_n_list('sv', requested_word_count)
	min_word_length = 3
	max_word_length = 8

	good_length = lambda w: len(w) >= min_word_length and len(w) <= max_word_length

	used_by = lambda words_set, word: word in words_set
	# used_by_other_languages = lambda w: used_by(czech, w) or used_by(english, w) or used_by(french, w) or used_by(italian, w) or used_by(spanish, w)

	swedish = []



	# list(filter(lambda w: 
	# 	good_length(w) and not used_by_other_languages(w), swedish))

	for word in swedish_unfiltered:

		if not word.isalpha():
			print("🔠 skipped word: '{}', not alpha".format(word))
			continue

		if not good_length(word):
			continue

		if used_by(czech, word):
			print("🇨🇿 skipped word: '{}', used by Czech".format(word))
			continue

		if used_by(english, word):
			print("🇬🇧 skipped word: '{}', used by English".format(word))
			continue

		if used_by(french, word):
			print("🇫🇷 skipped word: '{}', used by French".format(word))
			continue

		if used_by(italian, word):
			print("🇮🇹 skipped word: '{}', used by Italian".format(word))
			continue

		if used_by(spanish, word):
			print("🇪🇸 skipped word: '{}', used by Spanish".format(word))
			continue

		swedish.append(word)

	
	with open("output_swedish.txt", "w") as text_file:
		print(f"{swedish}", file=text_file)

	print("🇸🇪  Outputted #{} words, after having filtered out #{}".format(len(swedish), (requested_word_count-len(swedish))))
	

parse_swedish()