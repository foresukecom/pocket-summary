
from datetime import datetime
from urllib.request import urlopen
from urllib.parse   import quote
from json import loads
import urllib.request
import sys

def main(consumer_key, access_token):

	#アイテム数取得
	all_items = item_count(consumer_key, access_token, 'all')
	unread_items = item_count(consumer_key, access_token, 'unread')

	#ページタイトル取得
	page_title = generate_title(all_items, unread_items)

	#pocketにアイテムを追加する 
	add_item(consumer_key, access_token, page_title)



def item_count(consumer_key, access_token, state):
	"""
	pocketのアイテム数を取得する。
	consumer_key、access_token、stateを引数として受取り、アイテム数を戻り値として返す。
	"""
	
	count = 1000	#1回のgetコマンドで取得するアイテム数の上限
	offset = 0
	item_cnt = 0

	while(True):
		
		request_url = 'https://getpocket.com/v3/get?consumer_key={0}&access_token={1}&count={2}&offset={3}&state={4}'.format(consumer_key, access_token, count, offset, state)
		
		#html取得
		body = urlopen(request_url).read()
		body = body.decode('utf-8')
		body_json = loads(body)

		#JSONからアイテム数を取得する
		tmp_count = len(body_json['list'])

		#アイテム数の累算
		item_cnt = item_cnt + tmp_count

		#取得したアイテム数が、一度に取得できるアイテムの上限(count)より少なければ無限ループ終了する。
		if tmp_count < count:
			break
		
		offset = offset + count

	return item_cnt


def generate_title(all_items, unread_items):
	"""
	pocketに追加する統計情報表示用のアイテムのタイトルを生成する。
	全アイテム数と未読アイテム数を引数として受取り、日付と既読率をマージして返す。
	"""
	day = datetime.now().strftime('%Y年%m月%d日')
	
	read_items = all_items - unread_items
	read_rate = round((read_items / all_items)* 100, 1)
	
	title = '{0}, 全アイテム数:{1}, 未読アイテム数:{2}, 既読率:{3}%'.format(day, all_items, unread_items, read_rate)

	return title



def add_item(consumer_key, access_token, title):
	"""
	pocketに統計情報を追加する。
	"""
	#pocketの仕様上、アイテムのURLが重複すると上書きされるようなので、URLに日付を付与して一意にする。
	day = datetime.now().strftime('%Y%m%d')
	url = 'http://localhost/{0}'.format(day)
	
	tags = 'partition'

	#urlopenで全角の文字を指定するとUnicodeEncodeErrorになるので、urllib.parse.quoteでパースする。
	request_url = 'https://getpocket.com/v3/add?consumer_key={0}&access_token={1}&url={2}&title={3}&tags={4}'.format(consumer_key, access_token, url, quote(title), tags)
	urlopen(request_url)



if __name__ == '__main__':
	"""
	コマンドライン引数の処理
	引数が2つある場合のみ実際の処理をする。
	"""
    args = sys.argv
    if len(args) == 3:
        consumer_key = args[1]
        access_token = args[2]
        main(consumer_key, access_token)
    else:
        print('以下形式でconsumer_keyとaccess_tokenを指定してください')
        print('$ main.py <consumer_key> <access_token>')
        quit()

