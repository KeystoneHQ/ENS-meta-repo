import os
import sqlite3
from google.cloud import bigquery
from eth_utils import to_checksum_address


def query_ENS():
    client = bigquery.Client()
    query_job = client.query(
        """
        select * from ens-manager.names.reverse_records
        """
    )

    return query_job.result()  # Waits for job to complete.

def create_contracts_table(DB):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    try:
        create_table = '''create table ENS(
                                           id INTEGER PRIMARY KEY NOT NULL,
                                           addr VARCHAR(50) NOT NULL,
                                           name VARCHAR(50))'''

        sql_create_addr_index = "create index addr_index on ENS(addr)"
        cursor.execute(create_table)
        cursor.execute(sql_create_addr_index)
    except:
        clean_table = "DELETE FROM ENS"
        cursor.execute(clean_table)

    cursor.close()
    conn.commit()
    conn.close()


def get_ENS_to_sqlite(DB):
    create_contracts_table(DB)
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    ENS_list = query_ENS()
    for ENS in ENS_list:
        sql_insert_info = "insert into ENS (addr,name) values (?,?)"
        cursor.execute(sql_insert_info, (ENS.addr , ENS.name))
#         cursor.execute(sql_insert_info, (to_checksum_address(ENS.addr), ENS.name))

    cursor.close()
    conn.commit()
    conn.close()


if __name__ == "__main__":
    if not os.path.exists("./outputs/ENS/"):
        os.makedirs("./outputs/ENS/")
    get_ENS_to_sqlite(DB="./outputs/ENS/ENS.db")
