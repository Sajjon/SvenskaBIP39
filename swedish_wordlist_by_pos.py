import re
from collections import defaultdict

def created_pos_tagged_doc_parole():
	"""
	CODE | SWEDISH CATEGORY 	| EXAMPLE 	| ENGLISH TRANSLATION 
	AB 	 | Adverb 				| 'inte' 	| Adverb
	DT 	 | Determinerare 		| 'denna'	| Determiner
	______________________________________________________________________________
	HA 	 | Frågande/relativt    |			|	
		 |	adverb 				| 'när'	 	| Interrogative/Relative Adverb
	------------------------------------------------------------------------------
	HD 	 | Frågande/relativ     |			|
		 |	determinerare 		| 'vilken' 	| Interrogative/Relative Determiner
	------------------------------------------------------------------------------
	HP 	 | Frågande/relativt    |			|
		 |	pronomen 			| 'som' 	| Interrogative/Relative Pronoun
	------------------------------------------------------------------------------
	HS 	 | Frågande/relativt    |			|
		 | possessivt pronomen  | 'vars' 	| Interrogative/Relative Possessive
	------------------------------------------------------------------------------
	IE 	 | Infinitivmärke 		| 'att' 	| Infinitive Marker
	IN 	 | Interjektion 		| 'ja'		| Interjection
	JJ 	 | Adjektiv  			| 'glad' 	| Adjective					
	KN 	 | Konjunktion 			| 'och' 	| Conjunction
	NN 	 | Substantiv 			| 'pudding'	| Noun
	PC 	 | Particip 			| 'utsänd' 	| Participle
	PL 	 | Partikel 			| 'ut' 		| Particle
	PM 	 | Egennamn 			| 'Mats' 	| Proper Noun
	PN 	 | Pronomen 			| 'hon' 	| Pronoun
	PP 	 | Preposition 			| 'av'		| Preposition
	PS 	 | Possessivt pronomen 	| 'hennes'  | Possessive
	RG 	 | Grundtal 			| 'tre' 	| Cardinal number
	RO 	 | Ordningstal 			| 'tredje' 	| Ordinal number
	SN 	 | Subjunktion 			| 'att'		| Subjunction
	UO   | Utländskt ord 		| 'the'		| Foreign Word
	VB 	 | Verb 				| 'kasta'	| Verb 
	"""
	file_name = 'stats_PAROLE.txt'

	pos_whitelist = set([
		'JJ', 	# Adjective
		'NN', 	# Noun
		'RG', 	# Cardinal number
		'VB' 	# Verb
	])

	# The result of this program, a curated list (dictionary) of disamibious words of
	# (and their part of speech) of correct length which 
	# are easy to remember, all having a part of 
	# speech which is in the white list above.
	pos_of_words = {}

	regexp_for_tab = re.compile("[^\t]+")

	# words_for_pos_tmp = defaultdict(list)

	min_word_length = 3
	max_word_length = 8

	good_length = lambda w: len(w) >= min_word_length and len(w) <= max_word_length

	milestone = 500
	progress_counter = 0
	word_count_limit = 1000
	with open(file_name, 'r') as filehandle:
		for current_place in filehandle.readlines():
			line_without_trailing_newline = current_place.rstrip()
			tab_separated_substrings = regexp_for_tab.findall(line_without_trailing_newline)
			word = tab_separated_substrings[0]

			if not word.isalpha():
				# print("🔠 skipped word: '{}', not alpha".format(word))
				continue

			if not good_length(word):
				# print("3️⃣ 8️⃣ skipped word: '{}', too long or too short".format(word))
				continue

			# loooong
			pos_of_word_with_specification = tab_separated_substrings[1]
			pos_of_word_parts = pos_of_word_with_specification.split(".")
			if len(pos_of_word_parts) < 2:
				if len(pos_of_word_parts) == 0:
					print("☢️ POS: '{}', what to do?".format(pos_of_word_with_specification))
					break

			pos_of_word = pos_of_word_parts[0]

			if not pos_of_word in pos_whitelist:
				print("⚛️ skipped word: '{}', not in POS whitelist".format(word))
				continue
						

			# Dictionary over the POS of words
			pos_of_words[word] = pos_of_word

			# Add to a dictionary with POS as key and list of words as valuee
			# words_for_pos_tmp[pos_of_word].append(word)
			
			progress_counter += 1
			if progress_counter % milestone == 0:
				print("🧠 Parsed an additional #{} lines, have found #{} words so far".format(milestone, len(pos_of_words.keys())))

			if len(pos_of_words) == word_count_limit:
				break

	# words_for_pos = dict((k, tuple(v)) for k, v in words_for_pos_tmp.items())
	
	print("✅ Finished parsing, found #{} words".format(len(pos_of_words.keys())))
	for word, pos in pos_of_words.items():
		print("'{}' has POS: '{}'".format(word, pos))

created_pos_tagged_doc_parole()