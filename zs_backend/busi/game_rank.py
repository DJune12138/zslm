# -*- coding:utf-8 -*-
import operator
import time

from flask import render_template, jsonify
from flask.globals import session, request, g, current_app

from zs_backend import SqlOperate
from zs_backend.busi import busi
from zs_backend.utils.game_util import get_bank_coin, coin_translate
from zs_backend.utils import erl, time_util
from zs_backend.busi import game_parameter
from zs_backend.utils.channel_qry import LogQry
from zs_backend.utils.common import login_require
from zs_backend.utils.log_table import *


def init_status_msg(begin=True, end=True, user_type='', game='', sort='', channel=None, OThers_list=[]):
    status_msg = dict()

    if begin:
        status_msg['beginDate'] = begin
    else:
        status_msg['beginDate'] = False

    if end:
        status_msg['endDate'] = end
    else:
        status_msg['endDate'] = False

    if channel != None:
        status_msg['channel'] = int(channel)

    if user_type != '':
        status_msg['user_type'] = user_type

    if game != '':
        status_msg['game'] = game

    if sort != '':
        status_msg['sort'] = sort

    OThers = []
    for value_dict in OThers_list:
        for key, value in value_dict.items():
            if key == "user_type":
                user_type_select = u'''
                        <td colspan=1>
                            玩家类型：<select id="user_type" name="user_type">
                                    <option value="0">全部</option>
                                    <option value="1">玩家</option>
                                    <option value="2">代理</option>
                                </select>
                        </td>'''
                OThers.append(user_type_select)

            if key == 'profit_loss':
                profit_select = u'''
                        <td colspan=1>
                            排行方式：<select id="profit_loss" name="profit_loss">
                                    <option value="0">盈利排行</option>
                                    <option value="1">亏损排行</option>
                                </select>
                        </td>'''
                OThers.append(profit_select)

            if key == 'point':
                profit_select = u'''
                        <td colspan=1>
                            排行方式：<select id="point" name="point">
                                    <option value="0">买分排行</option>
                                    <option value="1">卖分排行</option>
                                </select>
                        </td>'''
                OThers.append(profit_select)

            if key == 'recharge_withdraw':
                recharge_withdraw_select = u'''
                        <td colspan=1>
                            排行方式：<select id="recharge_withdraw" name="recharge_withdraw">
                                    <option value="0">充值排行</option>
                                    <option value="1">提现排行</option>
                                </select>
                        </td>'''
                OThers.append(recharge_withdraw_select)

            if key == "game":
                line = ['<option value="0">全部</option>']
                for k, v in game_parameter.get_subgame_list().items():
                    l = '<option value="%d">%s</option>' % (k, v)
                    line.append(l)

                game_select = u'''
                        <td colspan=1>
                            游戏：<select id="game" name="game">
                                    %s
                                </select>
                        </td>''' % "\n".join(line)
                OThers.append(game_select)

    status_msg['OThers'] = OThers
    return status_msg


@busi.route('/games/rank/profit', methods=['GET'])
@login_require
def show_profit_rank():
    status_msg = init_status_msg(OThers_list=[{'game': ''}, {'profit_loss': ''}], begin=11, end=11)

    return render_template('rank_profit.html', status_msg=status_msg)


def search_profit_loss_rank_today():
    game = request.args.get('game')
    sort = request.args.get('profit_loss')
    channel_id = session['select_channel']

    today0 = time_util.today0()

    if game == '0':
        game_str = ''
    else:
        game_str = ' AND gameid=%s' % game

    sort_str = ''
    if sort == '0':
        sort_str = "DESC"
    elif sort == '1':
        sort_str = "ASC"
    search_sql = """
        SELECT * FROM 
            (SELECT pid, (SELECT nick FROM player WHERE pid=id), (SELECT last_login_ip FROM player WHERE pid=id),
                     count(1), sum(stake_coin), sum(output_coin), (sum(output_coin) - sum(stake_coin)) total_win
            FROM %s
            WHERE time>=%d 
            %s 
            GROUP BY pid 
            ORDER BY time DESC) t
        ORDER BY total_win %s 
        LIMIT 100
        """ % (get_table_log_player_subgame(today0), today0, game_str, sort_str)

    game_db_qrl = LogQry(int(channel_id))
    alltime_search_datas = game_db_qrl.qry(search_sql)

    player_rank_list = []
    i = 1  # 用于记录排名
    for pid, nick, last_login_ip, game_count, stake_coin, output_coin, total_win in alltime_search_datas:
        player_dict = dict()
        player_dict['pid'] = pid
        player_dict['nick'] = nick
        player_dict['last_login_ip'] = last_login_ip
        player_dict['game_count'] = float(game_count)
        player_dict['stake_coin'] = float(stake_coin)
        player_dict['output_coin'] = float(output_coin)
        player_dict['total_win'] = float(total_win)
        player_dict['rank'] = i
        player_rank_list.append(player_dict)
        i += 1

    return jsonify(result='ok', data=player_rank_list)


