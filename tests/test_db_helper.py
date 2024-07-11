import tokenomics_decentralization.helper as hlp
import tokenomics_decentralization.db_helper as db_hlp
import sqlite3
import os
import pytest


@pytest.fixture
def setup_and_cleanup():
    """
    This function can be used to set up the right conditions for a test and also clean up after the test is finished.
    The part before the yield command is run before the test (setup) and the part after the yield command is run
    after (cleanup)
    """
    # Set up
    db_filename = db_hlp.get_db_filename('test')

    yield

    # Clean up
    os.remove(db_filename)


def test_get_db_filename(mocker):
    get_active_source_keywords_mock = mocker.patch("tokenomics_decentralization.helper.get_active_source_keywords")
    get_active_source_keywords_mock.return_value = ['test']

    filename = '_'.join(['bitcoin'] + ['test'])
    db_filename = db_hlp.get_db_filename('bitcoin')
    assert db_filename == hlp.MAPPING_INFO_DIR / f'addresses/{filename}.db'


def test_get_connector(setup_and_cleanup):
    db_filename = db_hlp.get_db_filename('test')
    conn = db_hlp.get_connector(db_filename)
    assert type(conn) is sqlite3.Connection


def test_insert_mapping(setup_and_cleanup):
    db_filename = db_hlp.get_db_filename('test')
    conn = db_hlp.get_connector(db_filename)
    c = conn.cursor()

    db_hlp.insert_mapping(conn, 'a1', 'e1', False)
    db_hlp.commit_database(conn)
    entry = c.execute('SELECT address, entity, is_contract FROM mapping WHERE address=?', ('a1', )).fetchone()
    assert entry == ('a1', 'e1', 0)

    db_hlp.insert_mapping(conn, 'a1', 'e1', False)
    db_hlp.commit_database(conn)
    entry = c.execute('SELECT address, entity, is_contract FROM mapping WHERE address=?', ('a1', )).fetchone()
    assert entry == ('a1', 'e1', 0)

    with pytest.raises(ValueError):
        db_hlp.insert_mapping(conn, 'a1', 'e2', False)


def test_get_address_entity(setup_and_cleanup):
    db_filename = db_hlp.get_db_filename('test')
    conn = db_hlp.get_connector(db_filename)
    db_hlp.insert_mapping(conn, 'a1', 'e1', False)
    db_hlp.commit_database(conn)

    entity = db_hlp.get_address_entity(conn, 'a1')
    assert entity == 'e1'

    entity = db_hlp.get_address_entity(conn, 'blah')
    assert entity == 'blah'
