function getLocalTime(nS) {
    if (nS == 0) {
        return ""
    }

    var date = new Date(nS * 1000);//时间戳为10位需*1000，时间戳为13位的话不需乘1000
    Y = date.getFullYear() + '-';
    M = (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1) + '-';
    D = (date.getDate() < 10 ? '0' + (date.getDate()) : date.getDate()) + ' ';
    h = (date.getHours() < 10 ? '0' + (date.getHours()) : date.getHours()) + ':';
    m = (date.getMinutes() < 10 ? '0' + (date.getMinutes()) : date.getMinutes()) + ':';
    s = (date.getSeconds() < 10 ? '0' + (date.getSeconds()) : date.getSeconds());

    return Y + M + D + h + m + s;
}

function getNowFormatDate() {
    var date = new Date();
    var seperator1 = "-";
    var year = date.getFullYear();
    var month = date.getMonth() + 1;
    var strDate = date.getDate();
    if (month >= 1 && month <= 9) {
        month = "0" + month;
    }
    if (strDate >= 0 && strDate <= 9) {
        strDate = "0" + strDate;
    }
    var currentdate = year + seperator1 + month + seperator1 + strDate;
    return currentdate;
}

function click_qry_btn_today() {
    var date = getNowFormatDate();
    if (document.getElementById("beginDate")) {
        document.getElementById("beginDate").value = date
    }

    if (document.getElementById("endDate")) {
        document.getElementById("endDate").value = date
    }

    document.getElementById("query_form").submit();
}

function coin_format(Coin) {
    var coin_rate = localStorage.getItem("coin_rate") || 1;
    if (coin_rate != 1) {
        // 向下取整, 保留两位小数
        Coin = Math.floor(Number(Coin) * 100 / coin_rate) / 100;
    }
    if (Coin > 0) {
        return '<span style="color: #F5222D ;font-weight: 600">+' + Coin + '</span>';
    }
    return '<span style="color: #64db63;font-weight: 600">' + Coin + '</span>';
}

function coin_format_no_color(Coin) {
    var coin_rate = localStorage.getItem("coin_rate") || 1;
    if (coin_rate != 1) {
        // 向下取整, 保留两位小数
        Coin = Math.floor((Number(Coin) * 100) / coin_rate) / 100;
    }
    return Coin;
}

function coin_format_back(Coin) {
    var coin_rate = localStorage.getItem("coin_rate") || 1;
    if (coin_rate != 1) {
        Coin = Number(Coin) * coin_rate;
    }
    return Math.round(Coin)
}

// 玩家id,跳转到玩家详情
function pid_format(pid) {
    var input_pid = $('#PlayerID').val()
    if (input_pid == pid) {
        return '<a style="color: red !important;" onclick="new_iframe(\'玩家信息详情\',\'/games/users/datas/details?pid=' + pid + '\')">' + pid + '</a>'
    }
    else {
        return '<a onclick="new_iframe(\'玩家信息详情\',\'/games/users/datas/details?pid=' + pid + '\')">' + pid + '</a>'
    }
}

//操作按钮,跳转到玩家详情
function goUserDetail(value, item) {
    return '<a onClick="new_iframe(\'玩家信息详情\',\'/games/users/datas/details?pid=' + item.pid + '\')">查看详情</a>'
}

function subgame_format(name) {
    if (name == "在线") {
        return name
    }
    return '<font color="blue">' + name + '</font>'
}

// 获取bootstrap-table表格中checked的id
function get_checked(TableID, IDCol) {
    var tb = document.getElementById(TableID);    // table 的 id
    var rows = tb.rows;                           // 获取表格所有行

    var check_str = "";
    var checklist = document.getElementsByName('btSelectItem');
    for (var i = 0; i < checklist.length; i++) {
        if (checklist[i].checked) {
            var pid = rows[i + 1].cells[IDCol].innerText;
            check_str = check_str + pid + ",";
        }
    }

    return check_str;
}

// loading加载图
function loadingShow(isTrue) {
    if (isTrue) {
        $('body').append('<section class="loading"><img src="/static/images/loading.gif"/> </section>');
        setTimeout(function () {
            $('.loading').remove();
        }, 30000)
    } else {
        $('.loading').remove();
    }
}

//合计
function get_total(items) {
    var count = 0;
    for (var i in items) {
        count += parseInt(items[i][this.field]);
    }
    return String(count);
}

//合计,加渠道过滤
function get_total_coin_rate(items) {
    coin_rate = localStorage.getItem("coin_rate") || 1;
    var count = 0;
    for (var i in items) {
        count += parseInt(items[i][this.field]);
    }
    return String(count / coin_rate);
}

