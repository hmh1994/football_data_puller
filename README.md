# Football Data Puller

This is a Python script that pulls football data from the web and stores it into the PostgresSQL database.
The script is designed to be run on regular cycles (e.g. every 5 minutes) to keep the database up to date.

## Table of Contents

- [Football Data Puller](#football-data-puller)
    - [Table of Contents](#table-of-contents)
    - [Contributing](#contributing)
        - [Prerequisites](#prerequisites)
        - [Installation](#installation)
        - [Testing](#testing)
        - [Contribution Guidelines](#contribution-guidelines)
    - [About](#about)

## Contributing

If you would like to contribute to this project, please follow the steps below:

### Prerequisites

- [Git](https://git-scm.com/)
- [Python 3.12](https://www.python.org/downloads/)

### Installation

#### 1. Clone the repository

```bash
$ git clone git@github.com:hmh1994/football_data_puller.git
```

#### 2. Set up the virtual environment

```bash
$ python3.12 -m venv venv
$ source venv/bin/activate
```

#### 3. Install the dependencies

```bash
(venv) $ pip install -e ".[all]"
```

### Testing

To run the tests, use the following command:

```bash
(venv) $ pytest -vv
```

### Contribution Guidelines

See [CONTRIBUTION.md](docs/CONTRIBUTION.md) for more information on how to contribute to this project.

## About

This project is authored and maintained by [@jormal](https://github.com/jormal).
