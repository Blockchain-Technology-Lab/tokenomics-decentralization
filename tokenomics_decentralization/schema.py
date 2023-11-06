import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        create_tables(conn)
    except Error as e:
        print(e)
    return conn


def create_tables(conn):
    create_ledger = '''
    CREATE TABLE IF NOT EXISTS ledgers (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    );
    '''

    create_entity = '''
    CREATE TABLE IF NOT EXISTS entities (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        ledger_id INTEGER,
        FOREIGN KEY (ledger_id) REFERENCES ledgers (id),
        CONSTRAINT U_Entity UNIQUE (name, ledger_id)
    );
    '''

    create_address = '''
    CREATE TABLE IF NOT EXISTS addresses (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        ledger_id INTEGER,
        entity_id INTEGER,
        FOREIGN KEY (ledger_id) REFERENCES ledgers (id),
        FOREIGN KEY (entity_id) REFERENCES entities (id),
        CONSTRAINT U_Address UNIQUE (name, ledger_id)
    );
    '''

    create_snapshot = '''
    CREATE TABLE IF NOT EXISTS snapshots (
        id INTEGER PRIMARY KEY,
        name DATETIME NOT NULL,
        ledger_id INTEGER NOT NULL,
        circulation TEXT,
        FOREIGN KEY (ledger_id) REFERENCES ledgers (id),
        CONSTRAINT U_Snapshot UNIQUE (ledger_id, name)
    );
    '''

    create_balance = '''
    CREATE TABLE IF NOT EXISTS balances (
        id INTEGER PRIMARY KEY,
        balance INTEGER,
        snapshot_id INTEGER NOT NULL,
        address_id INTEGER NOT NULL,
        FOREIGN KEY (address_id) REFERENCES addresses (id),
        FOREIGN KEY (snapshot_id) REFERENCES snapshots (id),
        CONSTRAINT U_Balance UNIQUE (address_id, snapshot_id)
    );
    '''

    create_metrics = '''
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        value FLOAT,
        snapshot_id INTEGER NOT NULL,
        FOREIGN KEY (snapshot_id) REFERENCES snapshots (id),
        CONSTRAINT U_Balance UNIQUE (name, snapshot_id)
    );
    '''

    c = conn.cursor()

    for query in [create_ledger, create_entity, create_address, create_snapshot, create_balance, create_metrics]:
        try:
            c.execute(query)
        except Error as e:
            print(e)


def get_connector(db_filename):
    return create_connection(db_filename)
