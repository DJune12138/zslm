# -*- coding:utf-8 -*-

from flask import render_template, jsonify
from flask.globals import session, request, g, current_app
from zs_backend.busi import busi
from zs_backend.utils.channel_qry import GameWeb, LogQry
from zs_backend.utils.common import login_require
from zs_backend.utils import time_util
from zs_backend.utils import game_util
from zs_backend import SqlOperate
import json


def otherQry(pid='', phone=''):
    phoneHtml = u'''
		<td>
			靓号：<input type="text" id="pid" name="pid" value="%s">
			手机号：<input type="text" id="phone" name="phone" value="%s"> 
			<input type="button" onclick="add_lucky_id()" value="增加靓号">
        </td>
	''' % (pid, phone)

    return [phoneHtml]


@busi.route('/users/lucky/', methods=['GET'])
@login_require
def luck_page_init():
    page = dict()
    page["otherQry"] = otherQry()

    return render_template('user_luckyid.html', page=page)


def do_qry(channel):
    sql = '''
			select id, nick, phone
			from player
			where id > 90000 and id < 100000
		'''

    return LogQry(channel).qry(sql)


@busi.route('/users/lucky/qry', methods=['GET'])
@login_require
def luck_qry():
    channel = session['select_channel']

    data = do_qry(channel)

    data_list = list()
    for primary_id, nick, phone in data:
        data_dict = dict()
        data_dict['id'] = primary_id
        data_dict['nick'] = nick
        data_dict['phone'] = phone
        data_list.append(data_dict)

    return jsonify(result='ok', data=data_list)


@busi.route('/users/luck/add', methods=['GET'])
@login_require
def add_lucy():
    pid = int(request.args.get('PlayerID'))
    channel = session['select_channel']
    phone = int(request.args.get('phone'))

    payload = {"luck": pid, "phone": phone}
    Result = GameWeb(channel).post("/api/create_luck", payload)['result']
    if Result == "succ":
        return jsonify({"result": "ok"})
    else:
        return jsonify({"result": "fail"})