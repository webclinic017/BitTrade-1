import requests

def create_order(title, text=''):
    url = "https://oapi.dingtalk.com/robot/send?access_token=469041a27e14b9de596be25b7291ff69654e65405400e406f4f3431f62c15ea4"
    headers = {'Content-type': 'application/json'}
    data = {
        "msgtype": "markdown",
        "markdown":
            {
                "title": 'YiDan提醒',
                "text": title + text
            },
        "at": {"isAtAll": True}
    }
    #requests.post(url, json=data, headers=headers)
