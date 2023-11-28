from tokenomics_decentralization.analyze import get_output_row, analyze_snapshot, analyze
import pathlib


def test_get_output_row(mocker):
    get_metrics_mock = mocker.patch('tokenomics_decentralization.helper.get_metrics')
    get_metrics_mock.return_value = ['hhi', 'gini']

    get_no_clustering_mock = mocker.patch('tokenomics_decentralization.helper.get_no_clustering_flag')
    get_exclude_contracts_mock = mocker.patch('tokenomics_decentralization.helper.get_exclude_contracts_flag')
    get_exclude_below_fees_mock = mocker.patch('tokenomics_decentralization.helper.get_exclude_below_fees_flag')
    get_top_limit_type_mock = mocker.patch('tokenomics_decentralization.helper.get_top_limit_type')
    get_top_limit_value_mock = mocker.patch('tokenomics_decentralization.helper.get_top_limit_value')

    get_no_clustering_mock.return_value = False
    get_exclude_contracts_mock.return_value = False
    get_exclude_below_fees_mock.return_value = False
    get_top_limit_type_mock.return_value = 'absolute'
    get_top_limit_value_mock.return_value = 0

    metrics = {'hhi': 1, 'gini': 0}
    csv_row = get_output_row('bitcoin', '2010-01-01', metrics)
    assert csv_row == ['bitcoin', '2010-01-01', False, False, 'absolute', 0, False, 1, 0]

    get_no_clustering_mock.return_value = True
    metrics = {'non-clustered hhi': 1, 'non-clustered gini': 0}
    csv_row = get_output_row('bitcoin', '2010-01-01', metrics)
    assert csv_row == ['bitcoin', '2010-01-01', True, False, 'absolute', 0, False, 1, 0]

    get_exclude_contracts_mock.return_value = True
    metrics = {'exclude_contracts non-clustered hhi': 1, 'exclude_contracts non-clustered gini': 0}
    csv_row = get_output_row('bitcoin', '2010-01-01', metrics)
    assert csv_row == ['bitcoin', '2010-01-01', True, True, 'absolute', 0, False, 1, 0]

    get_top_limit_value_mock.return_value = 1
    metrics = {'top-1_absolute exclude_contracts non-clustered hhi': 1, 'top-1_absolute exclude_contracts non-clustered gini': 0}
    csv_row = get_output_row('bitcoin', '2010-01-01', metrics)
    assert csv_row == ['bitcoin', '2010-01-01', True, True, 'absolute', 1, False, 1, 0]

    get_exclude_below_fees_mock.return_value = True
    get_top_limit_value_mock.return_value = 1
    metrics = {'top-1_absolute exclude_below_fees exclude_contracts non-clustered hhi': 1, 'top-1_absolute exclude_below_fees exclude_contracts non-clustered gini': 0}
    csv_row = get_output_row('bitcoin', '2010-01-01', metrics)
    assert csv_row == ['bitcoin', '2010-01-01', True, True, 'absolute', 1, True, 1, 0]


