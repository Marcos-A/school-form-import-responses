from config import config_master, config_public
import psycopg2
import sys
import traceback


def get_level_id(level_code):
    sql = """
            SELECT id FROM master.level
            WHERE code = %s;
          """
    conn = None
    try:
        params = config_master()
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        cursor.execute(sql, (level_code,))
        level_id = cursor.fetchone()[0]
        cursor.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        catch_exception(error)
    finally:
        if conn is not None:
            conn.close()
        return level_id



def get_group_id_and_degree_id(group_name):
    sql = """
            SELECT id, degree_id FROM master."group"
            WHERE name = %s;
          """
    conn = None
    try:
        params = config_master()
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        cursor.execute(sql, (group_name,))
        query_result = cursor.fetchone()
        group_id = query_result[0]
        degree_id = query_result[1]
        cursor.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        catch_exception(error)
    finally:
        if conn is not None:
            conn.close()
        return group_id, degree_id


# Get trainer id from trainer name
def get_trainer_id_by_name(trainer_name):
    if trainer_name is None:
        return None
    else:
        sql = "SELECT id FROM master.trainer WHERE name = %s;"
        conn = None
        try:
            params = config_master()
            conn = psycopg2.connect(**params)
            cursor = conn.cursor()
            cursor.execute(sql, (trainer_name,))
            trainer_id = cursor.fetchone()[0]
            cursor.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            catch_exception(error)
        finally:
            if conn is not None:
                conn.close()
            return trainer_id


# Get subject id from 'master' schema of database
def get_subject_id(subject_code, degree_id):
    sql = "SELECT id FROM master.subject WHERE code = %s AND degree_id = %s;"
    conn = None
    try:
        params = config_master()
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        cursor.execute(sql, (subject_code, degree_id,))
        subject_id = cursor.fetchone()[0]
        cursor.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        catch_exception(error)
    finally:
        if conn is not None:
            conn.close()
        return subject_id


def save_evaluation(timestamp, group_id, trainer_id, subject_id):
    evaluation_data = (timestamp, group_id, trainer_id, subject_id,)
    sql = """
            INSERT INTO public.forms_evaluation(timestamp, group_id, trainer_id, subject_id)
            VALUES(%s, %s, %s, %s)
            RETURNING id;
          """
    conn = None
    try:
        params = config_public()
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        cursor.execute(sql, evaluation_data)
        evaluation_id = cursor.fetchone()[0]
        cursor.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        catch_exception(error)
    finally:
        if conn is not None:
            conn.close()
        return evaluation_id


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


# Get topic id from 'master' schema of database
def get_topic_id(subject_code):
    if 'tutoria1' in subject_code.lower():
        topic_name = 'Tutoria 1r CF'
    elif 'tutoria2' in subject_code.lower():
        topic_name = 'Tutoria 2n CF'
    elif 'centre' in subject_code.lower():
        topic_name = 'Centre'
    else:
        topic_name = 'Assignatura'

    sql = "SELECT id FROM master.topic WHERE name = %s;"
    conn = None
    try:
        params = config_master()
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        cursor.execute(sql, (topic_name,))
        topic_id = cursor.fetchone()[0]
        cursor.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        catch_exception(error)
    finally:
        if conn is not None:
            conn.close()
    return topic_id


def save_answer(value, question_id, evaluation_id):
    answer_data = (value, question_id, evaluation_id,)
    sql = """
            INSERT INTO public.forms_answer(value, question_id, evaluation_id)
            VALUES(%s, %s, %s);
          """
    conn = None
    try:
        params = config_public()
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        cursor.execute(sql, answer_data)
        cursor.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        catch_exception(error)
    finally:
        if conn is not None:
            conn.close()
        return evaluation_id


def succeed():
    print('\033[92m' + 'OK' + '\033[0m')


def catch_exception(e):    
    print(str(e))
    print(traceback.format_exc())    
    sys.exit()