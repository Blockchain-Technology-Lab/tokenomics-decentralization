from math import log


def compute_tau(balance_distribution, threshold):
    tau_index, tau_market_share = 0, 0
    circulation = sum(balance_distribution)

    for balance in balance_distribution:
        market_share = balance / circulation
        if tau_market_share >= threshold:
            break
        tau_index += 1
        tau_market_share += market_share
    return tau_index, tau_market_share


def compute_gini(balance_distribution):
    parsed_entries = 0
    circulation = sum(balance_distribution)
    population = len(balance_distribution)
    gini = 1
    for balance in balance_distribution:
        richer_population_percentage = parsed_entries / population
        market_share = balance / circulation
        gini -= market_share * ((1 / population) + (2 * richer_population_percentage))
        parsed_entries += 1

    return gini


def compute_hhi(balance_distribution):
    circulation = sum(balance_distribution)
    hhi = 0
    for balance in balance_distribution:
        market_share = balance / circulation * 100
        hhi += market_share**2

    return hhi


def compute_shannon_entropy(balance_distribution):
    circulation = sum(balance_distribution)
    entropy = 0
    for balance in balance_distribution:
        market_share = balance / circulation
        if market_share > 0:
            entropy -= market_share * log(market_share, 2)

    return entropy


def compute_total_entities(balance_distribution):
    return len(balance_distribution)
