import nltk
from collections import defaultdict

class POSInfo(object):

	def __init__(self, pos, word):
		self.pos = pos
		self.count = 1
		self.words = [word]
		self.percentage = 0.0

	def increase_counter(self, word):
		self.count += 1
		self.percentage = self.count/2048
		self.words.append(word)

def read_languages_file(file_name):
	# define empty list
	words = []

	# open file and read the content in a list
	with open(file_name, 'r') as filehandle:
	    words = [current_place.rstrip() for current_place in filehandle.readlines()]

	print("✅ Read #{} words from '{}'".format(len(words), file_name))

	return words

def distribution_of_pos_tag_english():
	english = read_languages_file('english.txt')
	pos_tagged_tuples = nltk.pos_tag(english)

	# count_pos = defaultdict(int)
	count_pos = {}

	for pos_tuple in pos_tagged_tuples:
		(word, pos_tag) = pos_tuple
		if pos_tag in count_pos:
			count_pos[pos_tag].increase_counter(word)
		else:
			count_pos[pos_tag] = POSInfo(pos_tag, word)

	# count_pos_percentage = defaultdict(float)
	# for pos_tag, pos_tag_count in count_pos.items():
	# 	percentage =  pos_tag_count/len(english)
	# 	count_pos_percentage[pos_tag] = percentage
	# 	print("Found {}% '{}'".format((percentage*100), pos_tag))
	for posInfo in sorted(count_pos.values(), key=lambda e: e.count, reverse=True):
		print("{}\t{}".format(posInfo.pos, posInfo.count))
		# if posInfo.count < 20:
			# print("{}\n\n".format(posInfo.words))
		# print("\n⭐️===== {} =====\n".format(posInfo.pos))
		# print("🎉 {}% (#{} words) have tag '{}', among them are: \n\n{}\n".format((posInfo.percentage*100), posInfo.count, posInfo.pos, posInfo.words))

distribution_of_pos_tag_english()