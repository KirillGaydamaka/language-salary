import requests
from statistics import mean
from itertools import count
from terminaltables import AsciiTable
from dotenv import load_dotenv
import os


def predict_salary(salary_from, salary_to):
    if (not salary_from) or (salary_from == 0):
        return salary_to * 0.8
    if (not salary_to) or salary_to:
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
        page_response = requests.get(url_sj, params=payload, headers=headers_sj)
        page_response.raise_for_status()
        page_data = page_response.json()
        yield from page_data['objects']
        if not page_data['more']:
            break


def get_languages_popularity_hh(languages):
    languages_popularity = {}
    for language in languages:
        payload = {
            'text': 'Программист {}'.format(language),
            'search_field': 'name',
            'area': 1,
            'period': 30
        }
        response = requests.get(url_hh, params=payload)
        response.raise_for_status()
        vacancy_salaries = []
        for vacancy in fetch_vacancies_hh(language):
            vacancy_salaries.append(predict_rub_salary_hh(vacancy))
        vacancy_salaries_wo_none = list(filter(None, vacancy_salaries))
        languages_popularity[language] = {
            'vacancies_found': response.json()['found'],
            'vacancies_processed': len(vacancy_salaries_wo_none),
            'average_salary': int(mean(vacancy_salaries_wo_none))
        }
    return languages_popularity


def get_languages_popularity_sj(languages):
    languages_popularity = {}
    for language in languages:
        payload = {
            'town': '4',
            'catalogues': '48',
            'keywords[0][keys]': 'Программист',
            'keywords[0][srws]': 1,
            'keywords[1][keys]': language,
            'keywords[1][srws]': 1,
            'keywords[1][skwc]': 'and',
        }
        response = requests.get(url_sj, params=payload, headers=headers_sj)
        response.raise_for_status()

        vacancy_salaries = []
        for vacancy in fetch_vacancies_sj(language):
            vacancy_salaries.append(predict_rub_salary_sj(vacancy))
        vacancy_salaries_wo_none = list(filter(None, vacancy_salaries))
        if vacancy_salaries_wo_none:
            mean_salary = int(mean(vacancy_salaries_wo_none))
        else:
            mean_salary = None
        languages_popularity[language] = {
            'vacancies_found': response.json()['total'],
            'vacancies_processed': len(vacancy_salaries_wo_none),
            'average_salary': mean_salary
        }

    return languages_popularity


def make_table(language_popularity, title):
    table_data = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']
        ]
    for language in language_popularity:
        table_data.append([
            language,
            language_popularity[language]['vacancies_found'],
            language_popularity[language]['vacancies_processed'],
            language_popularity[language]['average_salary']])
    table = AsciiTable(table_data, title)
    return table


if __name__ == '__main__':
    load_dotenv()

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

    app_id = os.getenv('APP_ID')
    headers_sj = {'X-Api-App-Id': app_id}

    url_sj = 'https://api.superjob.ru/2.0/vacancies/'
    url_hh = 'https://api.hh.ru/vacancies'

    languages_popularity_hh = get_languages_popularity_hh(languages)
    languages_popularity_sj = get_languages_popularity_sj(languages)

    print(make_table(languages_popularity_hh, "HeadHunter Moscow").table)
    print(make_table(languages_popularity_sj, "SuperJob Moscow").table)

