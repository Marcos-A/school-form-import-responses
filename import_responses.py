# -*- coding: UTF-8 -*-

from config import config
import csv
import psycopg2
from sys import argv
from datetime import datetime
from pytz import timezone

#FILENAME = 'resultats_respostes.csv'

def extract_data(filename):
    data = ()
    with open(filename, 'r', encoding='utf-8') as file_responses:
        responses_reader = csv.DictReader(file_responses)

        for row in responses_reader:
            level = 'CF'
            timestamp = format_timestamp(row["TIMESTAMP"])
            classgroup = row["GRUP"]
            degree = get_degree(row["GRUP"])
            subject = get_item(row["OBJECTE"])

            row_data = [timestamp,
                        level,
                        degree,
                        classgroup,
                        subject
                        ] + extract_evaluations_with_comment(row)

            data += (tuple(row_data),)

    return data


def format_timestamp(timestamp):
    localtz = timezone('Europe/Madrid')
    # Add fake milliseconds to date without millisecods record
    timestamp = timestamp+'.000000'
    
    datetime_format_timestamp = datetime.strptime(timestamp, '%m/%d/%Y %H:%M:%S.%f')

    timezone_aware_timestamp = localtz.localize(datetime_format_timestamp)

    return timezone_aware_timestamp


def get_degree(classgroup):
    degree = ''
    for letter in classgroup:
        if not letter.isnumeric():
            degree += letter
        else:
            break

    return degree


def get_item(full_item_info):
    if "centre" in full_item_info.lower():
        return "Centre"

    elif "tutoria" in full_item_info.lower():
        return "Tutoria"

    else:
        if '-' in full_item_info:
            item = full_item_info.split(' - ')[0]
        else:
            item = full_item_info
        # Remove leading zeroes
        if item[2] == '0' and item[3].isnumeric():
            item = item[0] + item[1] + item[3]

        return item


def extract_evaluations_with_comment(evaluations_dict):
    evaluations = []
    for value in evaluations_dict.values():
        if value.isnumeric() and int(value)>=1 and int(value)<=10:
            evaluations.append(value)

    while len(evaluations)<6:
        evaluations.append(None)

    comment_added = False
    for key in evaluations_dict.keys():
        if 'comentari' in key.lower() and evaluations_dict.get(key) != '':
            evaluations.append(evaluations_dict.get(key))
            comment_added = True

    if not comment_added: evaluations.append('')

    return evaluations


def export_data_to_db(data):
    sql = """
         INSERT INTO forms_evaluation(timestamp,
                                      level, degree_id,
                                      classgroup, subject_id,
                                      question1, question2, question3,
                                      question4, question5, question6,
                                      opinion)
         VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
      """
    conn = None
    try:
        params = config()
        print('Connecting to the PostgreSQL database...')

        conn = psycopg2.connect(**params)
        cursor = conn.cursor()

        cursor.executemany(sql, data)

        cursor.close()
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    filename = argv[1]
    data = extract_data(filename)
    export_data_to_db(data)
