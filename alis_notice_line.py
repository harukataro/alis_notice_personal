import alis_util as alis
import idpw
import requests
from datetime import datetime as dt

INIFILE = './last_created_at.ini'
JST_DIFF = 9 * 60 * 60


def line_notify(message):
    line_notify_token = idpw.line_notify_token
    line_notify_api = 'https://notify-api.line.me/api/notify'

    payload = {'message': message}
    headers = {'Authorization': 'Bearer ' + line_notify_token}
    requests.post(line_notify_api, data=payload, headers=headers)


def message_gen(notification):
    type = notification["type"]
    msg = ''
    create_time = dt.fromtimestamp(notification['created_at'] + JST_DIFF).strftime('%Y/%m/%d %H:%M')

    if type == 'thread':
        acted_user = alis.get_user_name(notification['acted_user_id'])
        msg += f'{acted_user}さんが、あなたの記事にコメントしました。'
        msg += f'{notification["article_title"]}\n'
        msg += f'{create_time}\n'
        msg += f'https://alis.to/haruka/articles/{notification["article_id"]}/#article-comments'
    elif type == 'reply':
        acted_user = alis.get_user_name(notification['acted_user_id'])
        msg += f'{acted_user}さんが、あなたのコメントに返信しました。'
        msg += f'{notification["article_title"]}\n'
        msg += f'{create_time}\n'
        msg += f'https://alis.to/haruka/articles/{notification["article_id"]}/#article-comments'

    elif type == 'tip':
        acted_user = alis.get_user_name(notification['acted_user_id'])
        tip_val = notification["tip_value"] / 10e+17
        msg += f'{acted_user}さんから{tip_val} ALISを受け取りました。'
        msg += f'{notification["article_title"]}\n'
        msg += f'{create_time}\n'
        msg += f'https://alis.to/users/{notification["acted_user_id"]}'

    elif type == 'like':
        liked_count = notification['liked_count']
        msg += f'{liked_count}人があなたの記事にいいねをしました。'
        msg += f'{notification["article_title"]}\n'
        msg += f'{create_time}\n'
        msg += f'https://alis.to/haruka/articles/{notification["article_id"]}'
    print(msg)
    return msg


if __name__ == '__main__':

    with open(INIFILE) as f:
        last_time = int(f.read())

    accesstoken = alis.get_access_token(idpw.ID, idpw.PW)

    #if alis.is_unread_notification(accesstoken):
    if True:
        notifications = alis.notifications(accesstoken)
        for notification in notifications['Items']:
            if notification['created_at'] > last_time:
                message = message_gen(notification)
                line_notify(message)
            else:
                break
        with open(INIFILE, mode='w') as f:
            f.write(str(notifications['Items'][0]['created_at']))
