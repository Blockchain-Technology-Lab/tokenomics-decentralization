from tokenomics_decentralization.map import fill_db_with_addresses
from unittest.mock import call


def test_fill_db_with_addresses(mocker):
    db_insert_ledger_mock = mocker.patch('tokenomics_decentralization.db_helper.insert_ledger')
    db_insert_ledger_mock.return_value = None
    db_insert_entity_mock = mocker.patch('tokenomics_decentralization.db_helper.insert_entity')
    db_insert_entity_mock.return_value = None
    db_insert_update_address_mock = mocker.patch('tokenomics_decentralization.db_helper.insert_update_address')
    db_insert_update_address_mock.return_value = None
    db_commit_mock = mocker.patch('tokenomics_decentralization.db_helper.commit_database')
    db_commit_mock.return_value = None

    json_load_mock = mocker.patch('json.load')

    json_load_mock.return_value = {
        'address 1': {'name': 'Entity Name 1', 'source': 'website'},
        'address 2': {'name': 'Entity Name 2', 'source': 'website', 'is_contract': True},
    }

    fill_db_with_addresses('connector', 'random ledger')
    assert json_load_mock.call_args_list == []
    assert db_insert_entity_mock.call_args_list == []
    assert db_insert_update_address_mock.call_args_list == []
    assert db_commit_mock.call_args_list == []

    fill_db_with_addresses('connector', 'bitcoin')
    db_insert_ledger_mock.assert_called_with('connector', 'bitcoin')
    assert call('connector', 'bitcoin', 'Entity Name 1') in db_insert_entity_mock.call_args_list
    assert call('connector', 'bitcoin', 'Entity Name 2') in db_insert_entity_mock.call_args_list
    assert call('connector', 'bitcoin', 'address 1', 'Entity Name 1', False) in db_insert_update_address_mock.call_args_list
    assert call('connector', 'bitcoin', 'address 2', 'Entity Name 2', True) in db_insert_update_address_mock.call_args_list
    db_commit_mock.assert_called_with()
