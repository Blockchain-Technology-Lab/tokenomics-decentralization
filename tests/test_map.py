from tokenomics_decentralization.map import apply_mapping
from unittest.mock import call


def test_apply_mapping(mocker):
    get_db_connector_mock = mocker.patch('tokenomics_decentralization.db_helper.get_connector')
    get_db_connector_mock.return_value = 'connector'
    commit_database_mock = mocker.patch('tokenomics_decentralization.db_helper.commit_database')

    insert_mapping_mock = mocker.patch('tokenomics_decentralization.db_helper.insert_mapping')

    get_clusters_mock = mocker.patch('tokenomics_decentralization.helper.get_clusters')
    get_clusters_mock.return_value = {'entity2': 'cluster'}

    get_active_sources_mock = mocker.patch('tokenomics_decentralization.helper.get_active_sources')
    get_active_sources_mock.return_value = ['test']

    get_db_filename_mock = mocker.patch('tokenomics_decentralization.db_helper.get_db_filename')
    db_filename = 'bitcoin_Test.db'
    get_db_filename_mock.return_value = db_filename

    os_isfile_mock = mocker.patch('os.path.isfile')
    os_isfile_mock.side_effect = {
        db_filename: True
    }.get

    get_force_map_addresses_mock = mocker.patch('tokenomics_decentralization.helper.get_force_map_addresses_flag')

    get_force_map_addresses_mock.return_value = False

    get_db_connector_calls = []
    insert_mapping_calls = []
    commit_db_calls = []

    apply_mapping('bitcoin')
    assert get_db_connector_mock.call_args_list == get_db_connector_calls

    os_isfile_mock.side_effect = {
        db_filename: False
    }.get

    # Test normal mapping insertion
    mocker.patch('builtins.open', mocker.mock_open(read_data='{"name": "entity1", "address": "addr1", "source": "test"}'))

    apply_mapping('bitcoin')
    get_db_connector_calls.append(call(db_filename))
    assert get_db_connector_mock.call_args_list == get_db_connector_calls
    insert_mapping_calls.append(call('connector', 'addr1', 'entity1', False))
    assert insert_mapping_mock.call_args_list == insert_mapping_calls
    commit_db_calls.append(call('connector'))
    assert commit_database_mock.call_args_list == commit_db_calls

    # Test ignoring non-active source
    mocker.patch('builtins.open', mocker.mock_open(read_data='{"name": "entity1", "address": "addr1", "source": "other"}'))

    apply_mapping('bitcoin')
    get_db_connector_calls.append(call(db_filename))
    assert get_db_connector_mock.call_args_list == get_db_connector_calls
    assert insert_mapping_mock.call_args_list == insert_mapping_calls
    commit_db_calls.append(call('connector'))
    assert commit_database_mock.call_args_list == commit_db_calls

    # Test force map flag
    os_isfile_mock.side_effect = {
        db_filename: True
    }.get

    get_force_map_addresses_mock.return_value = True

    apply_mapping('bitcoin')
    get_db_connector_calls.append(call(db_filename))
    assert get_db_connector_mock.call_args_list == get_db_connector_calls
    commit_db_calls.append(call('connector'))
    assert commit_database_mock.call_args_list == commit_db_calls

    # Test cluster
    mocker.patch('builtins.open', mocker.mock_open(read_data='{"name": "entity2", "address": "addr1", "source": "test"}'))

    apply_mapping('bitcoin')
    get_db_connector_calls.append(call(db_filename))
    assert get_db_connector_mock.call_args_list == get_db_connector_calls
    insert_mapping_calls.append(call('connector', 'addr1', 'cluster', False))
    assert insert_mapping_mock.call_args_list == insert_mapping_calls
    commit_db_calls.append(call('connector'))
    assert commit_database_mock.call_args_list == commit_db_calls

    # Test is_contract
    mocker.patch('builtins.open', mocker.mock_open(read_data='{"name": "entity2", "address": "addr1", "source": "test", "is_contract": true}'))

    apply_mapping('bitcoin')
    get_db_connector_calls.append(call(db_filename))
    assert get_db_connector_mock.call_args_list == get_db_connector_calls
    insert_mapping_calls.append(call('connector', 'addr1', 'cluster', True))
    assert insert_mapping_mock.call_args_list == insert_mapping_calls
    commit_db_calls.append(call('connector'))
    assert commit_database_mock.call_args_list == commit_db_calls
