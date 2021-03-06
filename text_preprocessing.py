import spacy
import en_core_web_sm
import en_coref_md
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json
from collections import defaultdict

#load POS tagger and sentence parser
nlp = en_core_web_sm.load()
#load coreference resolution model
nlp = spacy.load("en_coref_md")
#print("nlp pipeline components are {}".format(nlp.pipe_names))

#load data
'''
input = "I feel that the new visitation policy is discriminatory. I think it should be abolished. I don't like this policy."
#input = "I feel discriminated by the new visitation policy. I think it should be abolished. I don't like this policy."
'''
input = "Robert DeNiro plays the most unbelievably intelligent illiterate of all time. \
This movie is so wasteful of talent, it is truly disgusting. The script is unbelievable. \
The dialog is unbelievable. Jane Fonda's character is a caricature of herself, and not a funny one. \
The movie moves at a snail's pace, is photographed in an ill-advised manner, and is insufferably preachy. \
It also plugs in every cliche in the book. Swoozie Kurtz is excellent in a supporting role, \
but so what? Equally annoying is this new IMDB rule of requiring ten lines for every review. \
When a movie is this worthless, it doesn't require ten lines of text to let other readers know \
that it is a waste of time and tape. Avoid this movie."

doc = nlp(input)
#print(doc._.coref_resolved)

json_output = defaultdict(list)
coref_output = defaultdict(list)
for cluster in doc._.coref_clusters:
    #identifying antecedents
    #print("Reference: {}".format(cluster.main))
    for section in cluster.mentions:
        #identifying anaphora, cataphora, coreferring noun phrases
        #outputs index of start and end token
        coref_output[cluster.main.text].append({'start':section.start, 'end':section.end})
json_output['coreference'] = coref_output
#json_output = json.dumps(json_output)
#print(json_output)


#get sentiment analyzer
sentiAnalyzer = SentimentIntensityAnalyzer()
#analysis_output_all = defaultdict(list)
for sent in doc.sents:
    #get sentiment score for each sentence
    #print(sent.text)
    #score and extract sentiment polarity scores
	#print(sentiAnalyzer.polarity_scores(sent.text))
	analysis_output = defaultdict(list)
	analysis_output['sentiment'] = sentiAnalyzer.polarity_scores(sent.text)
	#print(json.dumps(analysis_output))
	
	#implement grammar rules to tease out entity-sentiment relationships
	for token in sent:
		#print(token.text, token.pos_, token.dep_)
		analysis_output['dependency'].append({'text':token.text, 'pos':token.pos_, 'dep':token.dep_})
    
	#apply grammar rules here
	relationship_output = defaultdict(list)

	#initialize
	subject = ""
	object = ""
	temp_object = ""

	for count, token in enumerate(analysis_output['dependency']):
		#print("token:{}, dep:{}".format(token['text'], token['dep']))
		
		### Identifying and extracting subjects ###
		#Base case: plain old nsubj
		if token['dep']=='nsubj':
			subject = token['text']
			
			#Rule 1: Check if it is a compound entity
			if count-1 >= 0:
				#check not the first token
				token_minus_1 = analysis_output['dependency'][count-1]
				if token_minus_1['dep']=='compound' and token['dep']=='nsubj':
					subject = " ".join([token_minus_1['text'], token['text']])
			
			#Rule 2: If nsubj is preceded by possessive and case dependencies, extract compound, poss, case and nsubj
				#check that there are at least 3 more token behind
				if count-3 >= 0:
					token_minus_2 = analysis_output['dependency'][count-2]
					token_minus_3 = analysis_output['dependency'][count-3]
					if token_minus_3['dep']=='compound' and token_minus_2['dep']=='poss' and token['dep']=='nsubj':
						subject = " ".join([token_minus_3['text'], token_minus_2['text']+token_minus_1['text'], token['text']])
			#print("Subject: {}".format(subject))

		### Identifying and extracting objects ###
		#Base case: plain old dobj (extracting direct objects)
		if token['dep']=='dobj':
			object = token['text']
			#Rule 1: Check if it is a compound entity
			if count-1 >= 0:
				#check not the first token
				token_minus_1 = analysis_output['dependency'][count-1]
				if token_minus_1['dep']=='compound' and token['dep']=='dobj':
					object = " ".join([token_minus_1['text'], token['text']])

		#Rule 2: temporarily store prepositional objects. Direct objects 
		if token['dep']=='pobj':
			temp_object = token['text']
	#Following from rule #2, if no direct object present, use pobj
	if object == "" and temp_object != "":
		object = temp_object
	
	#Rule 3: Sentences without subjects (Imperative/Axiomatic expression)
	if object != "" and subject == "":
		subject = "(Author)"
	
	#Rule 4: Sentences without objects ()
	if object == "" and subject != "":
		object = subject
		subject = "(Author)" 
	
	#print final object identified
	#if object != "": print("Object: {}".format(object))

	json_output['raw'].append(analysis_output)
	json_output['relationship'].append({'subject':subject, 'object':object, 'sentiment':analysis_output['sentiment']['compound']})
    
	#print("\n")
print(json.dumps(json_output))