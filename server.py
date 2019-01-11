# encoding=utf8

import sys
import spacy as sp
from flask import Flask, request, jsonify, session
from flask_cors import CORS, cross_origin
import urllib.request
import urllib.parse

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
CORS(app, support_credentials=True)
#print('Initiating ontology server...', file=sys.stderr)

# Load language model
#print('Preloading language model...', file=sys.stderr)
nlp = sp.load('en')
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)

# Load ontology model
#print('Preloading ontology model...', file=sys.stderr)
from owlready2 import *
ontology_base = 'data/ontology/'
ontology_path = ontology_base + 'maintenance.'
onto_path.append(ontology_base)
basepath = os.path.dirname(__file__)
filepath = os.path.abspath(os.path.join(basepath, ontology_path + "owl"))
ontology_prefix = basepath + '/' + ontology_path
ontology_prefix_clean = basepath + '/' + ontology_base
ontology = get_ontology(filepath).load()
ontology.load()

# Define ontology classes
with ontology:
    class Maintenance(Thing):
        response_classmap = {
            ontology_prefix + 'Damage': 'Maintenance related issue.',
            ontology_prefix + 'TenantInCharge': 'The tenant is responsible for resolving the issue because:',
            ontology_prefix + 'LandlordInCharge': 'The landlord is responsible for resolving the issue because:',
            ontology_prefix + 'BadUse': 'The damage is caused by the tenants bad use (<a href="http://wetten.overheid.nl/BWBR0005290/2018-06-13#Boek7_Titeldeel4_Afdeling5_ParagraafOnderafdeling1_Artikel218">Section 218, Book 7</a>).',
            ontology_prefix + 'NaturalCause': 'The damage is not caused by the tenant (<a href="http://wetten.overheid.nl/BWBR0005290/2018-06-13#Boek7_Titeldeel4_Afdeling5_ParagraafOnderafdeling1_Artikel218">Section 218, Book 7</a>).',
            ontology_prefix + 'SmallObject': 'The damaged object is small (<a href="http://wetten.overheid.nl/BWBR0005290/2018-06-13#Boek7_Titeldeel4_Afdeling5_ParagraafOnderafdeling1_Artikel240">Section 240, Book 7</a>).',
            ontology_prefix + 'BigObject': 'The damaged object is big (<a href="http://wetten.overheid.nl/BWBR0005290/2018-06-13#Boek7_Titeldeel4_Afdeling5_ParagraafOnderafdeling1_Artikel240">Section 240, Book 7</a>).',
            ontology_prefix + 'MajorAction': 'The damage requires a big effort to be resolved. (<a href="http://wetten.overheid.nl/BWBR0014931/2003-08-01">Minor Repairs Decree</a>).',
            ontology_prefix + 'MinorAction': 'The damage requires a small effort to be resolved (<a href="http://wetten.overheid.nl/BWBR0014931/2003-08-01">Minor Repairs Decree</a>).',
        }
        ontology_properties = {
            'causedBy': 'Did you cause the damage yourself (through bad use)?',
            'hasSize': 'What object is damaged?',
            'require': 'What action is required to fix the damaged object?'
        }
        ontology_property_classes = {
            'causedBy': ['BadUse', 'NaturalCause'],
            'hasSize': ['BigObject', 'SmallObject'],
            'require': ['MinorAction', 'MajorAction']
        }

        # Map resolved classes to their chatbot response
        def GetResolvedOutput(self, resolved_class):
            return self.response_classmap.get(resolved_class)

        # Get an explenation from a resolved class
        def GetResolvedExplenation(self, resolved_class):
            explenation = []
            for property in self.ontology_properties:
                if property in dir(resolved_class):
                    reasons = getattr(resolved_class, property)
                    if len(reasons) > 0:
                        for reason in reasons:
                            class_str = str(reason.__class__).replace('\\', '/')
                            if '/' not in class_str:
                                class_str = ontology_prefix_clean + class_str
                            explenation.append(self.response_classmap.get(class_str))
            return explenation

        # Get options
        def GetOptionsByProperty(self, propertyName):
            if propertyName not in self.ontology_property_classes:
                return False
            propertyClasses = self.ontology_property_classes[propertyName]
            options = []
            for propertyClass in propertyClasses:
                for instance in ontology[propertyClass].instances():
                    instance.lemma_ = lemmatizer(instance.name, 'VERB')[0]
                    options.append(instance)
            return options

        iteration = 0

        def ResolveMaintenanceIssue(self, properties):
            self.iteration += 1

            # Create an instance from the given properties
            onto_instance = ontology.Maintenance("maintenance_" + str(self.iteration))
            for property in properties:
                setattr(onto_instance, property, properties.get(property))

            # Resolve the instance
            sync_reasoner()
            resolved_class = onto_instance.__class__
            resolved_classes = {
                ontology_prefix + 'TenantInCharge',
                ontology_prefix + 'LandlordInCharge',
            }
            resolved_class_str = str(resolved_class).replace('\\', '/')
            if '/' not in resolved_class_str:
                resolved_class_str = ontology_prefix_clean + resolved_class_str
            if resolved_class_str in resolved_classes:
                conclusion = self.GetResolvedOutput(resolved_class_str)
                support = self.GetResolvedExplenation(onto_instance)
                del onto_instance
                # close_world(onto_instance)
                return True, conclusion, support
            else:
                conclusion = 'Not yet resolved! Need more facts.'
                missing = []
                for property in self.ontology_properties:
                    if property not in properties:
                        missing.append({property: self.ontology_properties.get(property)})
                del onto_instance
                # close_world(onto_instance)
                return False, conclusion, missing

    # Define possible maintenance conclusions
    class TenantInCharge(Maintenance):
        equivalent_to = [
            ontology.Damage
            & (ontology.causedBy.some(ontology.BadUse) |
               ontology.hasSize.some(ontology.SmallObject) |
               ontology.require.some(ontology.MinorAction))
        ]

    class LandlordInCharge(Maintenance):
        equivalent_to = [
            ontology.Damage
            & (ontology.causedBy.some(ontology.NaturalCause) &
               ontology.hasSize.some(ontology.BigObject) &
               ontology.require.some(ontology.MajorAction))
        ]

