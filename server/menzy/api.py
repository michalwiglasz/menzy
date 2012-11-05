# -*- coding: utf-8 -*-

from scrapper import get_cantine_list, get_cantine_menu

from flask import Blueprint
import simplejson
from functools import partial
import time


api = Blueprint('api', __name__)


cache = {}
cantine_list_expires = 86400  # 1 day
cantine_menu_expires = 60     # 1 minute


def json_response(resp, status=None, headers=None):
    headers = headers or {}
    headers['content-type'] = 'application/json; charset=utf-8'
    return simplejson.dumps(resp, indent=4), status, headers


def cached_json_response(key, expires, func, status=None, headers=None):
    resp = get_cached(key, expires, func)
    return json_response(resp, status, headers)


def get_cached(key, expires, func):
    now = time.time()

    if key in cache:
        inserted, resp = cache[key]
        if time.time() - inserted <= expires:
            return resp

    resp = func()
    cache[key] = now, resp
    return resp


@api.route("/")
def homepage():
    return json_response({
        'app': 'Menzy',
        'version': 1,
        'author': 'Michal Wiglasz, michalwiglasz.cz',
        'help': ('Try /list.json to fetch list of cantines, or /menu/<id>.json'
                 ' to fetch current menu for specified cantine.')
    })


@api.route("/list.json")
def list():
    return cached_json_response('cantine_list', cantine_list_expires,
                                get_cantine_list)


@api.route("/menu/<int:cantine_id>.json")
def menu(cantine_id):
    cantine_list = get_cached('cantine_list', cantine_list_expires,
                              get_cantine_list)
    url = cantine_list[cantine_id]['menu_url']
    key = 'menu_' + str(cantine_id)
    return cached_json_response(key, cantine_menu_expires,
                      partial(get_cantine_menu, url))