@busi.route('/search/games/rank/profit', methods=['GET'])
@login_require
def search_profit_loss_rank():
    start = request.args.get('beginDate')
    end = request.args.get('endDate')
    game = request.args.get('game')
    sort = request.args.get('profit_loss')
    channel_id = session['select_channel']

    if game == '0':
        game_str = ''
    else:
        game_str = ' AND t_player_subgame.gameid=%s' % game

    start_date = time_util.formatDatestamp(start)
    end_date = time_util.formatDatestamp(end)

    today0 = time_util.today0()
    if start_date == today0:
        return search_profit_loss_rank_today()

    if start_date > end_date:
        return jsonify(result='failed', msg=u"终止日期不能小于起始日期！")

    start_date = int(time_util.formatTimeWithDesc(start_date, "%Y%m%d"))
    end_date = int(time_util.formatTimeWithDesc(end_date + 86400, "%Y%m%d"))

    sort_str = ''
    if sort == '0':
        sort_str = "DESC"
    elif sort == '1':
        sort_str = "ASC"
    search_sql = """SELECT * FROM (SELECT pid, (SELECT nick FROM player WHERE pid=id), (SELECT last_login_ip FROM player WHERE pid=id),
                     sum(game_count), sum(stake_coin), sum(output_coin), (sum(output_coin) - sum(stake_coin)) total_win
                    FROM t_player_subgame
                    WHERE time>=%d 
                    AND time<%d%s 
                    GROUP BY pid ORDER BY time DESC) t
                    ORDER BY total_win %s LIMIT 100""" \
                 % (start_date, end_date, game_str, sort_str)

    game_db_qrl = LogQry(int(channel_id))
    alltime_search_datas = game_db_qrl.qry(search_sql)

    player_rank_list = []
    i = 1  # 用于记录排名
    for pid, nick, last_login_ip, game_count, stake_coin, output_coin, total_win in alltime_search_datas:
        player_dict = dict()
        player_dict['pid'] = pid
        player_dict['nick'] = nick
        player_dict['last_login_ip'] = last_login_ip
        player_dict['game_count'] = float(game_count)
        player_dict['stake_coin'] = float(stake_coin)
        player_dict['output_coin'] = float(output_coin)
        player_dict['total_win'] = float(total_win)
        player_dict['rank'] = i
        player_rank_list.append(player_dict)
        i += 1

    return jsonify(result='ok', data=player_rank_list)


@busi.route('/games/rank/point', methods=['GET'])
@login_require
def show_point_rank():
    status_msg = init_status_msg(OThers_list=[{'point': ''}, {'user_type': ''}], begin=11, end=11)

    return render_template('rank_sellpoint.html', status_msg=status_msg)


