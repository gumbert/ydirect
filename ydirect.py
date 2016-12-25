# -*- coding: utf-8 -*-
from grab import Grab
from tqdm import tqdm
import re
import time

# получаем количество страниц с объявлениями
def get_pages(g, url, query):
	print(query)
	fullurl = url.format(query, 0)
	g.go(fullurl)

	# проверка последней цифры
	try:
		pages = g.doc.select('//a[@class="b-pager__page"]')[-1].text()
	except:
		print('pass', fullurl)

	# если в конце стоит многоточие
	if pages == '\u2026':
		pages = g.doc.select('//a[@class="b-pager__page"]')[-2].text()
		fullurl = url.format(query, int(pages))
		g.go(fullurl)
		pages = g.doc.select('//a[@class="b-pager__page"]')[-1].text()

	return pages	


def main():
	g = Grab()
	g.setup(encoding='utf-8', connect_timeout=3, timeout=5)

	# список запросов
	words = [
				'застройщики москвы и московской области',
				'новостройки с отделкой в подмосковье от застройщика'
			]
	
	url = 'http://direct.yandex.ru/search?&rid=213&text={0}&page={1}'

	with open('firms.csv', 'wt', encoding="utf-8") as f:
		f.write('"firm";"phone";"email";"title";"text";"domain"'+'\n')
		
		# номер телефона будем использовать за уникальное поле
		uniq_phones = []

		for query in words:
			pages = get_pages(g, url, query)

			for page in tqdm(range(int(pages))):
				
				fullurl = url.format(query, page)
				g.go(fullurl)
				
				for item in g.doc.select('//div[@class="banner-selection"]'):

					# получаем заголовок и текст объявления
					ad_title = re.sub(r'"', '', item.select('./div[@class="ad"]/div[@class="ad-link"]').text())
					ad_body = re.sub(r'"', '', item.select('./div[@class="ad"]/div')[-1].text())

					# пробуем получить название компании, телефон и почту
					try:
						# получаем ссылку на карточку объявления
						ad_url = item.select('./div[@class="ad"]/span/a[@class="vcard"]').attr('href')
						g1 = Grab()
						g1.go(ad_url)

						try:
							ad_h1 = re.sub(r'"', '', g1.doc.select('//h1').text())
						except:
							ad_h1 = ''

						try:
							ad_phone = g1.doc.select('//div[@class="contact-item call-button-container"]/div[@class="large-text"]').text()
						except:
							ad_phone = ''

						try:
							ad_email = g1.doc.select('//a[@class="email"]').text()
						except:
							ad_email = ''
					except:
						ad_h1 = ''
						ad_phone = ''
						ad_email = ''

					# пробуем получить адрес сайта
					try:
						ad_domain = item.select('./div[@class="ad"]/span/span[@class="domain"]').text()
					except:
						ad_domain = ''

					# если объявление с таким номером уже есть, не добавляем его
					if ad_phone in uniq_phones:
						pass
					else:
						f.write('"'+ad_h1+'";"'+ad_phone+'";"'+ad_email+'";"'+ad_title+'";"'+ad_body+'";"'+ad_domain+'"'+'\n')
						uniq_phones.append(ad_phone)
		f.close()

if __name__ == "__main__":
    main()
