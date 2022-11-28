import sys
import json
from websocket import WebSocketApp
import configparser

group_ids = dict() 

config = configparser.ConfigParser()
config.read('config.ini')

def on_message(ws:WebSocketApp,msg):
    msg = json.loads(msg)
    if msg.get('method') == 'chatroommemberAdd':
        group_id = msg.get('data', {}).get('wxid')
        group_ids.setdefault(member_id,group_id)
        member_id = msg.get('data', {}).get('member', [{}])[0].get('wxid','')
        data = json.dumps({
        "method": "getUserInfo",
        "wxid": member_id
        })
        ws.send(data)
    elif msg.get('method', '') == 'getUserInfo_Recv':
        wxid = msg.msg.get('data', {}).get('wxid','')
        nickname = msg.get('data', {}).get('nickName','')
        head_img = msg.get('data', {}).get('headImg','')
        group_id = group_ids.get(wxid,'')
        group_ids.pop(wxid)
        welcome = config.get(group_id)
        if welcome:
            title = config.get(group_id,title).replace('%nickname%',nickname) or '欢迎加入群聊'
            content = config.get(group_id,content).replace('%nickname%',nickname) or ''
            title = config.get(group_id,url) or head_img
            text = config.get(group_id,text)
            ws.send(json.dumps({
                "method": "sendAppmsgForward",
                "wxid": group_id,
                "xml": f"<?xml version=\"1.0\"?><msg><appmsg appid=\"\" sdkver=\"0\"><title>{title}</title><des>{content}</des><type>5</type><url>{url}</url><thumburl>{head_img}</thumburl></appmsg></msg>",
                "pid": 0
            }))
            if text:
                ws.send(json.dumps({
                    "method": "sendText",
                    "wxid": group_id,
                    "msg": text,
                    "atid": wxid,
                    "pid": 0
                }))

def on_open(ws):
    ws.send(json.dumps({
            "method": "sendText",
            "wxid": "filehelper",
            "msg": "群欢迎助手已启动",
            "atid": "",
            "pid": 0
        }))

if __name__ == "__main__":
    data = sys.argv
    name = data[data.index('--name') + 1]
    key = data[data.index('--key') + 1]
    url = "ws://127.0.0.1:8202/wx?name=" + name + "&key=" + key
    ws = WebSocketApp(url=url,on_message=on_message,on_open=on_open)
    ws.run_forever()