@busi.route('/search/games/rank/sellpoint', methods=['GET'])
@login_require
def search_sell_buy_point_rank():
    start = request.args.get('beginDate', '')
    end = request.args.get('endDate', '')
    user_type = request.args.get('user_type', '')
    sort = request.args.get('point', '')
    channel_id = session['select_channel']

    start_date = time_util.start(start)
    end_date = time_util.end(end)

    if start_date > end_date:
        return jsonify(result='failed', msg=u'终止日期不能小于起始日期！')

    # 卖分排行榜
    if sort == '1':

        if user_type == '1':
            user_type_str = " AND give_agent=0"
        elif user_type == '2':
            user_type_str = " AND give_agent=1"
        else:
            user_type_str = ""

        give_search_sql = """SELECT * FROM (SELECT give_id, sum(money) as total_money, 
                        (SELECT nick FROM player WHERE give_id=id), (SELECT last_login_ip FROM player WHERE give_id=id)
                        FROM log_bank_give 
                        WHERE time>=%d 
                        AND time<%d
                        AND ((give_agent=1 AND recv_agent=0) OR (give_agent=0 AND recv_agent=1))
                        %s
                        GROUP BY give_id) as t
                        ORDER BY t.total_money desc LIMIT 100""" \
                          % (start_date, end_date, user_type_str)

        game_db_qrl = LogQry(int(channel_id))
        bank_search_data = game_db_qrl.qry(give_search_sql)

        player_rank_list = list()
        player_dict = dict()
        gid_list = list()
        i = 1  # 排名
        for give_id, total_money, nick, last_login_ip in bank_search_data:
            gid_list.append(give_id)
            player_dict['pid'] = give_id
            player_dict['nick'] = nick
            player_dict['last_login_ip'] = last_login_ip
            player_dict['total_down_coin'] = float(total_money)
            player_dict['game_count'] = 0
            player_dict['total_up_coin'] = 0
            player_dict['rank'] = i
            player_rank_list.append(player_dict)
            player_dict = dict()
            i += 1

        if len(gid_list) == 1:
            pid_str = '(' + str(gid_list[0]) + ')'
        elif len(gid_list) == 0:
            pid_str = '(0)'
        else:
            pid_str = str(tuple(gid_list))

        recv_search_sql = """SELECT recv_id, sum(money) 
                            FROM log_bank_give
                            WHERE time>=%d 
                            AND time<%d 
                            AND recv_id IN %s 
                            GROUP BY recv_id""" \
                          % (start_date, end_date, pid_str)
        recv_player_datas = game_db_qrl.qry(recv_search_sql)

        for rid, total_money in recv_player_datas:
            for value_dict in player_rank_list:
                if value_dict['pid'] == rid:
                    value_dict['total_up_coin'] = float(total_money)

        start_ymd = int(time_util.formatTimeWithDesc(start_date, "%Y%m%d"))
        end_ymd = int(time_util.formatTimeWithDesc(end_date + 86400, "%Y%m%d"))
        game_count_sql = """SELECT pid, time, game_count
                            FROM t_player_subgame
                            WHERE time>=%d 
                            AND time<%d
                            AND pid IN %s
                            ORDER BY time desc""" \
                         % (start_ymd, end_ymd, pid_str)

        game_count_datas = game_db_qrl.qry(game_count_sql)

        game_count_dict = dict()
        for pid, time_stamp, game_count in game_count_datas:
            if not game_count_dict.has_key(pid):
                game_count_dict[pid] = game_count
            game_count_dict[pid] += game_count

        for pid, game_count in game_count_dict.items():
            for value_dict in player_rank_list:
                if value_dict['pid'] == pid:
                    value_dict['game_count'] = game_count
    # 买分排行榜
    else:
        if user_type == '1':
            user_type_str = " AND recv_agent=0"
        elif user_type == '2':
            user_type_str = " AND recv_agent=1"
        else:
            user_type_str = ""

        recv_search_sql = """SELECT * FROM (SELECT recv_id, sum(money) as total_money, 
                        (SELECT nick FROM player WHERE recv_id=id), (SELECT last_login_ip FROM player WHERE recv_id=id)
                        FROM log_bank_give 
                        WHERE time>=%d 
                        AND time<%d
                        AND ((give_agent=1 AND recv_agent=0) OR (give_agent=0 AND recv_agent=1))
                        %s
                        GROUP BY recv_id)t
                        ORDER BY t.total_money desc LIMIT 100""" \
                          % (start_date, end_date + 86400, user_type_str)

        game_db_qrl = LogQry(int(channel_id))
        bank_search_data = game_db_qrl.qry(recv_search_sql)

        player_rank_list = list()
        player_dict = dict()
        rid_list = list()
        i = 1  # 排名
        for recv_id, total_money, nick, last_login_ip in bank_search_data:
            rid_list.append(recv_id)
            player_dict['pid'] = recv_id
            player_dict['nick'] = nick
            player_dict['last_login_ip'] = last_login_ip
            player_dict['total_up_coin'] = float(total_money)
            player_dict['game_count'] = 0
            player_dict['total_down_coin'] = 0
            player_dict['rank'] = i
            player_rank_list.append(player_dict)
            player_dict = dict()
            i += 1

        if len(rid_list) == 1:
            pid_str = '(' + str(rid_list[0]) + ')'
        elif len(rid_list) == 0:
            pid_str = '(0)'
        else:
            pid_str = str(tuple(rid_list))

        give_search_sql = """SELECT give_id, sum(money) 
                            FROM log_bank_give
                            WHERE time>=%d 
                            AND time<%d
                            AND give_id IN %s 
                            GROUP BY give_id""" \
                          % (start_date, end_date, pid_str)

        recv_player_datas = game_db_qrl.qry(give_search_sql)

        for gid, total_money in recv_player_datas:
            for value_dict in player_rank_list:
                if value_dict['pid'] == gid:
                    value_dict['total_down_coin'] = float(total_money)

        start_ymd = int(time_util.formatTimeWithDesc(start_date, "%Y%m%d"))
        end_ymd = int(time_util.formatTimeWithDesc(end_date + 86400, "%Y%m%d"))
        game_count_sql = """SELECT pid, time, game_count
                            FROM t_player_subgame
                            WHERE time>=%d 
                            AND time<%d
                            AND  pid IN %s
                            ORDER BY time desc""" \
                         % (start_ymd, end_ymd, pid_str)

        game_count_datas = game_db_qrl.qry(game_count_sql)

        game_count_dict = dict()
        for pid, time_stamp, game_count in game_count_datas:
            if not game_count_dict.has_key(pid):
                game_count_dict[pid] = game_count
            game_count_dict[pid] += game_count

        for pid, game_count in game_count_dict.items():
            for value_dict in player_rank_list:
                if value_dict['pid'] == pid:
                    value_dict['game_count'] = game_count

    return jsonify(result=0, data=player_rank_list)


