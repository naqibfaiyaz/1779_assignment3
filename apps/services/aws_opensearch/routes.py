# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.services.aws_opensearch import blueprint
from flask import request, json, Response
from redis import Redis
import logging, requests
from requests.auth import HTTPBasicAuth
from apps import REDIS_ENDPOINT, STORAGE_URL, OS_ENDPOINT, OS_USERNAME, OS_PASSWORD

@blueprint.route('/put',methods=['POST'])
#Upload a new file to an existing bucket
def put_search_index(keyMd5=None, key=None, value=None, label=None, category=None):
    keyMd5Val = keyMd5 or request.form.get('keyMd5')
    keyName = key or request.form.get('key')
    val = value or request.form.get('value')
    lbl = label or request.form.get('label')
    cat = category or request.form.get('category')
    
    print(keyName, val)
    
    logging.basicConfig(level=logging.INFO)
    jsonObj={
        'img_url': STORAGE_URL + val,
        'label': lbl,
        'category': cat,
        'key': keyName,
        'keyMd5': keyMd5Val
    }
    # redis = Redis(host=REDIS_ENDPOINT, port=6379, decode_responses=True, ssl=True, username='myuser', password='MyPassword0123456789')
    response = requests.put(OS_ENDPOINT + "/photos/_doc/" + keyMd5Val,
            auth = HTTPBasicAuth(OS_USERNAME, OS_PASSWORD), json=jsonObj)
    
    if response:
        img_url=STORAGE_URL + val
    else:
        img_url=None

    return Response(json.dumps({"success": response, "content":{"key": keyName, "img": img_url, "label": lbl, "category": cat}, "msg": json.loads(response.content)}, default=str), status=200, mimetype='application/json')


@blueprint.route('/get',methods=['GET', 'POST'])
#Upload a new file to an existing bucket
def get_from_search_index(search=None):
    searchKey = search or request.form.get('search')

    logging.basicConfig(level=logging.INFO)
    # redis = Redis(host=REDIS_ENDPOINT, port=6379, decode_responses=True, ssl=True, username='myuser', password='MyPassword0123456789')
    
    response = json.loads(requests.get(OS_ENDPOINT + "/photos/_search?q=*" + searchKey + "*&pretty=true",
            auth = HTTPBasicAuth(OS_USERNAME, OS_PASSWORD)).content)['hits']['hits']

    all_matched={}
    for data in response:
        sanitizedData={
            "category": json.loads(data['_source']['category']),
            "label": json.loads(data['_source']['label']),
            "img": data['_source']['img_url'],
            "key": data['_source']['key']
        }
        all_matched[data['_source']['key']]=sanitizedData
        # all_matched.append({data['_source']['key']: sanitizedData})

    print(response)
    if response:
        response=response
        status=True
    else:
        status=False
    
    return Response(json.dumps({"success": status, "content": all_matched}, default=str), status=200, mimetype='application/json')

@blueprint.route('/delete', methods=['DELETE'])
#Upload a new file to an existing bucket
def delete_search_doc(keyMd5=None):
    keyMd5Val = keyMd5 or request.form.get('keyMd5')

    logging.basicConfig(level=logging.INFO)
    # redis = Redis(host=REDIS_ENDPOINT, port=6379, decode_responses=True, ssl=True, username='myuser', password='MyPassword0123456789')
    response = json.loads(requests.delete(OS_ENDPOINT + "/photos/_doc/" + keyMd5Val,
            auth = HTTPBasicAuth(OS_USERNAME, OS_PASSWORD)).content)
    
    print(response)
    if response:
        status=True
        msg=keyMd5Val + " removed successfully from cache."
    else:
        status=False
        msg=keyMd5Val + " not found in cache"
    
    return Response(json.dumps({"success": status, "content":{"key": keyMd5Val}, "msg": response}, default=str), status=200, mimetype='application/json')
