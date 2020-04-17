import requests
import pprint
from statistics import mean
from itertools import count


def predict_salary(salary_from, salary_to):
    if (not salary_from) or (salary_from == 0):
        return salary_to * 0.8
    if (not salary_to) or (salary_to):
        return salary_from * 1.2
    return (salary_from + salary_to) / 2


def predict_rub_salary_hh(vacancy):
    salary = vacancy['salary']
    if not salary or salary['currency'] != 'RUR':
        return None
    return predict_salary(salary['from'], salary['to'])

def predict_rub_salary_sj(vacancy):
    if vacancy['payment_from'] == 0 and vacancy['payment_to'] == 0:
        return None
    else:
        return predict_salary(vacancy['payment_from'], vacancy['payment_to'])

def fetch_vacancies_hh(language):
    for page in count():
        payload = {
            'text': 'Программист {}'.format(language),
            'search_field': 'name',
            'area': 1,
            'period': 30,
            'page': page
        }
        page_response = \
            requests.get('https://api.hh.ru/vacancies', params=payload)
        page_response.raise_for_status()
        page_data = page_response.json()

        if page >= page_data['pages']:
            break

        yield from page_data['items']


def fetch_vacancies_sj(language):
    for page in count():
        payload = {
            'town': '4',
            'catalogues': '48',
            'keywords[0][keys]': 'Программист',
            'keywords[0][srws]': 1,
            'keywords[1][keys]': language,
            'keywords[1][srws]': 1,
            'keywords[1][skwc]': 'and',
            'page': page
        }
        page_response = requests.get(url_sj, params=payload, headers=headers)
        page_response.raise_for_status()
        page_data = page_response.json()
        yield from page_data['objects']
        if not page_data['more']:
            break

languages = [
    'JavaScript',
    'Java',
    'Python',
    'Ruby',
    'PHP',
    'C++',
    'C#',
    'C',
    'Go',
    'Objective-C',
    'Scala',
    'Swift',
    'TypeScript',
]

languages_popularity_hh = {}

for language in languages:
    print(language)
    payload = {
        'text': 'Программист {}'.format(language),
        'search_field': 'name',
        'area': 1,
        'period': 30
    }
    response = requests.get('https://api.hh.ru/vacancies', params=payload)
    response.raise_for_status()

    vacancy_salaries = []
    for vacancy in fetch_vacancies_hh(language):
        vacancy_salaries.append(predict_rub_salary_hh(vacancy))

    vacancy_salaries_wo_none = list(filter(None, vacancy_salaries))
    languages_popularity_hh[language] = {
        'vacancies_found': response.json()['found'],
        'vacancies_processed': len(vacancy_salaries_wo_none),
        'average_salary': int(mean(vacancy_salaries_wo_none))
    }

pprint.pprint(languages_popularity_hh)


url_sj = 'https://api.superjob.ru/2.0/vacancies/'

headers = {
    'X-Api-App-Id': 'v3.r.132228763.49539bb63c4ceef06bdbfbd37374931114a7ef2f.9a1749bd9364951dfa0e2e5fbe7602c0e58109f3'
}

languages_popularity_sj = {}

for language in languages:
    #print(language)
    payload = {
        'town': '4',
        'catalogues': '48',
        'keywords[0][keys]': 'Программист',
        'keywords[0][srws]': 1,
        'keywords[1][keys]': language,
        'keywords[1][srws]': 1,
        'keywords[1][skwc]': 'and',
    }
    response = requests.get(url_sj, params=payload, headers=headers)
    response.raise_for_status()

    vacancy_salaries = []
    for vacancy in fetch_vacancies_sj(language):
        vacancy_salaries.append(predict_rub_salary_sj(vacancy))
    vacancy_salaries_wo_none = list(filter(None, vacancy_salaries))
    if vacancy_salaries_wo_none:
        mean_salary = int(mean(vacancy_salaries_wo_none))
    else:
        mean_salary = None
    languages_popularity_sj[language] = {
        'vacancies_found': response.json()['total'],
        'vacancies_processed': len(vacancy_salaries_wo_none),
        'average_salary': mean_salary
    }

pprint.pprint(languages_popularity_sj)