@busi.route('/games/rank/withdraw', methods=['GET'])
@login_require
def show_withdraw_rank():
    status_msg = init_status_msg(OThers_list=[{'recharge_withdraw': ''}, {'user_type': ''}], begin=11, end=11)

    return render_template('rank_withdraw.html', status_msg=status_msg)


@busi.route('/search/games/rank/withdraw', methods=['GET'])
@login_require
def search_withdraw_topup_rank():
    start = request.args.get('beginDate')
    end = request.args.get('endDate')
    sort = request.args.get('recharge_withdraw')
    channel_id = session['select_channel']

    start_date = time_util.start(start)
    end_date = time_util.end(end)

    if start_date > end_date:
        return jsonify(result='failed', msg=u'终止日期不能小于起始日期！')

    if sort == '0':
        sort_str = 'total_withdraw'
    else:
        sort_str = 'total_recharge'

    search_sql = """SELECT * FROM (SELECT pid, (SELECT nick FROM player WHERE pid=id), (SELECT last_login_ip FROM player WHERE pid=id),
                    sum(coin) as total_withdraw, sum(cost) as total_recharge
                    FROM admin_recharge
                    WHERE time>=%d 
                    AND time<%d 
                    GROUP BY pid)t 
                    ORDER BY t.%s desc LIMIT 100""" \
                 % (start_date, end_date, sort_str)

    game_db_qrl = LogQry(int(channel_id))
    give_search_sql = game_db_qrl.qry(search_sql)

    player_rank_list = list()
    pid_list = list()
    i = 1  # 排名
    for pid, nick, last_login_ip, total_withdraw, total_recharge in give_search_sql:
        pid_list.append(pid)
        player_dict = dict()
        player_dict['pid'] = pid
        player_dict['nick'] = nick
        player_dict['last_login_ip'] = last_login_ip
        player_dict['game_count'] = 0
        player_dict['withdraw'] = float(total_withdraw)
        player_dict['recharge'] = float(total_recharge)
        player_dict['rank'] = i
        player_rank_list.append(player_dict)
        i += 1

    if len(pid_list) == 1:
        pid_str = '(' + str(pid_list[0]) + ')'
    elif len(pid_list) == 0:
        pid_str = '(0)'
    else:
        pid_str = str(tuple(pid_list))

    start_ymd = int(time_util.formatTimeWithDesc(start_date, "%Y%m%d"))
    end_ymd = int(time_util.formatTimeWithDesc(end_date + 86400, "%Y%m%d"))
    game_count_sql = """SELECT pid, time, game_count
                        FROM t_player_subgame
                        WHERE time>=%d 
                        AND time<%d
                        AND pid IN %s
                        ORDER BY time desc""" \
                     % (start_ymd, end_ymd, pid_str)

    game_count_datas = game_db_qrl.qry(game_count_sql)

    game_count_dict = dict()
    for pid, time_stamp, game_count in game_count_datas:
        if not game_count_dict.has_key(pid):
            game_count_dict[pid] = game_count
        game_count_dict[pid] += game_count

    for pid, game_count in game_count_dict.items():
        for value_dict in player_rank_list:
            if value_dict['pid'] == pid:
                value_dict['game_count'] = game_count

    return jsonify(result='ok', data=player_rank_list)


@busi.route('/games/rank/gold', methods=['GET'])
@login_require
def show_gold_rank():
    status_msg = init_status_msg(begin=False, end=False, OThers_list=[{'user_type': ''}])

    return render_template('rank_gold.html', status_msg=status_msg)


