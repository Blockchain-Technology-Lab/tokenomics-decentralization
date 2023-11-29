import run
from unittest.mock import call


def test_run(mocker):
    apply_mapping_mock = mocker.patch('run.apply_mapping')
    analyze_mock = mocker.patch('run.analyze')
    plot_mock = mocker.patch('run.plot')
    get_plot_flag_mock = mocker.patch('tokenomics_decentralization.helper.get_plot_flag')

    get_plot_flag_mock.return_value = False

    run.main(['bitcoin'], ['2010-01-01'])

    apply_mapping_mock.assert_called_with('bitcoin', '2010-01-01')
    analyze_mock.assert_called_with(['bitcoin'], ['2010-01-01'])

    run.main(['bitcoin', 'ethereum'], ['2010-01-01', '2020-01-01'])
    assert call('bitcoin', '2010-01-01') in apply_mapping_mock.call_args_list
    assert call('bitcoin', '2020-01-01') in apply_mapping_mock.call_args_list
    assert call('ethereum', '2010-01-01') in apply_mapping_mock.call_args_list
    assert call('ethereum', '2020-01-01') in apply_mapping_mock.call_args_list
    analyze_mock.assert_called_with(['bitcoin', 'ethereum'], ['2010-01-01', '2020-01-01'])

    get_plot_flag_mock.return_value = True
    run.main(['bitcoin'], ['2010-01-01'])
    plot_mock.assert_called()
