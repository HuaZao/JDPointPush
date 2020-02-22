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
    "wskey": "填写你京东无线包的wskey",
    "x-app-id": "996"
}


def send_message(title, desp):
    if desp == "":
        desp = title
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
        params = {"mac": device["router_mac"], "source": "1", "currentPage": 1, "pageSize": 7}
        res = requests.get(url=jd_base_url + method, headers=headers, params=params)
        if res.status_code == 200:
            point_data_list = list(res.json()["result"]["pointRecords"])
            if len(point_data_list) > 0:
                # 判断是否今天
                create_time = point_data_list[0]["createTime"] / 1000
                point_amount = point_data_list[0]["pointAmount"]
                markdown_point_str = markdown_point_list(point_data_list)
                if is_today(create_time):
                    point_count = point_count + point_amount
                    point_desp = point_desp + "\n* " + device["router_name"] + "_" + \
                                 device["router_mac"] + " 到账积分" + str(point_amount) + markdown_point_str
                else:
                    point_desp = point_desp + "\n* " + device["router_name"] + "_" + \
                                 device["router_mac"] + " 今天没有获得任何积分" + markdown_point_str
            else:
                point_desp = point_desp + "\n* " + device["router_name"] + "_" + device["router_mac"] + " 积分尚未产生!"
    send_message(title=today_string + "总共到账积分:" + str(point_count), desp=point_desp)


def is_today(timeline):
    today_time_str = time.strftime("%Y%m%d", time.localtime(time.time()))
    point_time_str = time.strftime("%Y%m%d", time.localtime(timeline))
    return today_time_str == point_time_str


def today_string():
    return time.strftime("%Y_%m_%d", time.localtime(time.time()))


def time_string(timeline):
    return time.strftime("%Y_%m_%d", time.localtime(timeline))


def markdown_point_list(point_list):
    point_list_str = "\n"
    for point in point_list:
        create_time = time_string(point["createTime"] / 1000)
        point_amount = point["pointAmount"]
        point_list_str = point_list_str + "    - " + create_time + "增加" + str(point_amount) + "\n"
    return point_list_str

# def get_point_count():
#     method = "routerAccountInfo"
#     # params = {"mac": jd_router_mac}
#     res = requests.get(url=jd_base_url + method, headers=headers)
#     if res.status_code == 200:
#         point_amount = res.json()["result"]["accountInfo"]["amount"]
#         send_message(title="当前积分合计为" + str(point_amount), desp="")
#     else:
#         send_message(title="访问routerAccountInfo接口失败 Code:" + str(res.status_code),desp=res.text)


if __name__ == '__main__':
    get_point()
    # time.sleep(2)
    # get_point_count()
