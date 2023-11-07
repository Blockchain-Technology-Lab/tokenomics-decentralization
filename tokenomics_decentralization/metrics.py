from math import log


def compute_tau(entries, circulation, threshold):
    tau_index, tau_market_share = 0, 0

    for entry in entries:
        market_share = int(entry[1]) / circulation
        if tau_market_share >= threshold:
            break
        tau_index += 1
        tau_market_share += market_share
    return tau_index, tau_market_share


def compute_gini(entries, circulation):
    parsed_entries = 0
    population = len(entries)
    gini = 1
    for entry in entries:
        richer_population_percentage = parsed_entries / population
        market_share = int(entry[1]) / circulation
        gini -= market_share * ((1 / population) + (2 * richer_population_percentage))
        parsed_entries += 1

    return gini


def compute_hhi(entries, circulation):
    hhi = 0
    for entry in entries:
        market_share = int(entry[1]) / circulation * 100
        hhi += market_share**2

    return hhi


def compute_shannon_entropy(entries, circulation):
    entropy = 0
    for entry in entries:
        market_share = int(entry[1]) / circulation
        if market_share > 0:
            entropy -= market_share * log(market_share, 2)

    return entropy


def compute_total_entities(entries, circulation):
    return len(entries)
