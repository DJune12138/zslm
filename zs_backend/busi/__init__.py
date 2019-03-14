# -*- coding:utf-8 -*-
# 使用蓝图按照接口版本划分模块


from flask import Blueprint

# 创建版本1.0的蓝图 http://www.example.com/api/1.0/info
busi = Blueprint('busi', __name__)

from . import index, admin_user, channel, menu, auth, game_data, game_user, game_rank, \
    game_transaction, game_maniplate, presented_config, agent_distribution_config, \
    single_player_ctl, agent, game_opt_log, black_white_list, gm, game_data_compare, user_lucky, h5, \
    gm_manage, transfer_coin, player_add_subtract_money, member_level, game_platform, wx_agent, \
    pay_channel, recharge, card_data, withdrawal_order, game_detail, operat_state, recharge_discounts, \
    agent_list, agent_level, system_parameter, agent_add, agent_commission, \
    distribution_commission, player_game_detail, game_parameter, game_alarm
