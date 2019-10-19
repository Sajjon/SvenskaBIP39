import re
from collections import defaultdict

def created_pos_tagged_doc_parole():
	file_name = 'stats_PAROLE.txt'
	regexp_for_tab = re.compile("[^\t]+")

	words_for_pos_tmp = defaultdict(list)
	pos_of_words = {}

	progress_counter = 0
	with open(file_name, 'r') as filehandle:
		for current_place in filehandle.readlines():
			line_without_trailing_newline = current_place.rstrip()
			tab_separated_substrings = regexp_for_tab.findall(line_without_trailing_newline)
			word = tab_separated_substrings[0]
			pos_of_word = tab_separated_substrings[1]

			# Dictionary over the POS of words
			pos_of_words[word] = pos_of_word

			# Add to a dictionary with POS as key and list of words as valuee
			words_for_pos_tmp[pos_of_word].append(word)
			milestone = 10000
			progress_counter += 1
			if progress_counter % milestone == 0:
				print("🧠 Parsed an additional #{} lines, have found #{} words so far".format(milestone, len(pos_of_words.keys())))
				progress_counter = 0


	words_for_pos = dict((k, tuple(v)) for k, v in words_for_pos_tmp.items())
	
	print("✅ Finished parsing, found #{} diffrent part of parts of speech (POS)".format(len(words_for_pos_tmp.keys())))

created_pos_tagged_doc_parole()