import time
from random import randint

import numpy as np
import pandas as pd
import psycopg2
from psycopg2 import connect, Error
from psycopg2.extras import execute_values
from contextlib import closing
from tqdm import tqdm, trange

credentials_list = [{"type": "local", "dbname": "grid-task",
                     "host": "localhost", "port": 5433,
                     "user": "test", "password": "test"},
                    {"type": "docker", "dbname": "grid-task",
                     "host": "localhost", "port": 6543,
                     "user": "test", "password": "test"},
                    {"type": "cloud", "dbname": "grid-task",
                     "host": "HIDDEN", "port": 5432,
                     "user": "test", "password": "test"}]

table_name = '"test-table"'


def shell(conn, fun):
    msg = None
    with conn.cursor() as cursor:
        try:
            ret_val = fun(cursor)
        except (Exception, Error) as error:
            ret_val = -1
            msg = error
        finally:
            cursor.close()
    return ret_val, msg


def insert(conn, _=None):
    def _insert(cursor):
        number_of_rows = 1000
        data = [(i, randint(-128, 127), f"Just a text with i={i}") for i in range(number_of_rows)]
        insert_query = f'INSERT INTO {table_name} VALUES %s;'
        execute_values(cursor, insert_query, data)
        conn.commit()
        return 0

    return shell(conn, _insert)


def select(conn, cond=''):
    def _select(cursor):
        cursor.execute(f'SELECT * FROM {table_name} as t {cond};')
        rows = cursor.fetchall()
        return len(rows)

    return shell(conn, _select)


def clear(conn, _=None):
    # noinspection SqlWithoutWhere
    def _clear(cursor):
        cursor.execute(f'DELETE FROM {table_name};')
        conn.commit()
        return 0

    return shell(conn, _clear)


def main():
    number_of_tests = 100
    operations_list = ["INSERTING", "SELECTING BY CONDITION", "SELECTING ALL", "CLEARING"]
    functions_list = [insert, select, select, clear]
    args_list = [[], ['WHERE t.integer > 120'], [], []]

    results = np.zeros((len(credentials_list), len(operations_list)))

    for i, credentials in tqdm(enumerate(credentials_list), leave=False, total=len(credentials_list)):
        try:
            with closing(connect(dbname=credentials["dbname"],
                                 user=credentials["user"], password=credentials["password"],
                                 host=credentials["host"], port=credentials["port"])) as conn:
                rows_in_db_before_start, err = select(conn, "")
                if rows_in_db_before_start == -1:
                    print(f"\nFailed to execute operation SELECTING ALL before start: {err}")
                    return
                elif rows_in_db_before_start > 0:
                    ret_val, err = clear(conn)
                    if ret_val != 0:
                        print(f"\nFailed to execute operation CLEARING before start: {err}")
                        return

                for _ in trange(number_of_tests, leave=False):
                    for j, (operation, fun, args) in enumerate(zip(operations_list, functions_list, args_list)):
                        start = time.time()
                        ret_val, err = fun(conn, *args)
                        if ret_val == -1:
                            print(f"\nFailed to execute operation {operation}: {err}")
                            return
                        end = time.time()
                        results[i][j] += end - start
                conn.close()
        except psycopg2.OperationalError:
            print(f"\nCannot connect to {credentials['type']} server! Abort execution...")
            return
        except Exception as e:
            print(f"\nError: {e}")
            return
    fun = np.vectorize(lambda x: f"{round(x, 3)} sec.")
    df = pd.DataFrame(fun(results), columns=operations_list, index=[x["type"] for x in credentials_list])
    print(df)


if __name__ == "__main__":
    main()
