# Quantum Circuits using pyQuil

## Installation

Python 3.6+ is recommended.

* Install pyQuil using pip:

    ```bash
    pip install pyquil
    ```

* Downloading the QVM and Compiler:

    The Forest 2.0 Downloadable SDK Preview currently contains:

    * The Rigetti Quantum Virtual Machine (qvm) which allows high-performance simulation of Quil programs

    * The Rigetti Quil Compiler (quilc) which allows compilation and optimization of Quil programs to native gate sets

    Download the Forest SDK from <https://qcs.rigetti.com/sdk-downloads>, where you can find links for Windows, macOS, Linux (.deb), Linux (.rpm), and Linux (bare-bones).

    For further instructions on this step go to <http://docs.rigetti.com/en/stable/start.html#downloading-the-qvm-and-compiler>

* Run the QVM and Compile in server mode:

    ```bash
    ### CONSOLE 1
    $ qvm -S

    Welcome to the Rigetti QVM
    (Configured with 10240 MiB of workspace and 8 workers.)
    [2018-09-20 15:39:50] Starting server on port 5000.


    ### CONSOLE 2
    $ quilc -S

    ... - Launching quilc.
    ... - Spawning server at (tcp://*:5555) .
    ```

## Execute

* Change to the relevant directory:

    ```bash
    $ cd shors_algorithm/shor
    ```

* Run the file:

    ```bash
    $ python shor.py 25
    Factoring 25
    y: 13
    c: 307; r: 10
    factor: 18
    f1: 1; f2: 1
    trivial factor, continuing
    y: 7
    c: 0; r: 1
    r odd; continuing
    ...
    ...
    ...
    y: 19
    c: 607; r: 22
    factor: 19
    f1: 1; f2: 5
    Factorization: (5, 5)
    ```
