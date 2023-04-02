# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.services.photoUpload import blueprint
from flask import render_template, request, redirect, url_for, json
import requests
from jinja2 import TemplateNotFound
from apps import logger, grafanaUrl, API_ENDPOINT
from apps.services.home.routes import get_segment
from apps.services.helper import upload_file, removeAllImages
from apps.services.aws_dynamo.routes import update_key, get_key, get_keys_from_db, delete_key
from apps.services.aws_sqs.routes import produce_queue

@blueprint.route('/index')
# @login_required
def index():
    return render_template('home/index.html', segment='index')


@blueprint.route('/<template>')
# @login_required
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        if segment=='photos.html':
            return render_template("photoUpload/photos.html", memcache=getAllPhotos()) # needed for Core FE EC2 instance
        if segment=='dashboard.html': 
            return render_template("photoUpload/dashboard.html", grafanaUrl=grafanaUrl) # needed for app-manager EC2 instance
        elif segment=='knownKeys.html':
            return render_template("photoUpload/knownKeys.html", keysFromDB=getDBAllPhotos()) # needed for Core FE EC2 instance
        # elif segment=='cache.html':
        #     return render_template("photoUpload/cache.html", policies=getPolicy())
        return render_template("photoUpload/" + template, segment=segment.replace('.html', ''))

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except Exception as e:
        logger.error(str(e))
        return render_template('home/page-500.html'), 500


@blueprint.route('/put',methods=['POST', 'PUT'])
def putPhoto():
    # UPLOAD_FOLDER = apps.app_c'/static/assets/public/'
    # ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    medium=request.form.get('medium')
    key = request.form.get('key') 
    file = request.files['image']
    print(key, file)
    if key and file:
        upload_response = upload_file(file)
        print(upload_response)
        if upload_response:
            # db_response = json.loads(update_key(key, upload_response).data)
            # put_search_index(db_response['data']['key']['key_md5'], db_response['data']['key']['key'], db_response['data']['new_value'])
            queue_response = produce_queue(key, upload_response)
            # print(json.loads(queue_response.data))
            # if db_response:
                # cache_response = json.loads(put_cache(key, upload_response).data)
                # print(cache_response)
        # response = putPhotoInMemcache(key, file)
        
        # logger.info('Put request received- ' + str(response))
        if medium and medium=='api':
            return queue_response
        else:
            return render_template("photoUpload/addPhoto.html", msg="Key added to the queue, please wait a bit for the data")
    elif key:
        cache_response = json.loads(requests.post(API_ENDPOINT, json={
            "eventName": "GET_SINGLE_CACHE",
            "key": key
        }).content)
        if medium and medium=='api':
            return cache_response
        else:
            if 'success' in cache_response and cache_response['success']:
                return render_template("photoUpload/addPhoto.html", msg="Key exists, please upload a new image", data=cache_response["content"], key=key)
        
        checkInDB = json.loads(get_key(key).data)
        if 'success' in checkInDB and checkInDB['success']:
            cache_response = json.loads(requests.post(API_ENDPOINT, json={
                "eventName": "PUT_CACHE",
                "key": checkInDB['content']['key'],
                "img_url": checkInDB['content']['img_url'],
                "label": checkInDB['content']['labels'],
                "categories": checkInDB['content']['categories']
            }).content)
            
            print(cache_response)
            if medium and medium=='api':
                return cache_response
            else:
                if cache_response['success']:
                    return render_template("photoUpload/addPhoto.html", msg="Key exists, please upload a new image", data=cache_response["content"], key=key)
                else:
                    return render_template("photoUpload/addPhoto.html", msg="Key/Image mismatch, please upload properly")
    
    return render_template("photoUpload/addPhoto.html", msg="Key/Image mismatch, please upload properly")
    

# @blueprint.route('/get', defaults={'url_key': None}, methods=['POST'])
@blueprint.route('/get/<url_key>',methods=['GET'])
def getSinglePhoto(url_key):
    medium=request.form.get('medium')
    cache_response = json.loads(requests.post(API_ENDPOINT, json={
            "eventName": "GET_SINGLE_CACHE",
            "key": url_key
        }).content)

    if medium and medium=='api':
        return cache_response
    else:
        if 'success' in cache_response and cache_response['success']:
            return render_template("photoUpload/addPhoto.html", data=cache_response["content"], key=url_key)
        elif "content" not in cache_response and "error" in cache_response:
            return render_template("photoUpload/addPhoto.html", msg=cache_response["error"]["message"], key=url_key)

@blueprint.route('/getAllCache',methods=['POST'])
def getAllPhotos():
    return json.loads(requests.post(API_ENDPOINT, json={
        "eventName": "GET_ALL_CACHE",
        "search_value": "build"
    }).content)['content']

@blueprint.route('/invalidate_key/<url_key>',methods=['GET', 'POST'])
def invalidateKey(url_key) :
    response = json.loads(requests.post(API_ENDPOINT, json={
        "eventName": "REMOVE_CACHE",
        "key": url_key
    }).content)
    logger.info("invalidateKey response: " + str(response))
    
    return redirect(url_for("photoUpload_blueprint.route_template", template="photos.html"))

@blueprint.route('/getAllFromDB',methods=['POST'])
def getDBAllPhotos():
    return json.loads(get_keys_from_db().data)["content"]


@blueprint.route('/deleteAllKeys',methods=['GET'])
def deleteAllKeys():
    bucket_response = removeAllImages()
    print(bucket_response)
    
    if 'success' in bucket_response and bucket_response['success']:
        allPhotos=getDBAllPhotos()
        print(allPhotos)
        i=0
        for photo in allPhotos:
            print(photo)
            response = delete_key(photo)
            if response.status_code==200:
                i=i+1

        if len(allPhotos)==i:
            msg="All Keys are deleted"
        else:
            msg=i + " Keys are deleted"
    else: 
        msg="No image to delete"

    return redirect(url_for("photoUpload_blueprint.route_template", template="knownKeys.html", msg=msg))

@blueprint.route('/getSearchedData', methods=['POST'])
def getSearchedPhotos():
    response = json.loads(requests.post(API_ENDPOINT, json={
        "eventName": "FULL_TEXT_SEARCH",
        "search_value": request.form.get('search')
    }).content)['content']
    # return json.dumps(response['content'])
    return render_template("photoUpload/photos.html", memcache=response)
# @blueprint.route('/changePolicy',methods=['POST'])
# def changePolicy():
#     policy = request.form.get("replacement_policy")
#     newCapacity = int(request.form.get("capacity"))
    
#     response = changePolicyInDB(policy, newCapacity*1024*1024).json()

#     print(response)
#     if 'success' in response and response['success']=='true':
#         return redirect(url_for("photoUpload_blueprint.route_template", template="cache.html"))
        
# @blueprint.route('/getCurrentPolicy',methods=['POST'])
# def getPolicy():
#     return getPolicyFromDB('52.87.212.134')['content']