@busi.route('/searcj/games/rank/gold', methods=['GET'])
@login_require
def search_gold_rank():
    user_type = request.args.get('user_type')
    channel_id = session['select_channel']

    backend_agent_sql = "SELECT pid FROM admin_agent_list"
    agent_tup = LogQry(channel_id).qry(backend_agent_sql)

    agent_id_list = list()
    for agent_id in agent_tup:
        agent_id_list.append(agent_id[0])

    if user_type == '0':
        user_type_str = "1=1"
    elif user_type == '1':
        if len(agent_id_list) == 0:
            user_type_str = '1=1'
        else:
            user_type_str = 'id NOT IN %s' % str(tuple(agent_id_list))
    else:
        if len(agent_id_list) == 0:
            user_type_str = '1=0'
        else:
            user_type_str = 'id IN %s' % str(tuple(agent_id_list))

    search_sql = """SELECT id, nick, total_recharge_rmb, total_withdraw, coin, counter, last_login_ip, delivery_address 
                    FROM player 
                    WHERE %s
                    ORDER BY coin DESC LIMIT 100;""" % user_type_str

    game_db_qrl = LogQry(channel_id)

    coin_rank_datas = game_db_qrl.qry(search_sql)

    player_rank_list = list()
    pid_list = list()
    player_dict = dict()
    i = 1  # 排名
    for pid, nick, total_recharge, total_withdraw, coin, counter, last_login_ip, delivery_address in coin_rank_datas:
        pid_list.append(pid)
        player_dict['pid'] = pid
        player_dict['nick'] = nick
        player_dict['total_recharge'] = total_recharge
        player_dict['total_withdraw'] = total_withdraw
        player_dict['coin'] = coin
        player_dict['last_login_ip'] = last_login_ip
        player_dict['counter'] = get_bank_coin(counter)
        player_dict['game_count'] = 0
        player_dict['rank'] = i
        player_rank_list.append(player_dict)
        player_dict = dict()
        i += 1

    if len(pid_list) == 1:
        pid_str = '(' + str(pid_list[0]) + ')'
    elif len(pid_list) == 0:
        pid_str = '(0)'
    else:
        pid_str = str(tuple(pid_list))

    game_count_sql = """SELECT pid, time, game_count
                        FROM t_player_subgame
                        WHERE pid IN %s
                        ORDER BY time desc""" \
                     % pid_str

    game_count_datas = game_db_qrl.qry(game_count_sql)

    game_count_dict = dict()
    for pid, time_stamp, game_count in game_count_datas:
        if not game_count_dict.has_key(pid):
            game_count_dict[pid] = game_count
        game_count_dict[pid] += game_count

    for pid, game_count in game_count_dict.items():
        for value_dict in player_rank_list:
            if value_dict['pid'] == pid:
                value_dict['game_count'] = game_count

    return jsonify(result='ok', data=player_rank_list)


@busi.route('/games/rank/profit/json', methods=['GET'])
@login_require
def games_rank_profit_json():
    """返回盈利亏损json数据"""

    # 获取参数
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    channel_id = session['select_channel']

    # 处理参数
    start_time2 = time_util.formatDatestamp(start_time)
    end_time2 = time_util.formatDatestamp(end_time) + 86400
    start_time = start_time.replace('-', '')
    end_time = end_time.replace('-', '')
    channel_id = int(channel_id)

    # 获取数据
    if start_time2 == time_util.today0():
        retrieve_sql = '''
            SELECT (SELECT nick FROM player WHERE pid=id),sum(stake_coin),(sum(output_coin)-sum(stake_coin)),pid
            FROM %s
            WHERE time>=%s
            GROUP BY pid
            ORDER BY (sum(output_coin)-sum(stake_coin)) DESC
            LIMIT 100;
        ''' % (get_table_log_player_subgame(time_util.now_sec()), time_util.today0())
    else:
        retrieve_sql = """SELECT (SELECT nick FROM player WHERE pid=id),sum(stake_coin),(sum(output_coin)-sum(stake_coin)),pid
                          FROM t_player_subgame
                          WHERE time>=%s
                          AND time<=%s
                          GROUP BY pid
                          ORDER BY (sum(output_coin)-sum(stake_coin)) DESC
                          LIMIT 100;""" \
                       % (start_time, end_time)

    data = LogQry(int(channel_id)).qry(retrieve_sql)
    # 处理数据
    data_list = list()
    for nick, stake_coin, total_win, pid in data:
        data_dict = dict()
        data_dict['nick'] = nick
        data_dict['stake_coin'] = int(stake_coin)
        data_dict['total_win'] = int(total_win)
        data_dict['pid'] = pid
        data_list.append(data_dict)

    # 返回数据
    return jsonify(data=data_list)
