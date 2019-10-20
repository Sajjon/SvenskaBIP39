import re
from collections import defaultdict
import sys

min_word_length = 3
max_word_length = 8

good_length = lambda w: len(w) >= min_word_length and len(w) <= max_word_length

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

has_good_any_pos = lambda pos_list: any(set(pos_list).intersection(pos_whitelist))

class WordCandidate(object):
	def __init__(self, number_of_occurences_in_corpus, initial_pos, word_maybe_not_base_form, word_on_base_form):
		if word_on_base_form is None:
			raise ValueError("Base form cannot be None")
		
		if word_maybe_not_base_form is None:
			raise ValueError("Word cannot be None")

		self.word_on_base_form = word_on_base_form

		self.pos_tags = [initial_pos]
		self.different_forms = [word_maybe_not_base_form]

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


	def update_with_pos_of_word(self, number_of_occurences_in_corpus, pos_tag, word, word_base_form):
		if not word_base_form == self.word_on_base_form:
			raise ValueError("Not same base form of word, got '{}', but expected: '{}'".format(word_base_form, self.word_on_base_form))

		# if word.lower() in self.different_forms:
		# 	return False

		# name 'Björn', should not lowercase it, 
		# because it becomes 'björn'
		# (which equals the noun 'bear' in Swedish)?
		# Or actually we dont case?
		if pos_tag == 'PM':
			print("🙋🏻‍♀️ name of person found: '{}', lowercasing it anyway".format(word))

		self.pos_tags.append(pos_tag)
		self.different_forms.append(word.lower())
		self.sum_of_occurences_of_base_word += number_of_occurences_in_corpus
		return True

	def contains_any_word_of_suitable_length(self):
		for w in self.different_forms:
			if good_length(w):
				return True
		return False

	def contains_any_whitelisted_pos(self):
		return has_good_any_pos(self.pos_tags)

	def __str__(self):
		return "CANDIDATE<w={}, #pos_tags={}, #words={}>".format(self.word_on_base_form, len(self.pos_tags), len(self.different_forms))

	def as_result(self):
		return "{}\tPOS: {}\twords: {}".format(self.word_on_base_form, self.pos_tags, self.different_forms)

	def good_candiate(self):
		is_good_candidate = self.contains_any_word_of_suitable_length() and self.contains_any_whitelisted_pos()
		# print("⁉️ am I: '{}', a good candidate: '{}'".format(self, is_good_candidate))
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

	def parse(self, line_in_corpus):

		self.number_of_lines_parsed += 1

		regexp_for_tab = re.compile("[^\t]+")

		tab_separated_substrings = regexp_for_tab.findall(line_in_corpus)
		word = tab_separated_substrings[0]

		if not word.isalpha():
			return None

		pos_of_word_with_specification = tab_separated_substrings[1]

		# line @12 in file "stats_PAROLE.txt": 'det	PN.NEU.SIN.DEF.SUB+OBJ	|den..pn.1|	-	226213	9307.991048'
		# line @24 in file "stats_PAROLE.txt": 'Det	PN.NEU.SIN.DEF.SUB+OBJ	|den..pn.1|	-	110744	4556.785687'
		number_of_occurences_in_corpus_case_sensitive = tab_separated_substrings[2]

		pos_of_word_parts = pos_of_word_with_specification.split(".")

		def crash_and_burn(error_message):
			print("pos_of_word_with_specification: '{}'\ntab_separated_substrings: '{}'\n".format(pos_of_word_with_specification, tab_separated_substrings))
			error_message_formatted = "💣 Error: '{}'".format(error_message)
			raise ValueError(error_message_formatted)

		if len(pos_of_word_parts) < 1:
			crash_and_burn("len(pos_of_word_parts) < 1")

		pos_of_word = pos_of_word_parts[0]
	
		string_of_base_form_with_suffix = tab_separated_substrings[2] # '|vara..vb.2|vara..vb.1|vara_med..vbm.1|'
		list_of_base_form_with_suffix = string_of_base_form_with_suffix.split('|')
		base_form_with_suffix = list_of_base_form_with_suffix[1] # 'vara..vb.2'
		
		base_form = None

		if not base_form_with_suffix:
			# print("💡 Word: '{}' of POS: '{}' has no base form, setting 'base form' := word".format(word, pos_of_word))
			base_form = word
		else:
			base_form_parts = base_form_with_suffix.split("..") # ['vara', 'vb.2']
			if len(base_form_parts) < 2:
				print("🤷‍♂️ base_form_with_suffix: '{}'".format(base_form_with_suffix))
				crash_and_burn("len(base_form_parts) < 2")
		
			base_form = base_form_parts[0]
		
		if len(base_form) == 0:
			crash_and_burn("len(base_form) == 0")
		
		if base_form in self.candidates:
			self.candidates[base_form].update_with_pos_of_word(number_of_occurences_in_corpus_case_sensitive, pos_of_word, word, base_form)
		else:
			self.candidates[base_form] = WordCandidate(number_of_occurences_in_corpus_case_sensitive, pos_of_word, word, base_form)

			no_of_good_candidates = self.number_of_viable_candidates()
			if no_of_good_candidates > 0 and no_of_good_candidates % 10 == 0:
				print("🎉 Number of viable word candidates: #{}".format(no_of_good_candidates))

		return self.candidates[base_form]

	def viable_candidates(self):
		return list(filter(lambda w: w.good_candiate(), self.candidates.values()))

	def number_of_viable_candidates(self):
		return len(self.viable_candidates())

	def done(self):
		count = self.number_of_viable_candidates()
		return count > self.target_word_count 


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

	for posInfo in sorted(count_pos.values(), key=lambda e: e.count, reverse=True):
		print("{}\t{}".format(posInfo.pos, posInfo.count))



def parse(result):
	if result is None or not isinstance(result, Words):
		raise ValueError("Bad result")

	if not result.done():
		raise ValueError("Not enough canidates")

	viable_candidates = result.viable_candidates()
	print("✅ Finished parsing, found #{} candidate words".format(len(viable_candidates)))
	
	first = viable_candidates[0]

	if isinstance(first, WordCandidate):
		print("1️⃣ candidate: '{}', sum_of_occurences_of_base_word: #{}".format(first, first.sum_of_occurences_of_base_word))
	else:
		error_message = "Expected type: 'WordCandidate', but got type: '{}'".format(type(first))
		raise ValueError(error_message)

	candidates_sorted_by_frequency = sorted(viable_candidates, key=lambda c: c.sum_of_occurences_of_base_word, reverse=True)

	print("🤷‍♂️ #candidates_sorted_by_frequency: '{}'".format(len(candidates_sorted_by_frequency)))

	analyze_pos_distribution_of(candidates_sorted_by_frequency)
	
	output_elements = list(map(lambda wc: wc.as_result(), candidates_sorted_by_frequency))
	output_string = "\n".join(output_elements)

	output_file_name = 'output_swedish.txt'
	with open(output_file_name, "w") as text_file:
		print(f"{output_string}", file=text_file)

	print("🇸🇪 Outputted #{} words to file '{}'".format(len(output_elements), output_file_name))


def created_pos_tagged_doc_parole():
	file_name = 'stats_PAROLE.txt'

	words = Words(target_word_count=50)

	with open(file_name, 'r') as filehandle:
		for current_place in filehandle.readlines():
			line = current_place.rstrip() # without trailing newline
			
			words.parse(line)

			if words.done():
				break

	parse(result=words)
	
created_pos_tagged_doc_parole()