//弹窗提示信息
function showAlert(text, type) {
    $alert = $('.refactor-alert');
    $content = $alert.find('.refactor-alert-content');

    $content.css('background', '#ec971f').text(text);
    $alert.fadeIn();
    if (type == 'success') {
        $content.css('background', '#286090');
    }
    setTimeout(function () {
        $alert.fadeOut();
    }, 2000)
}

//删除二次确定
function showDelete(fn) {
    $confirm = $('.refactor-confirm');
    $confirm.fadeIn();
    $confirm.find('.cancel').click(function () {
        $confirm.fadeOut();
    });
    $confirm.find('.del').click(function () {
        $confirm.fadeOut();
        fn();
    })
}

// ajax接口回调
function ajaxCallback(res, success, noAlert) {
    loadingShow(false);
    if (res.error == 'system_err') {
        showAlert('服务器忙，请稍后再试');
        return;
    }
    if (res.result == 1 || res.result == 'ok') {
        if (success) {
            success(res);
        }
        if (!noAlert) {
            showAlert(res.msg, 'success');
        }
    } else {
        showAlert(res.msg);
    }
}

// 设置cookie
function setCookie(c_name, value, expiredays) {
    var exdate = new Date()
    var exdate = new Date()
    exdate.setDate(exdate.getDate() + expiredays)
    document.cookie = c_name + "=" + escape(value) + ((expiredays == null) ? "" : ";expires=" + exdate.toGMTString())
}

// 获取cookie
function getCookie(name) {
    var arr, reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");
    if (arr = document.cookie.match(reg))
        return unescape(arr[2]);
    else
        return null;
}

// 删除cookie
function delCookie(name) {
    var exp = new Date();
    exp.setTime(exp.getTime() - 1);
    var cval = getCookie(name);
    if (cval != null)
        document.cookie = name + "=" + cval + ";expires=" + exp.toGMTString();
}

//浮点数,乘法
function floatNumMul(a, b) {
    var c = 0,
        d = a.toString(),
        e = b.toString();
    try {
        c += d.split(".")[1].length;
    } catch (f) {
    }
    try {
        c += e.split(".")[1].length;
    } catch (f) {
    }
    return Number(d.replace(".", "")) * Number(e.replace(".", "")) / Math.pow(10, c);
}

//浮点数,除法
function floatNumDiv(a, b) {
    var c, d, e = 0,
        f = 0;
    try {
        e = a.toString().split(".")[1].length;
    } catch (g) {
    }
    try {
        f = b.toString().split(".")[1].length;
    } catch (g) {
    }
    return c = Number(a.toString().replace(".", "")), d = Number(b.toString().replace(".", "")), mul(c / d, Math.pow(10, f - e));
}

//日期快速查询
function date_fast(type) {
    var obj = {};
    var newTime;//现在时间
    var today;//今天开始时间
    var week;//星期几
    var month;//本月开始时间
    var last_month;//上月开始时间
    newTime = new Date().getTime() / 1000;
    today = new Date(new Date().setHours(0, 0, 0, 0)).getTime() / 1000;
    month = new Date(new Date(new Date().setDate(1)).setHours(0, 0, 0, 0)).getTime() / 1000;
    week = new Date().getDay();
    week = (week == 0) ? 7 : week;

    if (new Date().getMonth() == 0) {
        last_month = new Date(new Date(new Date().setFullYear(new Date().getFullYear() - 1, 11, 1)).setHours(0, 0, 0, 0)).getTime() / 1000;
    } else {
        last_month = new Date(new Date(new Date().setMonth(new Date().getMonth() - 1, 1)).setHours(0, 0, 0, 0)).getTime() / 1000;
    }
    switch (type) {
        case 'today':
            obj.start = getLocalTime(today);
            obj.end = getLocalTime(newTime);
            return obj;
            break
        case 'yesterday':
            obj.start = getLocalTime(today - 24 * 3600);
            obj.end = getLocalTime(today - 1);
            return obj;
            break
        case 'week':
            obj.start = getLocalTime(today - 24 * 3600 * (week - 1));
            obj.end = getLocalTime(newTime);
            return obj;
            break
        case 'last_week':
            obj.start = getLocalTime(today - 24 * 3600 * (week - 1 + 7));
            obj.end = getLocalTime(today - 24 * 3600 * (week - 1) - 1);
            return obj;
            break
        case 'month':
            obj.start = getLocalTime(month);
            obj.end = getLocalTime(newTime);
            return obj;
            break
        case 'last_month':
            obj.start = getLocalTime(last_month);
            obj.end = getLocalTime(month - 1);
            return obj;
            break
        case 'one_week':
            obj.start = getLocalTime(newTime - 6 * 24 * 3600);
            obj.end = getLocalTime(newTime);
            return obj;
            break
        case 'one_min':
            obj.start = getLocalTime(newTime - 60);
            obj.end = getLocalTime(newTime);
            return obj;
            break
    }
}

