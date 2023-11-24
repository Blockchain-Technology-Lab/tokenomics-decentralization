from tokenomics_decentralization.analyze import get_output_row


def test_get_output_row(mocker):
    get_metrics_mock = mocker.patch("tokenomics_decentralization.helper.get_metrics")
    get_metrics_mock.return_value = ['hhi', 'gini']

    get_no_clustering_mock = mocker.patch("tokenomics_decentralization.helper.get_no_clustering_flag")
    get_exclude_contracts_mock = mocker.patch("tokenomics_decentralization.helper.get_exclude_contracts_flag")
    get_exclude_below_fees_mock = mocker.patch("tokenomics_decentralization.helper.get_exclude_below_fees_flag")
    get_top_limit_type_mock = mocker.patch("tokenomics_decentralization.helper.get_top_limit_type")
    get_top_limit_value_mock = mocker.patch("tokenomics_decentralization.helper.get_top_limit_value")

    get_no_clustering_mock.return_value = False
    get_exclude_contracts_mock.return_value = False
    get_exclude_below_fees_mock.return_value = False
    get_top_limit_type_mock.return_value = 'absolute'
    get_top_limit_value_mock.return_value = 0

    metrics = {'hhi': 1, 'gini': 0}
    csv_row = get_output_row('bitcoin', '2010-01-01', metrics)
    assert csv_row == ['bitcoin', '2010-01-01', False, False, 'absolute', 0, 1, 0]

    get_no_clustering_mock.return_value = True
    metrics = {'non-clustered hhi': 1, 'non-clustered gini': 0}
    csv_row = get_output_row('bitcoin', '2010-01-01', metrics)
    assert csv_row == ['bitcoin', '2010-01-01', True, False, 'absolute', 0, 1, 0]

    get_exclude_contracts_mock.return_value = True
    metrics = {'exclude_contracts non-clustered hhi': 1, 'exclude_contracts non-clustered gini': 0}
    csv_row = get_output_row('bitcoin', '2010-01-01', metrics)
    assert csv_row == ['bitcoin', '2010-01-01', True, True, 'absolute', 0, 1, 0]

    get_top_limit_value_mock.return_value = 1
    metrics = {'top-1_absolute exclude_contracts non-clustered hhi': 1, 'top-1_absolute exclude_contracts non-clustered gini': 0}
    csv_row = get_output_row('bitcoin', '2010-01-01', metrics)
    assert csv_row == ['bitcoin', '2010-01-01', True, True, 'absolute', 1, 1, 0]
