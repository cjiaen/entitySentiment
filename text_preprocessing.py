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
#input = "I feel that the new visitation policy is discriminatory. I think it should be abolished"
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
#get all coref resolutions and output to json

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
    json_output['analysis'].append(analysis_output)
    #print("\n")
#print(json.dumps(json_output))