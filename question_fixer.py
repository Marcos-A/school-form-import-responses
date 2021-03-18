from config import config_master, config_public
from datetime import datetime
import psycopg2
from pytz import timezone
from query_master import *


def format_timestamp(timestamp):
    localtz = timezone('Europe/Madrid')    
    datetime_format_timestamp = datetime.strptime(timestamp, '%Y/%m/%d %H:%M:%S.%f')
    timezone_aware_timestamp = localtz.localize(datetime_format_timestamp)
    return timezone_aware_timestamp


def get_type_id(type_name):
    sql = "SELECT id FROM master.type WHERE name = %s;"
    conn = None
    try:
        params = config_master()
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        cursor.execute(sql, (type_name,))
        type_id = cursor.fetchone()[0]
        cursor.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        catch_exception(error)
    finally:
        if conn is not None:
            conn.close()
        return type_id


def add_question():
    question_statement = "T’agraden les activitats extraescolars que es fan dins i fora del centre? (Xerrades, competicions esportives, sortides...)"
    disabled_timestamp = format_timestamp("2021/02/01 00:00:00.000000")
    type_id = get_type_id('Numeric')
    level_id = get_level_id('CF')
    topic_id = get_topic_id('Centre')
    created_timestamp = format_timestamp("2017/01/01 00:00:00.000000")
    question_data = (5, question_statement, disabled_timestamp, type_id, level_id, topic_id, created_timestamp)
    sql = """
            INSERT INTO master.question(sort, statement, disabled, type_id, level_id, topic_id, created)
            VALUES(%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
          """
    conn = None
    try:
        params = config_master()
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        cursor.execute(sql, question_data)
        question_id = cursor.fetchone()[0]
        cursor.close()
        conn.commit()
        succeed()
    except (Exception, psycopg2.DatabaseError) as error:
        catch_exception(error)
    finally:
        if conn is not None:
            conn.close()
        return question_id, level_id


# Get question id from 'master' schema of database
def get_question_id(sort, level_id, subject_code):
    sql = """
            SELECT id FROM master.question
            WHERE sort = %s AND level_id = %s AND
                  topic_id = %s AND disabled IS NULL;
          """
    conn = None
    try:
        params = config_master()
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        cursor.execute(sql, (sort, level_id, get_topic_id(subject_code)))
        question_id = cursor.fetchone()[0]
        cursor.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        catch_exception(error)
    finally:
        if conn is not None:
            conn.close()
        return question_id


def update_question_number(updated_question_id, current_question_id):
    sql = """
            UPDATE forms_answer AS an
            SET question_id = %s
            FROM forms_evaluation AS fe
            WHERE fe.id = an.evaluation_id
                AND fe.timestamp <= '2021/01/01'::date
                AND an.question_id = %s;
          """
    test2 = """
            UPDATE public.forms_answer 
            SET question_id = %s
            FROM public.forms_answer an
                LEFT JOIN public.forms_evaluation fe ON fe.id = an.evaluation_id
            WHERE fe.timestamp <= '2021/01/01'::date
                AND an.question_id = %s;
          """

    test = """
            SELECT an.question_id, fe.timestamp
            FROM public.forms_answer an
                LEFT JOIN public.forms_evaluation fe ON fe.id = an.id
            WHERE fe.timestamp <= '2021/01/01'::date
          """
    conn = None
    try:
        params = config_public()
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        cursor.execute(sql, (updated_question_id, current_question_id,))
        cursor.close()
        conn.commit()
        succeed()
    except (Exception, psycopg2.DatabaseError) as error:
        catch_exception(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    print("\u200a\u200aAdding old question to the database...", end =" ")
    updated_question_id, level_id = add_question()
    current_question_id = get_question_id(5, level_id, 'Centre')
    print("\u200a\u200aUpdating question id in old answers...", end =" ")
    update_question_number(updated_question_id, current_question_id)
