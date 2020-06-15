# Quantum Annealing using DWave

## Installation

The simplest way to start is to install dwave-ocean-sdk for the full suite of Ocean tools.

* Install the SDK using pip:

    ```bash
    pip install dwave-ocean-sdk
    ```

* The interactive dwave setup and dwave install commands of the the dwave-ocean-sdk step you through installation of non-open-source (“contrib”) tools.

    ```bash
    $ dwave setup

    Optionally install non-open-source packages and configure your environment.

    Do you want to select non-open-source packages to install (y/n)? [y]: n

    $ dwave install --help
    Usage: dwave install [OPTIONS] [PACKAGES]...

    Install optional non-open-source Ocean packages.

    Options:
    -l, --list     List available contrib (non-OSS) packages
    -a, --all      Install all contrib (non-OSS) packages
    -v, --verbose  Increase output verbosity
    --help         Show this message and exit.
    ```

* Setup access for D-Wave compute resources:

    ```bash
    $ dwave config create
    Configuration file not found; the default location is: /home/jane/.config/dwave/dwave.conf
    Confirm configuration file path [/home/jane/.config/dwave/dwave.conf]:
    Profile (create new) [prod]:
    API endpoint URL [skip]:
    Authentication token [skip]: ABC-1234567890abcdef1234567890abcdef
    Default client class (qpu or sw) [qpu]:
    Default solver [skip]:
    Configuration saved.
    ```

## Execute

* Change to the relevant working directory:

    ```bash
    $ cd knapsack
    ```

* Run the file:

    ```bash
    $ python knapsack.py
       0  1  2 energy num_oc. chain_.
    0  1  0  1 -108.0       8     0.0
    1  1  1  0 -106.0       1     0.0
    2  0  1  1 -104.0       1     0.0
    ['BINARY', 3 rows, 10 samples, 3 variables]
    ```
