# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.services.home import blueprint
from flask import render_template, request, json
# from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.services.s3Manager.routes import getBucketSize
import requests
from apps import API_ENDPOINT, STORAGE_BUCKET


@blueprint.route('/')
# @login_required
def RedirectIndex():
    return index()

@blueprint.route('/index')
# @login_required
def index():
    return render_template("home/index.html", segment='index', total_img=photoSummary()["total_img"], total_size=photoSummary()["total_size"], labels=photoSummary()["labels"], categories=photoSummary()["categories"])

@blueprint.route('/renderLbl/<value>',methods=['GET', 'POST'])
def getPhotosPageLbl(value):
    photos = photoSummary(sentLabel=value)["labels"]
    
    print(photos )
    return render_template("photoUpload/photos.html", memcache=photos)

@blueprint.route('/renderCat/<value>',methods=['GET', 'POST'])
def getPhotosPageCat(value):
    photos = photoSummary(sentCategory=value)["categories"]
    print(photos)
    return render_template("photoUpload/photos.html", memcache=photos)

def photoSummary(sentLabel=None, sentCategory=None):
    photoData = json.loads(requests.post(API_ENDPOINT, json={
        "eventName": "GET_ALL_CACHE",
        "search_value": "build"
    }).content)['content']

    label = {}
    category = {}
    # print(photoData)
    for photo in photoData:
        for lbl in photoData[photo]['label']:
            if lbl in label:
                label[lbl][photo]=photoData[photo]
            else:
                label[lbl]={photo: photoData[photo]}
        for cat in photoData[photo]['category']:
            if cat in category:
                category[cat][photo]=photoData[photo]
            else:
                category[cat]={photo:photoData[photo]}

    total_bucket_size = getBucketSize(STORAGE_BUCKET)
    # print(total_bucket_size)
    # print(label)
    if sentLabel:
        label = label[sentLabel]
    
    if sentCategory:
        category = category[sentCategory]
    response = {
        "total_img": len(photoData),
        "total_size": str(round(total_bucket_size/1024/1024)) + ' MB',
        "labels": label,
        "categories": category,
    }

    # print(response)
    return response
    print(label)
    print(category)
        # print(photoData[photo]['label'])
        # print(photoData[photo]['label'])



# @blueprint.route('/<template>')
# # @login_required
# def route_template(template):

#     try:

#         if not template.endswith('.html'):
#             template += '.html'

#         # Detect the current page
#         segment = get_segment(request)

#         # Serve the file (if exists) from app/templates/home/FILE.html
#         return render_template("photoUpload/" + template, segment=segment.replace('.html', ''))

#     except TemplateNotFound:
#         return render_template('home/page-404.html'), 404

#     except:
#         return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
