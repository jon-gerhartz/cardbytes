from datetime import datetime, timedelta
import pandas as pd
from bs4 import BeautifulSoup
import requests

cards = {
	'judge_rookie': '2017 Topps Chrome Aaron Judge Catching #169 PSA 9',
	'ichiro_rookie': '2001 Topps Ichiro Suzuki #726 PSA 9',
	'judge_rookie_gallery': 'Aaron Judge 2017 Topps Gallery #117 PSA 10',
	'cc_rookie': '1999 TOPPS TRADED CC SABATHIA ROOKIE #T33 FUTURE HOF YANKEES INDIANS PSA 9'
}

def get_prices(search_string, sold=True):
	search_query = search_string.replace(' ', '+').replace('#', '%23')
	if sold:
		url = f'https://www.ebay.com/sch/i.html?_from=R40&_nkw={search_query}&rt=nc&LH_Sold=1&_fsrp=1'
	else:
		url = f'https://www.ebay.com/sch/i.html?_from=R40&_nkw={search_query}&rt=nc'
	resp = requests.get(url)
	soup = BeautifulSoup(resp.text, 'lxml')
	items = soup.find_all('div',  attrs = {'class': 's-item__info clearfix'})
	items = items[1:]
	items_dict = {}
	i = 0
	for item in items:
		row = []
		try:
			title = item.find('div', attrs = {'class': 's-item__title'}).text
		except:
			title = item + '_' + i
		row.append(title)

		try:
			sold_date = item.find('span', attrs = {'class': 'POSITIVE'}).text
			sold_date = sold_date.replace('Sold  ', '')
			sold_date = datetime.strptime(sold_date, '%b %d, %Y')
		except Exception as e:
			sold_date = ''
		row.append(sold_date)

		try:
			price = item.find('span', attrs = {'class': 's-item__price'}).text
			price = price.replace('$', '')
			price = float(price)
		except:
			price = 0
		row.append(price)
		
		items_dict[i] = row
		i+=1

	df = pd.DataFrame.from_dict(items_dict, orient='index', columns=['item_title', 'sold_date', 'sale_price'])
	return df

def get_card_summary(cards, look_back_max=14):
	card_data = {}
	i = 0
	for name, search_string in cards.items():
		card_df = get_prices(search_string)
		now = datetime.now()
		now_minus_look_back = now - timedelta(days=look_back_max)
		last_sale_bool = card_df['sold_date'] >= now_minus_look_back
		card_df=card_df.loc[last_sale_bool]
		avg_price = round(card_df['sale_price'].mean(),2)
		last_sale = card_df['sold_date'].max()
		row = [name, avg_price, last_sale]
		card_data[i] = row
		i+=1
	card_summary_data = pd.DataFrame.from_dict(card_data, orient='index', columns=['card_name', 'market_price', 'last_sale'])
	return card_summary_data
card_summary_data = get_card_summary(cards)
print(card_summary_data)
total_cardfolio_value = card_summary_data['market_price'].sum()
print('Total cardfolio value:',total_cardfolio_value)
