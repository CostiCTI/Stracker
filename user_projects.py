'''
	This file contains contains functions for elasticsearch operations
'''

import time
import json
import math
import pickle

from datetime import datetime
from elasticsearch import Elasticsearch


def delete_last_phase(index, event_date, username):

	ES_HOST = {"host" : "localhost", "port" : 9200}
	es = Elasticsearch()
	project_name = 'measure_' + username + "_" + index

	query = {
		"query": { 
			"match": {
				"insert_date": event_date,
				# trebuie si asta "user": username
			}
		}
	}

	es.delete_by_query(index=project_name, doc_type='metric', body=query)


def delete_project(project_name, username):
	'''
		This function delete an index in elasticsearch

	Parameters:
	-----------
	project_name	string, name of the index

	Returns:
	--------
	None
	'''
	project = "measure_" + username + "_" + project_name
	es = Elasticsearch()
	es.indices.delete(index=project)


def get_projects(username):
	'''
		This function returns all indexes from elasticsearch that
	start with substring 'measure_'

	Parameters:
	-----------
	None

	Returns:
	--------
	list of indexes
	'''
	es = Elasticsearch()
	projects = []

	for index in es.indices.get('*'):
		if index.startswith("measure_" + username + "_"):
			projects.append(index[(9 + len(username)):])

	return projects


def load_model(file_name): 
    # load the model
    filename = file_name + '.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
    
    return loaded_model


def get_score(d, option):

	MODELCOMM = load_model('models/model_lr_codecomm')
	MODELCSV = load_model('models/model_lr_code_smells_violations')
	MODELLCOMP = load_model('models/model_lr_ncloc_classes')
	MODELVMIN = load_model('models/model_lr_violations_minor')
	MODELLF = load_model('models/model_lr_ncloc_functions')
	MODELLCOMP2 = load_model('models/model_lr_ncloc_classes_2')
	MODELLF2 = load_model('models/model_lr_ncloc_functions_min')

	compred = math.floor((MODELCOMM.predict(float(d['ncloc'])))[0][0])
	csvpred = math.floor((MODELCSV.predict(float(d['code_smells'])))[0][0])
	if int(d['ncloc']) < 6700:
		lcpred = math.floor((MODELLCOMP2.predict(float(d['ncloc'])))[0][0])
	else:
		lcpred = math.floor((MODELLCOMP.predict(float(d['ncloc'])))[0][0])
	vminpred = math.floor((MODELVMIN.predict(float(d['violations'])))[0][0])
	if int(d['ncloc']) < 4300:
		nclocfunpred = math.floor((MODELLF2.predict(float(d['ncloc'])))[0][0])
	else:
		nclocfunpred = math.floor((MODELLF.predict(float(d['ncloc'])))[0][0])

	if compred < 0:
		compred = 0

	if option == "comments" or option == "functions" or option == "classes":
		if compred < 0:
			compred = 0
		m = d[option]
		mp = compred
		score = 0
		dif = abs(m - mp)
		if mp != 0:
			p = dif * 100 / mp
		else:
			p = 100
		if p <= 10:
			score = 5
		elif p <= 25:
			score = 4
		elif p <= 45:
			score = 3
		elif p <= 70:
			score = 2
		else:
			score = 1

		return score

	elif option == "code_smells_viola":
		m = d['code_smells']
		mp = csvpred
	elif option == "complexity":
		m = d['lines']
		mp = lcpred
	elif option == "violations":
		m = d['violations']
		mp = vminpred
	else:
		m = d['functions']
		mp = nclocfunpred

	return 3


