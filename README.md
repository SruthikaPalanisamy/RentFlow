### rentflow

Equipment renting app

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch version-16
bench install-app rentflow
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/rentflow
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade
### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit

###  In README_internals.md: rename a test Yard Staff record. Does handled_by on linked Rental Bookings update automatically? Why or why not?

Yes — handled_by field on  Rental Bookings update automatically, and  don't need any change in this app.

When I rename a Yard Staff record, Frappe's core rename logic checks the schema for every DocType with a Link field pointing at Yard Staff — and runs an UPDATE on each of those doctypes, changing the old name to the new one. This happens automatically, for any Link field on any DocType.