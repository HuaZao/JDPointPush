# coding=utf-8
import requests
import time

# 京东API地址
jd_base_url = "https://mobile-api.jdcloud.com/v1/regions/cn-north-1/"

# Server酱 如 https://sc.ftqq.com/abc123456789.send
server_chan_url = "https://sc.ftqq.com/填写你的Key.send"

# 京东路由器设备列表,按照格式可填写多台
jd_router_device_list = [
    {"router_name": "京东无线路由宝", "router_mac": "AABBCCDDEEFF"}
]

# 多台示例,MAC需要全部大写如 AABBCCDDEE11
# jd_router_device_list = [
#     {"router_name": "机器01", "router_mac": "XXXXXXXXXX"},
#     {"router_name": "机器02", "router_mac": "XXXXXXXXXX"},
#     {"router_name": "机器03", "router_mac": "XXXXXXXXXX"},
#     {"router_name": "机器04", "router_mac": "XXXXXXXXXX"},
#     ....................
# ]

# x-app-id 固定996
headers = {
    "wskey": "填写你京东无线宝的wskey",
    "x-app-id": "996",
    "Content-Type": "application/json"
}

# 每天积分自动兑换成京豆(1-启用 0-关闭)
is_auto_exchange = 0


def send_message(title, desp):
    res = requests.get(url=server_chan_url, params={"text": title, "desp": desp})
    if res.status_code == 200:
        print("消息已推送!")
    else:
        print("消息推送失败!")
    print("title = >" + title)
    print("desp = >" + desp)


def get_point():
    method = "pointOperateRecords:show"
    point_count = 0
    point_desp = ""
    for device in jd_router_device_list:
        router_mac = device["router_mac"]
        router_name = device["router_name"]
        device_point_total = get_point_count(router_mac)
        params = {"mac": router_mac, "source": "1", "currentPage": 1, "pageSize": 7}
        res = requests.get(url=jd_base_url + method, headers=headers, params=params)
        if res.status_code == 200:
            point_data_list = list(res.json()["result"]["pointRecords"])
            if len(point_data_list) > 0:
                # 筛选出recordType为1的数据
                add_record_list = filter(is_add_record,point_data_list)
                first_record = list(add_record_list)[0]
                create_time = first_record["createTime"] / 1000
                point_amount = first_record["pointAmount"]
                markdown_point_str = markdown_point_list(point_data_list)
                # 判断是否今天到账新的积分
                if is_today(create_time):
                    point_count = point_count + point_amount
                    point_desp = point_desp + "\n* " + router_name + "_" + router_mac[-3:] + " 到账积分" + str(point_amount)
                    # 是否自动兑换积分
                    if is_auto_exchange:
                        if point_exchange(router_mac, point_amount):
                            point_desp = point_desp + ",已自动兑换为京豆"
                        else:
                            point_desp = point_desp + ",京豆兑换失败"
                    # 添加积分记录
                    point_desp = point_desp + markdown_point_str
                else:
                    point_desp = point_desp + "\n* " + router_name + "_" + \
                                 router_mac[-3:] + " 今天没有获得任何积分" + markdown_point_str
            else:
                point_desp = point_desp + "\n* " + router_name + "_" + router_mac[-3:] + " 积分尚未产生!"
        else:
            point_desp = point_desp + "\n* " + router_name + "_" + router_mac[-3:] + " " + res.text
    send_message(title=today_string() + "总共到账积分:" + str(point_count), desp=point_desp)


def is_today(timeline):
    today_time_str = time.strftime("%Y%m%d", time.localtime(time.time()))
    point_time_str = time.strftime("%Y%m%d", time.localtime(timeline))
    return today_time_str == point_time_str


def time_string(timeline):
    return time.strftime("%Y_%m_%d", time.localtime(timeline))


def today_string():
    return time.strftime("%Y_%m_%d", time.localtime(time.time()))


def is_add_record(list):
    return list["recordType"] == 1


def markdown_point_list(point_list):
    point_list_str = "\n"
    for point in point_list:
        create_time = time_string(point["createTime"] / 1000)
        point_amount = point["pointAmount"]
        if point["recordType"] == 1:
            point_list_str = point_list_str + "    - " + create_time + " 收入" + str(point_amount) + "\n"
        else:
            point_list_str = point_list_str + "    - " + create_time + " 支出" + str(point_amount) + "\n"
    # 添加分割线
    point_list_str = point_list_str + "\n-------"
    return point_list_str


def get_point_count(mac):
    method = "routerAccountInfo"
    params = {"mac": mac}
    point_amount = 0
    res = requests.get(url=jd_base_url + method, params=params, headers=headers)
    if res.status_code == 200:
        point_amount = res.json()["result"]["accountInfo"]["amount"]
    return point_amount


def point_exchange(mac, point_amount):
    method = "point:exchange"
    params = {
        "pointExchangeReqVo": {
            "deviceId": mac,
            "pointAmount": point_amount,
            "source": 3
        },
        "regionId": "cn-north-1"}
    res = requests.post(url=jd_base_url + method, json=params, headers=headers)
    return res.status_code == 200


if __name__ == '__main__':
    get_point()
