import time
import json
import os

import requests
import fake_headers
import bs4


def connection():
    """"""
    headers = fake_headers.Headers(browser="firefox", os="win")
    headers_dict = headers.generate()
    main_html = requests.get("https://spb.hh.ru/search/vacancy?text=python&salary=&area=1&area=2&ored_clusters=true",
                             headers=headers_dict).text
    return main_html


def creating_list(main_html):
    """"""
    main_soup = bs4.BeautifulSoup(main_html, "lxml")
    div_vacancy_serp__results_tag = main_soup.find('div', id="a11y-main-content")
    div_serp_item_tags = div_vacancy_serp__results_tag.find_all("div", class_='serp-item')

    vacancy_info = []

    for div_serp_item_tag in div_serp_item_tags:
        h3_tag = div_serp_item_tag.find("h3")
        title = h3_tag.text
        link = h3_tag.find("a")['href']
        company = div_serp_item_tag.find_all("a", attrs={'data-qa': 'vacancy-serp__vacancy-employer'})[0].text
        city = div_serp_item_tag.find("div", attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text

        headers = fake_headers.Headers(browser="firefox", os="win")
        full_serp_item_html = requests.get(link, headers=headers.generate()).text

        full_serp_item_soup = bs4.BeautifulSoup(full_serp_item_html, "lxml")
        div_vacancy_description_tags = full_serp_item_soup.find('div', class_='vacancy-description').text
        vacancy_description_text = " ".join(div_vacancy_description_tags.split('\n')).strip()
        vacancy_description_text = " ".join(vacancy_description_text.split())

        if "Django" and "Flask" in vacancy_description_text:
            fork_salary = full_serp_item_soup.find("span", attrs={'data-qa': 'vacancy-salary-compensation-type-net'})
            fork_salary_text = ''
            try:
                fork_salary_text = fork_salary.text
            except:
                pass

            vacancy_info.append(
                {
                    "title": title.replace(u'\xa0', ' '),
                    "description": vacancy_description_text.replace(u'\xa0', ' '),
                    "salary": fork_salary_text.replace(u'\xa0', ' '),
                    "company": company.replace(u'\xa0', ' '),
                    "city": city.replace(u'\xa0', ' '),
                    "link": link,
                }
            )
        time.sleep(0.3)
    return vacancy_info


if __name__ == '__main__':
    os.remove('scrapping-hh.json')
    main_html = connection()
    vacancy = creating_list(main_html)

    with open('scrapping-hh.json', 'a', encoding="utf-8") as f:
        json.dump(vacancy, f, ensure_ascii=False, indent=2)

