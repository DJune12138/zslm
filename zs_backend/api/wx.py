# -*- coding:utf-8 -*-
from flask import redirect
from flask import render_template, jsonify
from flask import url_for
from flask.globals import current_app, request, g
from zs_backend.sql import SqlOperate
from zs_backend.utils.common import login_require, md5
from zs_backend.utils.const import *
from zs_backend.utils import httpc_util
import time
from zs_backend import redis_conn

GET_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
REFRESH_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/refresh_token"
GET_USER_URL = "https://api.weixin.qq.com/sns/userinfo"
SHARE_URL = "https://api.weixin.qq.com/cgi-bin/token"

def get_wx_key(AppID):
	return redis_conn.hget(WX_CONFIG_TABLE, AppID)

def get_wx_app_list(Channel):
	return [redis_conn.hget(CHANNEL_CONFIG_TABLE+Channel, "wx_appid")]

def get_wx_h5_list(Channel):
	return [redis_conn.hget(CHANNEL_CONFIG_TABLE+Channel, "h5_wx_appid")]

@httpc_util.check_param(ctype="c2s", debug=True)
def wx_userinfo():
	json_dict = request.args
	OpenID = json_dict.get('openid')
	Token = json_dict.get('access_token')

	param = {"access_token":Token, "openid":OpenID}

	r = httpc_util.get(GET_USER_URL, param)
	Result = r.json()
	if Result.has_key("errcode") and int(Result["errcode"]) > 0:
		return jsonify(errcode = Result["errcode"])
	Result["timestamp"] = int(time.time())
	Result["token"] = md5(str(Result["unionid"]) + str(Result["timestamp"]) + SECRET_KEY)
	print Result["unionid"], Result["timestamp"], Result["token"]
	return jsonify(Result)

@httpc_util.check_param(ctype="c2s", debug=True)
def wx_access():
	json_dict = request.args
	AppID = json_dict.get('appid')
	Code = json_dict.get('code')

	WXKey = get_wx_key(AppID)
	if WXKey:
		param = {"appid":AppID, "secret":WXKey, "code":Code, "grant_type":"authorization_code"}

		r = httpc_util.get(GET_TOKEN_URL, param)
		return jsonify(r.json())
	else:
		return jsonify(errmsg='appid err')

@httpc_util.check_param(ctype="c2s", debug=True)
def wx_refresh():
	json_dict = request.args
	AppID = json_dict.get('appid')
	Token = json_dict.get('refresh_token')

	WXKey = get_wx_key(AppID)
	if WXKey:
		param = {"appid":AppID, "grant_type":"refresh_token", "refresh_token":Token}

		r = httpc_util.get(REFRESH_TOKEN_URL, param)
		return jsonify(r.json())
	else:
		return jsonify(errmsg='appid err')

def wx_share_access_token():
	json_dict = request.args
	AppID = json_dict.get('appid')
	WXKey = get_wx_key(AppID)

	WXKey = get_wx_key(AppID)
	if WXKey:
		param = {"appid":AppID, "grant_type":"client_credential", "secret":WXKey}

		r = httpc_util.get(SHARE_URL, param)
		return jsonify(r.json())
	else:
		return jsonify(errmsg='appid err')


