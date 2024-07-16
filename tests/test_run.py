import run
from unittest.mock import call


def test_run(mocker):
    apply_mapping_mock = mocker.patch('run.apply_mapping')
    analyze_mock = mocker.patch('run.analyze')
    plot_mock = mocker.patch('run.plot')
    get_plot_flag_mock = mocker.patch('tokenomics_decentralization.helper.get_plot_flag')

    get_plot_flag_mock.return_value = False

    mapping_calls = []
    analyze_calls = []

    run.main(['bitcoin'], ['2010-01-01'])
    mapping_calls.append(call('bitcoin'))
    assert apply_mapping_mock.call_args_list == mapping_calls
    analyze_calls.append(call(['bitcoin'], ['2010-01-01']))
    assert analyze_mock.call_args_list == analyze_calls

    run.main(['bitcoin', 'ethereum'], ['2010-01-01', '2020-01-01'])
    mapping_calls.append(call('bitcoin'))
    mapping_calls.append(call('ethereum'))
    assert apply_mapping_mock.call_args_list == mapping_calls
    analyze_calls.append(call(['bitcoin', 'ethereum'], ['2010-01-01', '2020-01-01']))
    assert analyze_mock.call_args_list == analyze_calls

    get_plot_flag_mock.return_value = True
    run.main(['bitcoin'], ['2010-01-01'])
    plot_mock.assert_called()
