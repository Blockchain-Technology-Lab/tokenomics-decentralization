import sqlite3
import tokenomics_decentralization.helper as hlp


def create_tables(conn):
    c = conn.cursor()

    create_mapping = '''
    CREATE TABLE IF NOT EXISTS mapping (
        id INTEGER PRIMARY KEY,
        address TEXT NOT NULL UNIQUE,
        entity TEXT NOT NULL,
        is_contract BIT DEFAULT 0
    );
    '''
    c.execute(create_mapping)


def get_db_filename(ledger):
    db_filename = '_'.join([ledger] + sorted(hlp.get_active_source_keywords()))
    return hlp.MAPPING_INFO_DIR / f'addresses/{db_filename}.db'


def get_connector(db_filename):
    conn = sqlite3.connect(db_filename)

    create_tables(conn)

    return conn


def commit_database(conn):
    conn.commit()


def insert_mapping(conn, address, entity, is_contract):
    c = conn.cursor()
    try:
        c.execute('INSERT INTO mapping(address, entity, is_contract) VALUES (?, ?, ?)', (address, entity, is_contract))
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in str(e):
            existing_entity = get_address_entity(conn, address)
            if existing_entity == entity:
                pass
            else:
                raise ValueError(f'Same address {address} associated with two entities: {entity} and {existing_entity}')
        else:
            raise e


def get_address_entity(conn, address):
    c = conn.cursor()
    entry = c.execute('SELECT entity FROM mapping WHERE address=?', (address, )).fetchone()
    if entry is not None:
        return entry[0]
    return address
