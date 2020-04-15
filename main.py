import requests
import pprint
from statistics import mean
from itertools import count


def predict_rub_salary(vacancy):
    salary = vacancy['salary']
    if not salary or salary['currency'] != 'RUR':
        return None

    if not salary['from']:
        return salary['to'] * 0.8
    if not salary['to']:
        return salary['from'] * 1.2
    return (salary['from'] + salary['to']) / 2


def fetch_records(language):
    for page in count():
        print(page)
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

languages_popularity = {}

for language in languages:
    payload = {
        'text': 'Программист {}'.format(language),
        'search_field': 'name',
        'area': 1,
        'period': 30
    }
    response = requests.get('https://api.hh.ru/vacancies', params=payload)
    response.raise_for_status()

    vacancy_salaries = []
    for vacancy in fetch_records(language):
        vacancy_salaries.append(predict_rub_salary(vacancy))

    vacancy_salaries_wo_none = list(filter(None, vacancy_salaries))
    languages_popularity[language] = {
        'vacancies_found': response.json()['found'],
        'vacancies_processed': len(vacancy_salaries_wo_none),
        'average_salary': int(mean(vacancy_salaries_wo_none))
    }

pprint.pprint(languages_popularity)


