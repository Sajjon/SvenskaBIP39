import re
from collections import defaultdict
import sys

min_word_length = 3
max_word_length = 8

good_length = lambda w: len(w) >= min_word_length and len(w) <= max_word_length

# Download corpus with POS tagged word stats here: https://svn.spraakdata.gu.se/sb-arkiv/pub/frekvens/stats_PAROLE.txt

"""
CODE | SWEDISH CATEGORY 	| EXAMPLE 	| ENGLISH TRANSLATION 
AB 	 | Adverb 				| 'inte' 	| Adverb
DT 	 | Determinerare 		| 'denna'	| Determiner
______________________________________________________________________________
HA 	 | Frågande/relativt	|			|	
	 |	adverb 				| 'när'	 	| Interrogative/Relative Adverb
------------------------------------------------------------------------------
HD 	 | Frågande/relativ	 |			|
	 |	determinerare 		| 'vilken' 	| Interrogative/Relative Determiner
------------------------------------------------------------------------------
HP 	 | Frågande/relativt	|			|
	 |	pronomen 			| 'som' 	| Interrogative/Relative Pronoun
------------------------------------------------------------------------------
HS 	 | Frågande/relativt	|			|
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
pos_whitelist = set([
	'JJ', 	# Adjective
	'NN', 	# Noun
	'RG', 	# Cardinal number
	'VB', 	# Verb,
	'AB',	# Adverb,
	'PP',	# Preposition
	'CD'	# Cardinal number
])

class WordCandidate(object):
	def __init__(self, number_of_occurences_in_corpus, initial_pos, word_maybe_not_base_form, word_on_base_form):
		if word_on_base_form is None:
			raise ValueError("Base form cannot be None")
		
		if word_maybe_not_base_form is None:
			raise ValueError("Word cannot be None")

		self.word_on_base_form = word_on_base_form

		self.pos_tags = set([initial_pos])
		self.different_forms = set([word_maybe_not_base_form])

		# For NON names (POS tag: 'PM') we will add the number of 
		# occurences of a uppercase word 'Jägare' and 'jägare' and their
		# non base forms: 'jägarna' and 'jägarnas' etc.
		self.sum_of_occurences_of_base_word = number_of_occurences_in_corpus

	def __eq__(self, other):
		if isinstance(other, WordCandidate):
			return self.word_on_base_form == other.word_on_base_form
		elif isinstance(other, str):
			result_of_comparision = self.word_on_base_form == other
			print("WordCandidate compared with string yields: '{}', useful⁉️".format(result_of_comparision))
			return result_of_comparision
		else:
			return ValueError("Cannot compare 'WordCandidate' with type: '{}'".format(type(other)))

	def __hash__(self):
		return self.word_on_base_form

	def update(self, base_form, word, pos, occurences):
		if not base_form == self.word_on_base_form:
			raise ValueError("Not same base form of word, got '{}', but expected: '{}'".format(base_form, self.word_on_base_form))

		self.pos_tags.add(pos)
		self.different_forms.add(word.lower())
		self.sum_of_occurences_of_base_word += occurences

	def contains_any_word_of_suitable_length(self):
		for w in self.different_forms:
			if good_length(w):
				return True
		return False

	def contains_any_whitelisted_pos(self):
		intersected_pos_tags = self.pos_tags.intersection(pos_whitelist)
		return len(intersected_pos_tags) > 0

	def __str__(self):
		return "CANDIDATE<w={}, #pos_tags={}, #words={}>".format(self.word_on_base_form, len(self.pos_tags), len(self.different_forms))

	def as_result(self):
		return "{}\t{}\t{}".format(self.word_on_base_form, self.pos_tags, self.different_forms)

	def good_candiate(self):
		is_good_candidate = self.contains_any_word_of_suitable_length() and self.contains_any_whitelisted_pos()
		return is_good_candidate

class Words(object):

	def __init__(self, target_word_count):
		self.target_word_count = target_word_count

		# Key: Word on _base form_, value: 'WordCandidate'
			# The result of this program, a curated list (dictionary) of disamibious words of
		# (and their part of speech) of correct length which 
		# are easy to remember, all having a part of 
		# speech which is in the white list above.
		self.candidates = {}

		self.number_of_lines_parsed = 0

	def add_or_update_candidate(self, base_form, word, pos, occurences):
		if base_form in self.candidates:
			self.candidates[base_form].update(base_form=base_form, word=word, pos=pos, occurences=occurences)
		else:
			no_of_good_candidates_before = self.number_of_viable_candidates()
			self.candidates[base_form] = WordCandidate(occurences, pos, word, base_form)

			no_of_good_candidates_after = self.number_of_viable_candidates()
			if no_of_good_candidates_after > 0 and no_of_good_candidates_after != no_of_good_candidates_before and no_of_good_candidates_after % 100 == 0:
				print("🎉 Number of viable word candidates: #{}".format(no_of_good_candidates_after))

	def tuple_from_line(self, line_in_corpus):
		regexp_for_tab = re.compile("[^\t]+")

		tab_separated_substrings = regexp_for_tab.findall(line_in_corpus)
		word = tab_separated_substrings[0]

		pos_of_word_with_specification = tab_separated_substrings[1]

		number_of_occurences_in_corpus = int(tab_separated_substrings[4])

		pos_of_word_parts = pos_of_word_with_specification.split(".")

		pos_of_word = pos_of_word_parts[0]
	
		string_of_base_form_with_suffix = tab_separated_substrings[2] # '|vara..vb.2|vara..vb.1|vara_med..vbm.1|'
		list_of_base_form_with_suffix = string_of_base_form_with_suffix.split('|')
		base_form_with_suffix = list_of_base_form_with_suffix[1] # 'vara..vb.2'
		
		base_form = None

		if not base_form_with_suffix:
			base_form = word
		else:
			base_form_parts = base_form_with_suffix.split("..")
			base_form = base_form_parts[0]

		return (base_form, word, pos_of_word, number_of_occurences_in_corpus)

	def parse(self, line_in_corpus):

		self.number_of_lines_parsed += 1

		(base_form, word, pos, occurences) = self.tuple_from_line(line_in_corpus)

		if not word.isalpha():
			return

		self.add_or_update_candidate(base_form=base_form, word=word, pos=pos, occurences=occurences)

		

	def viable_candidates(self):
		return list(filter(lambda w: w.good_candiate(), self.candidates.values()))

	def number_of_viable_candidates(self):
		return len(self.viable_candidates())

	def done(self):
		count = self.number_of_viable_candidates()
		return count >= self.target_word_count 


class POSInfo(object):

	def __init__(self, pos, word):
		self.pos = pos
		self.count = 1
		self.words = [word]

	def increase_counter(self, word):
		self.count += 1
		self.words.append(word)

def analyze_pos_distribution_of(candidates_sorted_by_frequency):
	count_pos = {}
	for candidate in candidates_sorted_by_frequency:
		for pos_tag in candidate.pos_tags:
			base_form = candidate.word_on_base_form
			if pos_tag in count_pos:
				count_pos[pos_tag].increase_counter(base_form)
			else:
				count_pos[pos_tag] = POSInfo(pos_tag, base_form)

	print("\n📊 Stats of distribution of part of speech tags")
	for posInfo in sorted(count_pos.values(), key=lambda e: e.count, reverse=True):
		print("{}\t{}".format(posInfo.pos, posInfo.count))



def parse_result(result):
	if result is None or not isinstance(result, Words):
		raise ValueError("Bad result")

	if not result.done():
		raise ValueError("Not enough canidates")

	viable_candidates = result.viable_candidates()

	candidates_sorted_by_frequency = sorted(viable_candidates, key=lambda c: c.sum_of_occurences_of_base_word, reverse=True)

	analyze_pos_distribution_of(candidates_sorted_by_frequency)
	
	output_elements = list(map(lambda wc: wc.as_result(), candidates_sorted_by_frequency))
	output_string = "\n".join(output_elements)

	output_file_name = 'candidates_swedish.txt'
	with open(output_file_name, "w") as text_file:
		print(f"{output_string}", file=text_file)

	print("\n✅ Outputted #{} candidates to file '{}'".format(len(output_elements), output_file_name))
	return candidates_sorted_by_frequency


def user_prompt(question: str) -> bool:
	""" Prompt the yes/no-*question* to the user. """
	from distutils.util import strtobool

	while True:
		user_input = input(question + " [y/n]: ").lower()
		try:
			result = strtobool(user_input)
			return result
		except ValueError:
			print("Please use y/n or yes/no.\n")

def ask_for_number(question, in_range):
	answer = None
	while answer not in in_range:
		raw_answer = input(question)
		answer = int(raw_answer)
		if isinstance(answer, int):
			return answer
		else:
			print("Please enter an int in range: {}".format(in_range))

def ask_for_human_input_for_final_list(target_word_count, candidates):
	if candidates is None or not isinstance(candidates, list):
		raise ValueError("Bad value of 'canidates'")

	if not isinstance(candidates[0], WordCandidate):
		error_message = "candidates list does not contain elements of type 'WordCandidate', value: '{}', has type: '{}'".format(candidates[0], type(candidates[0]))
		raise ValueError(error_message)

	if len(candidates) <= target_word_count:
		raise ValueError("List too short")

	# should be lowercase, correct length and disambgious
	output_elements = set([])

	for candidate in candidates:

		# question = "Include this word? {}".format(candidate.as_result())
		# if user_prompt(question):

		words_of_good_length_any_case = list(filter(lambda w: good_length(w), candidate.different_forms))
		words_of_good_length = list(map(lambda w: w.lower(), words_of_good_length_any_case))

		good_potential_words = []
		# list(filte(lambda w: , words_of_good_length))
		for word in words_of_good_length:
			if len(word) >= 4:
				prefix_of_word = word[:-4]
				if not prefix_of_word in list(map(lambda w: w[:-4], output_elements)):
					good_potential_words.append(word)
			else:
				if not word in output_elements:
					good_potential_words.append(word)

		if not good_potential_words:
			continue

		if len(good_potential_words) > 1:
			question = "\nInclude any of these words? {}\t<POS: {}>".format(good_potential_words, candidate.pos_tags)
			if user_prompt(question):
				word_indices = list(range(len(good_potential_words)))
				alternatives_dictionary = ["{} = '{}'".format(i, w) for i,w in enumerate(good_potential_words)]
				alternatives_string = "\n".join(alternatives_dictionary)
				question_alternatives = "Which one?\n{}\n".format(alternatives_string)
				chosen_word_index = ask_for_number(question_alternatives, word_indices)
				word = good_potential_words[chosen_word_index]
				output_elements.add(word)

		else:
			word = good_potential_words[0]
			question = "\nInclude this word? '{}'\t<POS: {}>".format(word, candidate.pos_tags)
			if user_prompt(question):
				output_elements.add(word)


		if len(output_elements) >= target_word_count:
			break
	
	output_string = "\n".join(output_elements)

	output_file_name = 'swedish.txt'
	with open(output_file_name, "w") as text_file:
		print(f"{output_string}", file=text_file)

	print("\n🇸🇪 Outputted #{} words to file '{}'".format(len(output_elements), output_file_name))
	return output_elements

def created_pos_tagged_doc_parole():
	file_name = 'stats_PAROLE.txt'
	target = 2048
	words = Words(target_word_count=target*3)

	with open(file_name, 'r') as filehandle:
		for current_place in filehandle.readlines():
			line = current_place.rstrip() # without trailing newline
			
			words.parse(line)

			if words.done():
				break

	candidates = parse_result(words)
	ask_for_human_input_for_final_list(target_word_count=target, candidates=candidates)

	
created_pos_tagged_doc_parole()