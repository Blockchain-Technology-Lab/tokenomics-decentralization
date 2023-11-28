from tokenomics_decentralization.map import fill_db_with_addresses, apply_mapping
from unittest.mock import call
import pathlib


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


def test_apply_mapping(mocker):
    get_db_connector_mock = mocker.patch('tokenomics_decentralization.map.get_connector')
    get_db_connector_mock.return_value = 'connector'

    fill_db_with_addresses_mock = mocker.patch('tokenomics_decentralization.map.fill_db_with_addresses')
    fill_db_with_balances_mock = mocker.patch('tokenomics_decentralization.map.fill_db_with_balances')

    get_force_map_addresses_mock = mocker.patch('tokenomics_decentralization.helper.get_force_map_addresses_flag')
    get_force_map_balances_mock = mocker.patch('tokenomics_decentralization.helper.get_force_map_balances_flag')

    get_output_directories_mock = mocker.patch('tokenomics_decentralization.helper.get_output_directories')
    get_input_directories_mock = mocker.patch('tokenomics_decentralization.helper.get_input_directories')

    os_isfile_mock = mocker.patch('os.path.isfile')
    os_isfile_mock.side_effect = {
        pathlib.Path('/output').resolve() / 'bitcoin_2010-01-01.db': False,
        pathlib.Path('/input1').resolve() / 'bitcoin_2010-01-01_raw_data.csv': False,
        pathlib.Path('/input2').resolve() / 'bitcoin_2010-01-01_raw_data.csv': False,
    }.get

    get_force_map_addresses_mock.return_value = False
    get_force_map_balances_mock.return_value = False

    get_output_directories_mock.return_value = [pathlib.Path('/output').resolve()]
    get_input_directories_mock.return_value = [pathlib.Path('/input1').resolve(), pathlib.Path('/input2').resolve()]

    apply_mapping('bitcoin', '2010-01-01')
    assert get_db_connector_mock.call_args_list == []
    assert fill_db_with_addresses_mock.call_args_list == []
    assert fill_db_with_balances_mock.call_args_list == []

    os_isfile_mock.side_effect = {
        pathlib.Path('/output').resolve() / 'bitcoin_2010-01-01.db': True,
    }.get
    get_input_directories_mock.reset_mock()

    apply_mapping('bitcoin', '2010-01-01')
    assert get_input_directories_mock.call_args_list == []
    assert fill_db_with_addresses_mock.call_args_list == []
    assert fill_db_with_balances_mock.call_args_list == []

    get_force_map_addresses_mock.return_value = True
    get_force_map_balances_mock.return_value = True

    apply_mapping('bitcoin', '2010-01-01')
    assert fill_db_with_addresses_mock.call_args_list == [call('connector', 'bitcoin')]
    assert fill_db_with_balances_mock.call_args_list == [call('connector', 'bitcoin', '2010-01-01')]

    os_isfile_mock.side_effect = {
        pathlib.Path('/output').resolve() / 'bitcoin_2010-01-01.db': False,
        pathlib.Path('/input1').resolve() / 'bitcoin_2010-01-01_raw_data.csv': True
    }.get

    get_force_map_addresses_mock.return_value = False
    get_force_map_balances_mock.return_value = False
    get_input_directories_mock.reset_mock()
    fill_db_with_addresses_mock.reset_mock()
    fill_db_with_balances_mock.reset_mock()

    apply_mapping('bitcoin', '2010-01-01')
    assert get_input_directories_mock.call_args_list == [call()]
    assert fill_db_with_addresses_mock.call_args_list == [call('connector', 'bitcoin')]
    assert fill_db_with_balances_mock.call_args_list == [call('connector', 'bitcoin', '2010-01-01')]
