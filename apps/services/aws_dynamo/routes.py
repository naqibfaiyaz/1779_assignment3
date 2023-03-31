# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.services.aws_dynamo import blueprint
from flask import request, json, Response
from redis import Redis
import logging, boto3, hashlib
from apps import AWS_ACCESS_KEY, AWS_SECRET_KEY, STORAGE_URL

@blueprint.route('/insert',methods=['POST'])
#Upload a new file to an existing bucket
def insert_key(key=None, value=None):
    # device_table = create_devices_table
    # print("Status:", device_table)
    keyName = key or request.form.get('key')
    val = value or request.form.get('value')
    
    print(keyName, val)
    
    dynamodb = boto3.resource('dynamodb',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name='us-east-1')
    
    table = dynamodb.Table('key_img')
    print(table)
    item = { 
            'key_md5': hashlib.md5(keyName.encode()).hexdigest(),
            'key': keyName,
            'img_url': val
        }
    response = table.put_item(
        Item = item
    )

    # table.get_item(
    #         Key={'key_name': keyName, 'datacount': datacount})

    print(response)
    return Response(json.dumps({"success": response, "data":item}, default=str), status=200, mimetype='application/json')


@blueprint.route('/update',methods=['PATCH'])
#Upload a new file to an existing bucket
def update_key(key=None, value=None, attributes=None, labels=None, categories=None):
    # device_table = create_devices_table
    # print("Status:", device_table)
    keyName = key or request.form.get('key')
    val = value or request.form.get('value')
    attr = attributes or request.form.get('attributes')
    lbls = labels or request.form.get('labels')
    cat = categories or request.form.get('categories')
    
    print(keyName, val)
    
    dynamodb = boto3.resource('dynamodb',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name='us-east-1')
    
    table = dynamodb.Table('key_img')

    key = { 
            'key_md5': hashlib.md5(keyName.encode()).hexdigest(),
            'key': keyName
    }
    response = table.update_item(
        Key = key,
        ExpressionAttributeNames={
            "#img_url": "img_url",
            "#attributes": "attributes",
            "#categories": "categories",
            "#labels": "labels",
            },
        ExpressionAttributeValues={
            ':img': val,
            ':attr': attr,
            ':cat': cat,
            ':lbls': lbls
            
        },
        UpdateExpression="SET #img_url = :img, #attributes = :attr, #labels = :lbls, #categories = :cat",
    )

    return Response(json.dumps({"success": response, "data":{"key": key, "new_value": val}}, default=str), status=200, mimetype='application/json')

@blueprint.route('/delete',methods=['DELETE'])
#Upload a new file to an existing bucket
def delete_key(key=None):
    # device_table = create_devices_table
    # print("Status:", device_table)
    keyName = key or request.form.get('key')
    
    dynamodb = boto3.resource('dynamodb',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name='us-east-1')
    
    table = dynamodb.Table('key_img')
    
    key = { 
            'key_md5': hashlib.md5(keyName.encode()).hexdigest(),
            'key': keyName
    }
    response = table.delete_item(
        Key = key
    )
    
    return Response(json.dumps({"success": response, "data":{"key": key}, "msg": "Key deleted Successfully"}, default=str), status=200, mimetype='application/json')


@blueprint.route('/get',methods=['GET', 'POST'])
#Upload a new file to an existing bucket
def get_key(key=None):
    # device_table = create_devices_table
    # print("Status:", device_table)
    keyName = key or request.form.get('key')
    
    print(keyName)
    
    dynamodb = boto3.resource('dynamodb',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name='us-east-1')
    
    table = dynamodb.Table('key_img')
    
    key = { 
            'key_md5': hashlib.md5(keyName.encode()).hexdigest(),
            'key': keyName
    }
    response = table.get_item(
        Key = key
    )

    if 'Item' in response:
        data=response['Item']
        success=True
        msg= keyName + " found"
    else: 
        data={}
        success=False
        msg= keyName + " does not exists"

    
    return Response(json.dumps({"success": success, "content":data, "msg": msg}, default=str), status=200, mimetype='application/json')


@blueprint.route('/get_all_from_db',methods=['GET', 'POST'])
#Upload a new file to an existing bucket
def get_keys_from_db():
    dynamodb = boto3.resource('dynamodb',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name='us-east-1')
    
    table = dynamodb.Table('key_img')
    
    response = table.scan()
    items = response['Items']
    allDBitems={'content':{},'keys':[], 'success': None}
    for item in items:
        item['img_url']=STORAGE_URL+item['img_url']
        allDBitems['content'][item['key']]=item
            # allCache.append({"content":})
        allDBitems['keys']=list(allDBitems['content'].keys())
        allDBitems['success']='true'

    if len(allDBitems)==0:
        success=True 
        msg="No items in the Table"
    else:
        success=True 
        msg="All items are fetched"

    
    return Response(json.dumps(allDBitems, default=str), status=200, mimetype='application/json')


@blueprint.route('/query',methods=['GET', 'POST'])
#Upload a new file to an existing bucket
def get_data_from_md5(param=None, value=None):
    # device_table = create_devices_table
    # print("Status:", device_table)
    parm = param or request.form.get('param')
    val = value or request.form.get('value')
    
    print(parm, val)
    
    dynamodb = boto3.resource('dynamodb',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name='us-east-1')
    
    table = dynamodb.Table('key_img')
    
    response = table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key(parm).eq(val))

    print(response)
    if 'Items' in response:
        data=response['Items'][0]
        print(data)
        success=True
        msg= data['key'] + " found"
    else: 
        data={}
        success=False
        msg= param + '=' + val + " does not exists"

    
    return Response(json.dumps({"success": success, "content":data, "msg": msg}, default=str), status=200, mimetype='application/json')

@blueprint.route('/get_label_wise_img',methods=['GET', 'POST'])
#Upload a new file to an existing bucket
def label_wise_data():
    # device_table = create_devices_table
    # print("Status:", device_table)
    all_data=json.loads(get_keys_from_db().data)['content']
    # print(all_data)
    label_list={}
    for key_data in all_data:
        for label in all_data[key_data]['labels']:
            if label not in label_list:
                print(label)
                print(all_data[key_data]['img_url'])
                label_list[label]=[]
                label_list[label].append(all_data[key_data]['img_url'])
            else:
                label_list[label].append(all_data[key_data]['img_url'])

    # print(label_list)

    
    return Response(json.dumps({"success": True, "label_data": label_list, "label_list": list(label_list.keys()), "msg": "Successfully fetched all labels"}, default=str), status=200, mimetype='application/json')



@blueprint.route('/get_category_wise_img',methods=['GET', 'POST'])
#Upload a new file to an existing bucket
def category_wise_data():
    # device_table = create_devices_table
    # print("Status:", device_table)
    all_data=json.loads(get_keys_from_db().data)['content']
    # print(all_data)
    category_list={}
    for key_data in all_data:
        for category in all_data[key_data]['categories']:
            if category not in category_list:
                print(category)
                print(all_data[key_data]['img_url'])
                category_list[category]=[]
                category_list[category].append(all_data[key_data]['img_url'])
            else:
                category_list[category].append(all_data[key_data]['img_url'])

    # print(label_list)

    
    return Response(json.dumps({"success": True, "label_data": category_list, "label_list": list(category_list.keys()), "msg": "Successfully fetched all categories"}, default=str), status=200, mimetype='application/json')