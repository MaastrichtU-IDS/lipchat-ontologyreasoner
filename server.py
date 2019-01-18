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
nlp = sp.load('en_default')
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)

# Load ontology model
#print('Preloading ontology model...', file=sys.stderr)
from owlready2 import *
import os
cwd = os.getcwd()
ontology_base = 'data\\ontology\\'
ontology_path = ontology_base + 'maintenance.'
onto_path.append(ontology_base)
basepath = os.path.dirname(__file__)
filepath = os.path.abspath(os.path.join(basepath, ontology_path + "owl"))
ontology_prefix = basepath + '\\' + ontology_path
ontology_prefix_clean = basepath + '\\' + ontology_base
ontology = get_ontology(filepath).load()
ontology.load()
ontology_prefix = cwd + ontology_prefix 
iteration = 0


# test_issue = ontology.MaintenanceIssue("test_issue")
# test_use = ontology.BadUse("test_use")

# sync_reasoner()

# print("TEST1: ")
# print("-------")
# print()
# print(test_issue.__class__)

# print()
# print()

# print("TEST2: ")
# print("-------")
# print()

# test_issue.causedBy = [ test_use ]

# sync_reasoner()

# print(test_issue.__class__)

# print()
# print()

#Define ontology classes
# with ontology:
#     class LegalIssue(Thing):
#         response_classmap = {
#             ontology_prefix + 'MaintenanceIssue': 'Maintenance related issue.',
#             ontology_prefix + 'MinorIssue': 'The tenant is responsible for resolving the issue because:',
#             ontology_prefix + 'MajorIssue': 'The landlord is responsible for resolving the issue because:',
#             ontology_prefix + 'BadUse': 'The damage is caused by the tenants negligence (<a href="http://wetten.overheid.nl/BWBR0005290/2018-06-13#Boek7_Titeldeel4_Afdeling5_ParagraafOnderafdeling1_Artikel218">Section 218, Book 7</a>).',
#             ontology_prefix + 'NaturalCalamity': 'The damage has not been caused by the tenant (<a href="http://wetten.overheid.nl/BWBR0005290/2018-06-13#Boek7_Titeldeel4_Afdeling5_ParagraafOnderafdeling1_Artikel218">Section 218, Book 7</a>).',
#             ontology_prefix + 'SmallObject': 'The damaged object is small (<a href="http://wetten.overheid.nl/BWBR0005290/2018-06-13#Boek7_Titeldeel4_Afdeling5_ParagraafOnderafdeling1_Artikel240">Section 240, Book 7</a>).',
#             ontology_prefix + 'BigObject': 'The damaged object is large (<a href="http://wetten.overheid.nl/BWBR0005290/2018-06-13#Boek7_Titeldeel4_Afdeling5_ParagraafOnderafdeling1_Artikel240">Section 240, Book 7</a>).',
#             ontology_prefix + 'HighCost': 'The damage requires extensive actions to be resolved. (<a href="http://wetten.overheid.nl/BWBR0014931/2003-08-01">Minor Repairs Decree</a>).',
#             ontology_prefix + 'LowCost': 'The damage requires minor actionsto be resolved (<a href="http://wetten.overheid.nl/BWBR0014931/2003-08-01">Minor Repairs Decree</a>).',
#         }
#         ontology_properties = {
#             'causedBy': 'Was the damage caused by your actions?',
#             'associatedWithObject': 'What object was damaged?',
#             'hasCost': 'Does this object require more than 100 EURO to fix?'
#         }
#         ontology_property_classes = {
#             'causedBy': ['BadUse', 'NaturalCalamity'],
#             'associatedWithObject': ['BigObject', 'SmallObject'],
#             'hasCost': ['LowCost', 'HighCost']
#         }

        # Map resolved classes to their chatbot response
        # def GetResolvedOutput(self, resolved_class):
        #     return self.response_classmap.get(resolved_class)

        # # Get an explenation from a resolved class
        # def GetResolvedExplenation(self, resolved_class):
        #     explenation = []
        #     for property in self.ontology_properties:
        #         if property in dir(resolved_class):
        #             reasons = getattr(resolved_class, property)
        #             if len(reasons) > 0:
        #                 for reason in reasons:
        #                     class_str = str(reason.__class__).replace('\\', '/')
        #                     if '/' not in class_str:
        #                         class_str = ontology_prefix_clean + class_str
        #                     explenation.append(self.response_classmap.get(class_str))
        #     return explenation

        # # Get options
        # def GetOptionsByProperty(self, propertyName):
        #     if propertyName not in self.ontology_property_classes:
        #         return False
        #     propertyClasses = self.ontology_property_classes[propertyName]
        #     options = []
        #     for propertyClass in propertyClasses:
        #         for instance in ontology[propertyClass].instances():
        #             instance.lemma_ = lemmatizer(instance.name, 'VERB')[0]
        #             options.append(instance)
        #     return options

        # iteration = 0

        # def ResolveMaintenanceIssue(self, properties):
        #     self.iteration += 1
        #     print()
        #     print()
        #     # Create an instance from the given properties
        #     onto_instance = ontology.LegalIssue("maintenanceissue_" + str(self.iteration))
        #     #print("instance: " + str(onto_instance))
        #     print()
        #     print()
        #     print("properties: " + str(properties))
        #     print()
        #     print()
        #     for property in properties:
        #         #print("property: " + str(property))
        #         #print("other: " + str(properties.get(property)))
        #         setattr(onto_instance, property, properties.get(property))

        #     # Resolve the instance
        #     sync_reasoner()
        #     resolved_class = onto_instance.__class__
        #     print()
        #     print()
        #     print("TEST: " + str(resolved_class))
        #     print()
        #     print()
        #     resolved_classes = {
        #         ontology_prefix + 'MinorIssue',
        #         ontology_prefix + 'MajorIssue',
        #     }
        #     print()
        #     print()
        #     print("prefix: "  + str(ontology_prefix))
        #     print()
        #     print()
        #     resolved_class_str = str(resolved_class).replace('/', '\\')
            
        #     print("resolved: " + str(resolved_class_str))
        #     #
        #     #print("resolved class str" + str(resolved_class_str))

        #     if '\\' not in resolved_class_str:
        #         print("Kody1")
        #         resolved_class_str = ontology_prefix_clean + resolved_class_str
        #     if resolved_class_str in resolved_classes:
        #         print("Kody2")
        #         conclusion = self.GetResolvedOutput(resolved_class_str)
        #         support = self.GetResolvedExplenation(onto_instance)
        #         del onto_instance
        #         # close_world(onto_instance)
        #         return True, conclusion, support
        #     else:
        #         print("Kody3")
        #         conclusion = 'Not yet resolved! Need more facts.'
        #         missing = []
        #         for property in self.ontology_properties:
        #             if property not in properties:
        #                 missing.append({property: self.ontology_properties.get(property)})
        #         del onto_instance
        #         # close_world(onto_instance)
        #         print()
        #         print()
        #         print("missing: " + str(missing))
        #         print()
        #         print()
        #         return False, conclusion, missing

    # # Define possible maintenance conclusions
    # class MinorIssue(LegalIssue):
    #     equivalent_to = [
    #         ontology.MaintenanceIssue
    #         & (ontology.causedBy.some(ontology.BadUse) |
    #            ontology.associatedWithObject.some(ontology.SmallObject) |
    #            ontology.hasCost.some(ontology.LowCost))
    #     ]

    # class MajorIssue(LegalIssue):
    #     equivalent_to = [
    #         ontology.MaintenanceIssue
    #         & (ontology.causedBy.some(ontology.NaturalCalamity) &
    #            ontology.associatedWithObject.some(ontology.BigObject) &
    #            ontology.hasCost.some(ontology.HighCost))
    #     ]