def test_analyze_snapshot(mocker):
    get_force_analyze_mock = mocker.patch('tokenomics_decentralization.helper.get_force_analyze_flag')
    get_no_clustering_mock = mocker.patch('tokenomics_decentralization.helper.get_no_clustering_flag')
    get_exclude_contracts_mock = mocker.patch('tokenomics_decentralization.helper.get_exclude_contracts_flag')
    get_exclude_below_fees_mock = mocker.patch('tokenomics_decentralization.helper.get_exclude_below_fees_flag')
    get_median_tx_fee_mock = mocker.patch('tokenomics_decentralization.helper.get_median_tx_fee')
    get_top_limit_type_mock = mocker.patch('tokenomics_decentralization.helper.get_top_limit_type')
    get_top_limit_value_mock = mocker.patch('tokenomics_decentralization.helper.get_top_limit_value')
    get_metrics_mock = mocker.patch('tokenomics_decentralization.helper.get_metrics')
    get_snapshot_info_mock = mocker.patch('tokenomics_decentralization.db_helper.get_snapshot_info')
    get_metric_value_mock = mocker.patch('tokenomics_decentralization.db_helper.get_metric_value')
    get_clustered_entries_mock = mocker.patch('tokenomics_decentralization.db_helper.get_balance_entries')
    get_nonclustered_entries_mock = mocker.patch('tokenomics_decentralization.db_helper.get_non_clustered_balance_entries')
    db_insert_mock = mocker.patch('tokenomics_decentralization.db_helper.insert_metric')
    db_commit_mock = mocker.patch('tokenomics_decentralization.db_helper.commit_database')

    get_force_analyze_mock.return_value = False
    get_no_clustering_mock.return_value = False
    get_exclude_contracts_mock.return_value = False
    get_exclude_below_fees_mock.return_value = False
    get_median_tx_fee_mock.return_value = 0
    get_top_limit_type_mock.return_value = 'absolute'
    get_top_limit_value_mock.return_value = 0

    get_snapshot_info_mock .return_value = [1, 1, '2010-01-01', 8]

    get_metrics_mock.return_value = ['hhi']

    get_metric_value_mock.return_value = [1]

    output = analyze_snapshot(None, 'bitcoin', '2010-01-01')
    assert output == {'hhi': 1}

    get_no_clustering_mock.return_value = True
    get_exclude_contracts_mock.return_value = True
    get_exclude_below_fees_mock.return_value = True
    get_top_limit_type_mock.return_value = 'absolute'
    get_top_limit_value_mock.return_value = 1

    output = analyze_snapshot(None, 'bitcoin', '2010-01-01')
    assert output == {'top-1_absolute exclude_below_fees exclude_contracts non-clustered hhi': 1}

    get_clustered_entries_mock.return_value = [['entity', 4], ['entity 2', 4]]
    get_nonclustered_entries_mock.return_value = [['address', 4], ['address 2', 4]]

    get_force_analyze_mock.return_value = True

    db_insert_mock.return_value = None
    db_commit_mock.return_value = None

    output = analyze_snapshot(None, 'bitcoin', '2010-01-01')
    assert output == {'top-1_absolute exclude_below_fees exclude_contracts non-clustered hhi': 10000}

    get_no_clustering_mock.return_value = False

    output = analyze_snapshot(None, 'bitcoin', '2010-01-01')
    assert output == {'top-1_absolute exclude_below_fees exclude_contracts hhi': 10000}

    get_top_limit_value_mock.return_value = 0

    output = analyze_snapshot(None, 'bitcoin', '2010-01-01')
    assert output == {'exclude_below_fees exclude_contracts hhi': 5000}

    get_top_limit_type_mock.return_value = 'percentage'
    get_top_limit_value_mock.return_value = 0.5

    output = analyze_snapshot(None, 'bitcoin', '2010-01-01')
    assert output == {'top-0.5_percentage exclude_below_fees exclude_contracts hhi': 10000}

    get_top_limit_value_mock.return_value = 0
    get_metrics_mock.return_value = ['tau=0.5']

    output = analyze_snapshot(None, 'bitcoin', '2010-01-01')
    assert output == {'exclude_below_fees exclude_contracts tau=0.5': 1}


def test_analyze(mocker):
    get_output_directories_mock = mocker.patch('tokenomics_decentralization.helper.get_output_directories')
    get_output_directories_mock.return_value = [pathlib.Path(__file__).resolve()]

    is_file_mock = mocker.patch('os.path.isfile')
    is_file_mock.return_value = True

    get_db_connector_mock = mocker.patch('tokenomics_decentralization.schema.get_connector')
    get_db_connector_mock.return_value = None

    analyze_snapshot_mock = mocker.patch('tokenomics_decentralization.analyze.analyze_snapshot')
    analyze_snapshot_mock.return_value = {'hhi': 1}

    write_csv_output_mock = mocker.patch('tokenomics_decentralization.analyze.write_csv_output')
    write_csv_output_mock.return_value = None

    get_output_row_mock = mocker.patch('tokenomics_decentralization.analyze.get_output_row')
    get_output_row_mock.return_value = 'row'

    output_rows = analyze(['bitcoin'], ['2010-01-01'])
    assert output_rows == ['row']
    analyze_snapshot_mock.assert_called_with(None, 'bitcoin', '2010-01-01')

    output_rows = analyze(['bitcoin', 'ethereum'], ['2010-01-01', '2011-01-01'])
    assert output_rows == ['row', 'row', 'row', 'row']

    is_file_mock.return_value = False
    output_rows = analyze(['bitcoin', 'ethereum'], ['2010-01-01', '2011-01-01'])
    assert output_rows == []
