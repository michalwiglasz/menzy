# -*- coding: utf-8 -*-

from scrapper import get_cantine_list

from flask import Blueprint
import simplejson

import time

api = Blueprint('api', __name__)

cache = {}

def json_response(resp, status=None, headers=None):
    headers = headers or {}
    headers['content-type'] = 'application/json; charset=utf-8'
    return simplejson.dumps(resp), status, headers


def cached_json_response(key, expires, func, status=None, headers=None,
                  cache_key=None, cache_expires=None):
    now = time.time()
    headers = headers or {}
    headers['content-type'] = 'application/json; charset=utf-8'

    if key in cache:
        inserted, resp = cache[key]
        if now - inserted <= expires:
            return simplejson.dumps(resp), status, headers

    resp = func()
    cache[key] = now, resp
    return simplejson.dumps(resp), status, headers


@api.route("/")
def homepage():
    return json_response({
        'app': 'Menzy',
        'version': 1,
        'author': 'Michal Wiglasz, michalwiglasz.cz',
    })


@api.route("/list.json")
def list():
    return cached_json_response('cantine_list', 86400, get_cantine_list)
