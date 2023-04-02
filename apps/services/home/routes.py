# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.services.home import blueprint
from flask import render_template, request, json, redirect, url_for
# from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.services.nodePartitions.models import nodePartitions, memcacheNodes
from apps.services.memcacheManager.routes import changePolicyInDB
import boto3
from apps import AWS_ACCESS_KEY, AWS_SECRET_KEY, db, app_manager_fe


@blueprint.route('/')
# @login_required
def RedirectIndex():
    return index()

@blueprint.route('/index')
# @login_required
def index():
    return redirect(url_for("photoUpload_blueprint.route_template", template="photos.html"), code=302)

@blueprint.route('/<template>')
# @login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("photoUpload/" + template, segment=segment.replace('.html', ''))

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
