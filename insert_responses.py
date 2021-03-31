# -*- coding: UTF-8 -*-

from query_master import *
import csv
from datetime import datetime
from pytz import timezone
from sys import argv


def extract_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file_responses:
            responses_reader = csv.DictReader(file_responses)

            for row in responses_reader:
                timestamp = format_timestamp(row["TIMESTAMP"])
                group_id, degree_id = get_group_id_and_degree_id(fix_group_name(row["GRUP"]))
                trainer_name = get_trainer_name(row["OBJECTE"])
                subject_code = get_subject_code(row["OBJECTE"], row["GRUP"])
                subject_id = get_subject_id(subject_code, degree_id)
                trainer_id = get_trainer_id_by_name(trainer_name)
                level_id = get_level_id('CF')
                evaluation_id = save_evaluation(timestamp, group_id, trainer_id, subject_id,)

                extract_evaluations(evaluation_id, level_id, subject_code, row)
        succeed()
    except Exception as e:
        catch_exception(e)


def extract_evaluations(evaluation_id, level_id, subject_code, row):
    if subject_code == 'Centre':
        question1_id = get_question_id(1, level_id, subject_code)
        save_answer(row['CENTRE-ÍTEM1'], question1_id, evaluation_id)

        question2_id = get_question_id(2, level_id, subject_code)
        save_answer(row['CENTRE-ÍTEM2'], question2_id, evaluation_id)

        question3_id = get_question_id(3, level_id, subject_code)
        save_answer(row['CENTRE-ÍTEM3'], question3_id, evaluation_id)

        question4_id = get_question_id(4, level_id, subject_code)
        save_answer(row['CENTRE-ÍTEM4'], question4_id, evaluation_id)

        question5_id = get_question_id(5, level_id, subject_code)
        save_answer(row['CENTRE-ÍTEM5'], question5_id, evaluation_id)

        question6_id = get_question_id(6, level_id, subject_code)
        save_answer(row['CENTRE-ÍTEM6'], question6_id, evaluation_id)

        opinion_id = get_question_id(7, level_id, subject_code)
        save_answer(row['CENTRE-COMENTARI'], opinion_id, evaluation_id)

    elif subject_code == 'Tutoria1':
        question1_id = get_question_id(1, level_id, subject_code)
        save_answer(row['TUTORIA1-ÍTEM1'], question1_id, evaluation_id)

        question2_id = get_question_id(2, level_id, subject_code)
        save_answer(row['TUTORIA1-ÍTEM2'], question2_id, evaluation_id)

        question3_id = get_question_id(3, level_id, subject_code)
        save_answer(row['TUTORIA1-ÍTEM3'], question3_id, evaluation_id)

        opinion_id = get_question_id(4, level_id, subject_code)
        save_answer(row['TUTORIA1-COMENTARI'], opinion_id, evaluation_id)

    elif subject_code == 'Tutoria2':
        question1_id = get_question_id(1, level_id, subject_code)
        save_answer(row['TUTORIA2-ÍTEM1'], question1_id, evaluation_id)

        question2_id = get_question_id(2, level_id, subject_code)
        save_answer(row['TUTORIA2-ÍTEM2'], question2_id, evaluation_id)

        question3_id = get_question_id(3, level_id, subject_code)
        save_answer(row['TUTORIA2-ÍTEM3'], question3_id, evaluation_id)

        question4_id = get_question_id(4, level_id, subject_code)
        save_answer(row['TUTORIA2-ÍTEM4'], question4_id, evaluation_id)

        opinion_id = get_question_id(5, level_id, subject_code)
        save_answer(row['TUTORIA2-COMENTARI'], opinion_id, evaluation_id)

    # Assignatura
    else:
        question1_id = get_question_id(1, level_id, subject_code)
        save_answer(row['MP-ÍTEM1'], question1_id, evaluation_id)

        question2_id = get_question_id(2, level_id, subject_code)
        save_answer(row['MP-ÍTEM2'], question2_id, evaluation_id)

        question3_id = get_question_id(3, level_id, subject_code)
        save_answer(row['MP-ÍTEM3'], question3_id, evaluation_id)

        question4_id = get_question_id(4, level_id, subject_code)
        save_answer(row['MP-ÍTEM4'], question4_id, evaluation_id)

        opinion_id = get_question_id(5, level_id, subject_code)
        save_answer(row['MP-COMENTARI'], opinion_id, evaluation_id)


def format_timestamp(timestamp):
    localtz = timezone('Europe/Madrid')
    # Add fake milliseconds to date without millisecods record
    timestamp = timestamp+'.000000'
    
    datetime_format_timestamp = datetime.strptime(timestamp, '%m/%d/%Y %H:%M:%S.%f')

    timezone_aware_timestamp = localtz.localize(datetime_format_timestamp)

    return timezone_aware_timestamp


def get_subject_code(full_item_info, group_info):
    if "centre" in full_item_info.lower():
        return "Centre"

    elif "tutoria" in full_item_info.lower():
        if '1' in group_info:
            return "Tutoria1"
        elif '2' in group_info:
            return "Tutoria2"
    else:
        if '-' in full_item_info:
            item = full_item_info.split(' - ')[0]
        else:
            item = full_item_info
        return item


# Fix DAM group names
def fix_group_name(group):
    if group == 'DAM1A':
        return 'DAM1'
    elif group == 'DAM1B':
        return 'ASIX1'
    elif group == 'DAM2':
    	return 'DAM2A'
    else:
        return group


# Extract trainer's name from row["OBJECTE"]
def get_trainer_name(objecte):
    if (not "(" in objecte and not ")" in objecte):
        return None
    else:
        trainer_name = objecte.split('(')[1].split(')')[0]
        if trainer_name == 'Ana':
            return 'Ana L'
        elif trainer_name == 'Anna':
            return 'Anna C'
        elif trainer_name == 'Juan':
            return 'Juan Z'
        elif trainer_name == 'Marcos':
            return 'Marcos A'
        elif trainer_name == 'Montse':
            return 'Montse P'
        elif trainer_name == 'Xavi':
            return 'Xavi C'
        else:
            return None


if __name__ == '__main__':
    filename = argv[1]
    print('\033[93m' + 'Inserting answers into database. This process may take a while.' + '\033[0m')
    print("\u200a\u200aImporting data from " + filename + "...", end=" ")
    extract_data(filename)
