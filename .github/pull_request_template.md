All Submissions:

* [ ] Have you followed the guidelines in our [Contributing documentation](https://blockchain-technology-lab.github.io/tokenomics-decentralization/contribute)?
* [ ] Have you verified that there aren't any other open Pull Requests for the same update/change?
* [ ] Does the Pull Request pass all tests?

# Description

/* Add a short description of your Pull Request */

## Checklist

/* Keep from below the appropriate checklist for your Pull Request and remove the others */

### New Ledger Support Submissions:

- What mapping information did you add for the new ledger?
  - [ ] addresses
  - [ ] special addresses
- [ ] Did you add the new ledger to `config.yaml`?
- [ ] Did you document the added ledger in the documentation pages?


### Update Mapping Support Information Submissions:

- For which ledger do you update the mapping information?
  - [ ] /* ledger name */
- What mapping information do you update?
  - [ ] addresses
  - [ ] special addresses

### New Metric Support Submissions:

- [ ] Did you create a function named `compute_{metric name}` in `tokenomics_decentralization/metrics.py`?
- [ ] Did you import the metric's function to `tokenomics_decentralization/analyze.py` and added it in the `compute_functions` dictionary?
- [ ] Did you add the new metric to `config.yaml`?
- [ ] Did you write unit tests for the new metric?
- [ ] Did you document the new metric in the documentation pages?