# global sess
# sess = {}

# def set_errcnt(user, message):
#     # setattr(g, '_err_cnt', message)
#     sess[user] = message
#     return sess[user]


# def get_errcnt(user):
#     # err_cnt = getattr(g, '_err_cnt', None)
#     if not user in sess:
#         sess[user] = 0
#     return sess[user]


# conversations = {}
# asking = 'çausedBy'
# maint = LegalIssue()

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
    global iteration
    iteration += 1
    issue = ontology.MaintenanceIssue("issue" + str(iteration))
    if (request.args.get('usage') == '0'):
        print('seun0')
        use = ontology.BadUse("use" + str(iteration))
    else:
        print('seun1')
        use = ontology.WearAndTear("use" + str(iteration))

    if (request.args.get('propertyitem') == '0'):
        print('seun2')
        obj = ontology.BigObject("obj" + str(iteration))
    else:
        print('seun3')
        obj = ontology.SmallObject("obj" + str(iteration))

    if (request.args.get('actioncost') == '0'):
        print('seun4')
        cost = ontology.HighCost("cost" + str(iteration))
    else:
        print('seun5')
        cost = ontology.SmallObject("cost" + str(iteration))

    # link issue to properties using ontology relations
    issue.causedBy = [ use ]
    issue.associatedWithObject = [ obj ]
    issue.hasCost = [ cost ]

    sync_reasoner()

    print(issue.__class__)

    if ("MajorIssue" in str(issue.__class__)):
        response = {'text': 'The landlord may be responsible for resolving this issue.'}
        return jsonify(response)
    elif ("MinorIssue" in str(issue.__class__)):
        response = {'text': 'The tenant is generally responsible for repairing, replacing or maintaining such items in this case.'}
        return jsonify(response)
    else:
        response = {'text': 'I am not sure if the tenant or landlord is responsible for resolving this particular issue.'}
        return jsonify(response)

if __name__ == "__main__":
    port = 5577
    # print('Starting ontology server on port  ' + str(port), file=sys.stderr)
    app.run(host='0.0.0.0', port=port)
    # app.run(port=port)
