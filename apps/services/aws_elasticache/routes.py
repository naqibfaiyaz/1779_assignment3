# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.services.aws_elasticache import blueprint
from flask import request, json, Response
from redis import Redis
import logging
from apps import REDIS_ENDPOINT, STORAGE_URL

@blueprint.route('/put',methods=['POST'])
#Upload a new file to an existing bucket
def put_cache(key=None, value=None, label=None, category=None):
    keyName = key or request.form.get('key')
    val = value or request.form.get('value')
    lbl = label or request.form.get('label')
    cat = category or request.form.get('category')
    
    print(keyName, val)
    
    logging.basicConfig(level=logging.INFO)
    jsonObj={
        'img_url': val,
        'label': lbl,
        'category': cat
    }
    # redis = Redis(host=REDIS_ENDPOINT, port=6379, decode_responses=True, ssl=True, username='myuser', password='MyPassword0123456789')
    redis = Redis(host=REDIS_ENDPOINT)

    if redis.ping():
        response = redis.set(keyName, json.dumps(jsonObj))

    if response:
        msg = keyName + " successfully Saved."
        img_url=STORAGE_URL + val
    else:
        msg = "Something went wrong, could not save to the cache"
        img_url=None

    return Response(json.dumps({"success": response, "content":{"key": keyName, "img": img_url, "label": lbl, "category": cat}, "msg": msg}, default=str), status=200, mimetype='application/json')


@blueprint.route('/get',methods=['GET', 'POST'])
#Upload a new file to an existing bucket
def get_cache(key=None):
    keyName = key or request.form.get('key')

    logging.basicConfig(level=logging.INFO)
    # redis = Redis(host=REDIS_ENDPOINT, port=6379, decode_responses=True, ssl=True, username='myuser', password='MyPassword0123456789')
    redis = Redis(host=REDIS_ENDPOINT)

    if redis.ping():
        response = json.loads(redis.get(keyName))
        print(response)
        if response:
            response=response
            status=True
            img_url=STORAGE_URL + response['img_url']
        else:
            status=False
            img_url=None
    
    return Response(json.dumps({"success": status, "content":{"key": keyName, "img": img_url, "label": response["label"], "category": response["category"]}}, default=str), status=200, mimetype='application/json')

@blueprint.route('/delete', methods=['DELETE'])
#Upload a new file to an existing bucket
def delete_cache(key=None):
    keyName = key or request.form.get('key')

    logging.basicConfig(level=logging.INFO)
    # redis = Redis(host=REDIS_ENDPOINT, port=6379, decode_responses=True, ssl=True, username='myuser', password='MyPassword0123456789')
    redis = Redis(host=REDIS_ENDPOINT)
    
    if redis.ping():
        response = redis.get(keyName)
        
        print(response)
        if response:
            response=response.decode()
            delete_response = redis.delete(keyName)
            print(delete_response)
            if delete_response:
                status=True
                msg=keyName + " removed successfully from cache."
            else:
                status=True
                msg="Something went wrong while deleting from cache."
        else:
            status=False
            msg=keyName + " not found in cache"
    
    return Response(json.dumps({"success": status, "content":{"key": keyName}, "msg": msg}, default=str), status=200, mimetype='application/json')

@blueprint.route('/get_all',methods=['GET', 'POST'])
#Upload a new file to an existing bucket
def get_all_cache():
    # keyName = key or request.form.get('key')

    logging.basicConfig(level=logging.INFO)
    # redis = Redis(host=REDIS_ENDPOINT, port=6379, decode_responses=True, ssl=True, username='myuser', password='MyPassword0123456789')
    redis = Redis(host=REDIS_ENDPOINT)
    allCache={'content':{},'keys':[], 'success': None}
    if redis.ping():
        for key in redis.scan_iter():
            keyName=key.decode()
            print(keyName)
            key_value=json.loads(get_cache(keyName).data)["content"]
            print(key_value)
            allCache['content'][keyName]=key_value
            # allCache.append({"content":})
        allCache['keys']=list(allCache['content'].keys())
        allCache['success']='true'
    
    return Response(json.dumps(allCache, default=str), status=200, mimetype='application/json')