# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.services.aws_rekognition import blueprint
from flask import request, json, Response
from redis import Redis
import logging, boto3
from apps import AWS_ACCESS_KEY, AWS_SECRET_KEY, STORAGE_BUCKET

@blueprint.route('/detect_label',methods=['POST'])
#Upload a new file to an existing bucket
def detect_labels(key=None, max_labels=3, min_confidence=99):
    key_md5=key or request.form.get("key_md5")
    rekognition = boto3.client("rekognition",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name='us-east-1')
    response = rekognition.detect_labels(
		Image={
			"S3Object": {
				"Bucket": STORAGE_BUCKET,
				"Name": key_md5,
			}
		},
		MaxLabels=max_labels,
		MinConfidence=min_confidence,
	)
        
    labels=[]
    categories=[]
    for label in response['Labels']:
        print(label)
        if label['Name'] not in labels:
            labels.append(label['Name'])
            for category in label['Categories']:
                if category['Name'] not in categories:
                    categories.append(category['Name'])

    return Response(json.dumps({"success": True, "labels": labels, "categories": categories, "attributes": response['Labels']}, default=str), status=200, mimetype='application/json')

@blueprint.route('/index_faces',methods=['POST'])
def index_faces(key, collection_id, attributes=()):
    key_md5=key or request.form.get("key_md5")
    rekognition = boto3.client("rekognition",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name='us-east-1')
    response = rekognition.index_faces(
		Image={
			"S3Object": {
				"Bucket": STORAGE_BUCKET,
				"Name": key_md5,
			}
		},
        CollectionId=collection_id,
        ExternalImageId=key_md5,
        DetectionAttributes=attributes,
	)
    
    return response['FaceRecords']


@blueprint.route('/search_faces',methods=['POST'])
def search_faces_by_image(key, collection_id, threshold=80, region="us-east-1"):
    key_md5=key or request.form.get("key_md5")
    rekognition = boto3.client("rekognition",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name='us-east-1')
    response = rekognition.search_faces_by_image(
		Image={
			"S3Object": {
				"Bucket": STORAGE_BUCKET,
				"Name": key_md5,
			}
		},
        CollectionId=collection_id,
        FaceMatchThreshold=threshold,
	)
    return response['FaceMatches']