def add_phase(index, d, username):

	ES_HOST    = {"host" : "localhost", "port" : 9200}
	INDEX_NAME = 'measure_' + username + "_" + index
	TYPE_NAME  = 'metric'
	
	es = Elasticsearch()

	MODELCOMM = load_model('models/model_lr_codecomm')
	MODELCSV = load_model('models/model_lr_code_smells_violations')
	MODELLCOMP = load_model('models/model_lr_ncloc_classes')
	MODELVMIN = load_model('models/model_lr_violations_minor')
	MODELLF = load_model('models/model_lr_ncloc_functions')
	MODELLCOMP2 = load_model('models/model_lr_ncloc_classes_2')
	MODELLF2 = load_model('models/model_lr_ncloc_functions_min')

	compred = math.floor((MODELCOMM.predict(float(d['ncloc'])))[0][0])
	csvpred = math.floor((MODELCSV.predict(float(d['code_smells'])))[0][0])
	if int(d['ncloc']) < 6700:
		lcpred = math.floor((MODELLCOMP2.predict(float(d['ncloc'])))[0][0])
	else:
		lcpred = math.floor((MODELLCOMP.predict(float(d['ncloc'])))[0][0])
	vminpred = math.floor((MODELVMIN.predict(float(d['violations'])))[0][0])
	if int(d['ncloc']) < 4300:
		nclocfunpred = math.floor((MODELLF2.predict(float(d['ncloc'])))[0][0])
	else:
		nclocfunpred = math.floor((MODELLF.predict(float(d['ncloc'])))[0][0])

	if compred < 0:
		compred = 0
	if csvpred < 0:
		csvpred = 0
	if lcpred < 0:
		lcpred = 0
	if vminpred < 0:
		vminpred = 0
	if vminpred > int(d['violations']):
		vminpred = d['violations']
	if nclocfunpred < 0:
		nclocfunpred = 0
	if nclocfunpred > float(d['ncloc']) * 5:
		nclocfunpred = float(d['ncloc']) / 5

	x = es.index(index=INDEX_NAME, doc_type='metric', body={
		'user': username,
		'insert_date': int(time.time() * 1000),
		'lines': float(d['lines']),
		'ncloc': float(d['ncloc']),
		'comments': float(d['comment_lines']),
		'comments_pred': compred,
		'violations': float(d['violations']),
		'violations_pred': csvpred,
		'minor_violations': float(d['minor_violations']),
		'minor_violations_pred': vminpred,
		'major_violations': float(d['major_violations']),
		'code_smells': float(d['code_smells']),
		'bugs': float(d['bugs']),
		'vulnerabilities': float(d['vulnerabilities']),
		'files': float(d['files']),
		'classes': float(d['classes']),
		'classes_pred': lcpred,
		'functions': float(d['functions']),
		'functions_pred': nclocfunpred,
		'complexity': float(d['complexity']),
	})


def get_project_data(index, username):

	ES_HOST    = {"host" : "localhost", "port" : 9200}
	INDEX_NAME = 'measure_' + username + "_" + index
	TYPE_NAME  = 'metric'
	
	es = Elasticsearch()

	query = {
		'size': 1000,
		'query': {
			"match": {
            	"user": username
          		}
			}
		}

	res = es.search(index=INDEX_NAME, body=query)

	result = []
	for r in res['hits']['hits']:
		d = r['_source']
		result.append(d)

	return result




def create_new_project(index, username):
	'''
		Create a new index with a starting registration

	Parameters:
	-----------
	index	string, name of the new index

	Returns:
	--------
	None
	'''

	ES_HOST    = {"host" : "localhost", "port" : 9200}
	INDEX_NAME = 'measure_' + username + "_" + index
	TYPE_NAME  = 'metric'

	es = Elasticsearch()

	request_body = {
			"settings" : {
				"number_of_shards": 5,
				"number_of_replicas": 1
			},

			'mappings': {
				INDEX_NAME: {
					'properties': {
						'user': {'type': 'string'},
						'insert_date': {'type': 'date'},
						'lines': {'type': 'float'},
						'ncloc': {'type': 'float'},
						'comments': {'type': 'float'},
						'comments_pred': {'type': 'float'},
						'violations': {'type': 'float'},
						'violations_pred': {'type': 'float'},
						'minor_violations': {'type': 'float'},
						'minor_violations_pred': {'type': 'float'},
						'major_violations': {'type': 'float'},
						'code_smells': {'type': 'float'},
						'bugs': {'type': 'float'},
						'vulnerabilities': {'type': 'float'},
						'files': {'type': 'float'},
						'classes': {'type': 'float'},
						'functions': {'type': 'float'},
						'functions_pred': {'type': 'float'},
						'complexity': {'type': 'float'},
						'classes_pred': {'type': 'float'}
					}}}
		}

	es.indices.create(index = INDEX_NAME, body = request_body)


	es.index(index=INDEX_NAME, doc_type='metric', id=0, body={
		'user': username,
		'insert_date': int(time.time() * 1000),
		'lines': 0,
		'ncloc': 0,
		'comments': 0,
		'comments_pred': 0,
		'violations': 0,
		'violations_pred': 0,
		'minor_violations': 0,
		'minor_violations_pred': 0,
		'major_violations': 0,
		'code_smells': 0,
		'bugs': 0,
		'vulnerabilities': 0,
		'files': 0,
		'classes': 0,
		'functions': 0,
		'functions_pred': 0,
		'complexity': 0,
		'classes_pred': 0
	})


#add_phase('measure_audi', 226, 63, 112, 318, 298)
#get_project_data('zet')