//照片上传
function imgUpload($this, input, output) {
    var dic = new FormData();
    dic.append('qr_code', document.getElementById(input).files[0]);
    $.ajax({
        url: '/pay_channel/qr_code/save',
        type: 'POST',
        data: dic,
        processData: false,
        contentType: false,
        dataType: 'JSON',
        success: function (items) {
            if (items.result == '1') {
                $(output).val(items.file_name);
                showAlert('上传成功', 'success');
            } else {
                showAlert(items.msg)
            }
        }
    })
}

//获取url传参
function getUrlParams() {
    var obj = {};
    var url = window.location.href.split('?');
    if (url.length == 1) {
        return obj;
    } else {
        $.each(url[1].split('&'), function (index, item) {
            $.each(item.split('='), function () {
                obj[item.split('=')[0]] = item.split('=')[1];
            })
        })
        return obj;
    }
}

//打开子页面
function new_iframe(title, src) {
    var list_ = window.parent.document.getElementById("list_");
    var content = window.parent.document.getElementById("content");
    if ($(list_).find('.list_ul_ li').length == 15) {
        parent.window.showAlert('最多打开15个页签');
        return
    }
    var isNew = true;
    if (isNew) {
        $(list_).find('.list_ul_ li').removeClass('select_child')
        $(list_).find('.list_ul_').append('<li class="select_child" key="' + src + '"><a>' + title + '</a><span>×</span></li>');

        $(content).find('iframe').hide();
        $(content).append('<iframe src="' + src + '" name="main" class="iframe" marginwidth="0" marginheight="0"\n' +
            '            frameborder="0" scrolling="auto" target="_self" width="100%" height="100%"></iframe>');

        $(list_).find('.list_ul_ li').click(function () {
            $(list_).find('.list_ul_ li').removeClass('select_child');
            $(this).addClass('select_child');
            var self_ = this;

            $(content).find('iframe').hide();
            $(content).find('iframe').each(function (index, item) {
                if ($(self_).attr('key') == $(item).attr('src')) {
                    $(item).show()
                }
            })
        })

        $(list_).find('.list_ul_ li span').click(function () {
            var isTrue = $(this).parent('li').hasClass('select_child');
            var index = $(list_).find('.list_ul_ li span').index(this);
            $(this).parent('li').remove();
            if (isTrue) {
                $(list_).find('.list_ul_ li').removeClass('select_child');
                if (index == 0) {
                    $(list_).find('.list_ul_').find('li').eq(0).addClass('select_child');
                } else {
                    $(list_).find('.list_ul_').find('li').eq(index - 1).addClass('select_child');
                }
                $(list_).find('.list_ul_').find('li.select_child').click();
            }
            if ($(list_).find('.list_ul_ li').length == 0) {
                $(content).find('iframe').hide();
            }
        })
        $(content).find('iframe').height(parent.window.iframe_height);
    }
}

//ajax接口参数
function queryParams() {
    var obj = {};
    $.each(arguments, function (index, item) {
        obj[item] = $('#' + item).val()
    })
    return obj;
}

$(function () {
    //开关按钮
    $('.switch_button').click(function () {
        if ($(this).siblings('select').val() == '-1') {//兼容游戏平台管理页面
            return;
        }
        if ($(this).attr('value') == '1') {
            $(this).attr('value', '0');
        } else if ($(this).attr('value') == '0') {
            $(this).attr('value', '1');
        }
    })

    //日期快速查询
    nav_li = $('ul.date_fast li');
    nav_li.click(function () {
        localStorage.setItem('update_url', false);
        nav_li.removeClass('active');
        $(this).addClass('active');
        time = $(this).attr('time');
        localStorage.setItem('date_fast', time)
        if ($('#beginDate').val().slice(-3, -2) == '-') {
            $('#beginDate').val(date_fast(time).start.slice(0, 10));
            $('#endDate').val(date_fast(time).end.slice(0, 10));
        } else {
            $('#beginDate').val(date_fast(time).start);
            $('#endDate').val(date_fast(time).end);
        }
        $(this).closest('.search').find('#query_btn').click();
    })

    //日期快速查询,兼容模板返回页面
    if (localStorage.getItem('update_url') == 'false') {
        setTimeout(function () {
            nav_li.removeClass('active');
            nav_li.each(function (index, item) {
                if ($(item).attr('time') == localStorage.getItem('date_fast')) {
                    $(item).addClass('active');
                }
            });
        }, 100)
    } else {
        nav_li.eq(5).addClass('active');
    }

    //子菜单（如:佣金计算/发放记录）
    nav_sub_span = $('.nav-sub span');
    nav_data = $('.nav-data');
    nav_data.hide().eq(0).show();
    nav_sub_span.click(function () {
        nav_sub_span.removeClass('nav-select');
        $(this).addClass('nav-select');
        nav_data.hide().eq(nav_sub_span.index(this)).show();
    })
})