global sess
sess = {}

def set_errcnt(user, message):
    # setattr(g, '_err_cnt', message)
    sess[user] = message
    return sess[user]


def get_errcnt(user):
    # err_cnt = getattr(g, '_err_cnt', None)
    if not user in sess:
        sess[user] = 0
    return sess[user]


conversations = {}
maint = Maintenance()

from nltk import wordpunct_tokenize
from nltk.corpus import stopwords


@app.route("/language", methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def detect_language():
    userText = request.args.get('msg')

    probabilities = {}

    tokens = wordpunct_tokenize(userText)
    words = [word.lower() for word in tokens]

    for lang in stopwords.fileids():
        stopwords_set = set(stopwords.words(lang))
        words_set = set(words)
        common_words = words_set.intersection(stopwords_set)

        probabilities[lang] = len(common_words)

    return max(probabilities, key=probabilities.get)


@app.route("/get", methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def get_bot_response():
    userText = request.args.get('msg')

    # Retrieve conversation history
    known_information = {}
    first_entry = False
    userToken = request.args.get('token')
    error_cnt = get_errcnt(userToken)
    asking = 'causedBy'
    if userToken != "" and userToken in conversations:
        known_information = conversations[userToken]['status']
        if 'asking' in conversations[userToken]:
            asking = conversations[userToken]['asking']
    else:
        first_entry = True
        asking = 'causedBy'
        pass

    # Parse input (extract new information compatible with ontology)
    # Match input and find best matching instance
    for property in Maintenance.ontology_properties:
        if property not in known_information:
            options = maint.GetOptionsByProperty(property)
            parsed_property = False
            doc = nlp(userText)
            for token in doc:
                if token.lemma_ != '-PRON-' and token.pos not in ['DET', 'INTJ']:
                    # if token.lemma_ != '-PRON-' and token.pos_ == 'VERB':

                    # Construct object phrases (assuming only 2 different classes exist, rewrite this method and the word2vec service if multi class classification is needed)
                    phrase1_class = ''
                    phrase2_class = ''
                    phrase1 = ''
                    phrase2 = ''
                    for option in options:
                        if phrase1_class == '' or phrase1_class == option.__class__:
                            phrase1_class = option.__class__
                            phrase1 += ' ' + option.name
                        elif phrase2_class == '' or phrase2_class == option.__class__:
                            phrase2_class = option.__class__
                            phrase2 += ' ' + option.name

                        # Classify using exact string matching
                        if token.lower_ == option.name or token.lemma_ == option.lemma_:
                            parsed_property = option.__class__

                    # Classify using word similarity if string matching gave no results (uses word2vec service on same host)
                    # Only when directly asking for this response and not on first entry
                    if not parsed_property and len(token.lower_) > 2 and asking == property and first_entry == False:
                        url = 'http://127.0.0.1:5566/classify?text=' + token.lower_ + '&phrase1=' + phrase1 + '&phrase2=' + phrase2
                        url = url.replace(" ", "%20")
                        f = urllib.request.urlopen(url)
                        object_class = f.read().decode('utf-8')
                        if object_class != '' and object_class != 'UNCLASSIFIED':
                            if object_class == 'phrase1':
                                parsed_property = phrase1_class
                            elif object_class == 'phrase2':
                                parsed_property = phrase2_class

            # Add instance to list of known information
            if parsed_property:
                known_information[property] = [parsed_property()]

    # Test
    # known_information = {
    # 	'causedBy': [ontology.BadUse()],
    # 	# 'causedBy': [ontology.NaturalCause()],
    # 	# 'require': [ontology.bleeding],
    # 	# 'hasSize': [ontology.BigObject()],
    # 	# 'require': [ontology.MajorAction()],
    # }

    response = {'text': 'Sorry, I do not understand.'}
    conversation_status = {
        'status': known_information
    }
    [resolved, conclusion, support] = maint.ResolveMaintenanceIssue(known_information)
    if resolved:
        # response = conclusion + '\n' + str(support)
        response = {'text': conclusion,
                    'support': support}
    elif len(support) > 0:
        response = {'ask': support[0]}
        conversation_status['asking'] = list(support[0].keys())[0]

    # Save status
    conversations[userToken] = conversation_status
    if error_cnt > 0:
        response = {'text': 'Sorry, I could not be of assistance. Could you try again?'}
        set_errcnt(userToken, 0)
        # known_information = {}
        first_entry = True
        asking = 'çaused_by'
        if userToken in conversations:
            del conversations[userToken]
            del conversation_status
            del known_information
            print('done')
    if 'text' in response and "understand" in response['text']:
        # error_cnt = get_errcnt(userToken)
        error_cnt += 1
        set_errcnt(userToken, error_cnt)
        # response['text'] = response['text'] + str(get_errcnt(userToken))

    print(response)

    return jsonify(response)


if __name__ == "__main__":
    port = 5577
    # print('Starting ontology server on port  ' + str(port), file=sys.stderr)
    app.run(host='0.0.0.0', port=port)
    # app.run(port=port)
