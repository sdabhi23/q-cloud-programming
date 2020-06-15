# Quantum Circuits using Qiskit

## Installation

* Use pip to install qiskit. pip 19 or newer is needed to install qiskit-aer from precompiled binary on Linux.

    ```bash
    pip install qiskit
    ```

* Install other recommended dependencies:

    ```bash
    pip install matplotlib
    pip install ipywidgets
    pip install seaborn
    pip install pygments
    ```

* Access IBM Quantum Systems

    1. Create a free IBM Quantum Experience account.

    1. Navigate to My Account to view your account settings.

        ![account settings](./install_0.png)

    1. Click on Copy token to copy the token to your clipboard. Temporarily paste this API token into your favorite text editor so you can use it later to create an account configuration file.

        ![auth token](./install_1.png)

    1. Run the following commands to store your API token locally for later use in a configuration file called qiskitrc. Replace MY_API_TOKEN with the API token value that you stored in your text editor.

        ```python
        from qiskit import IBMQ
        IBMQ.save_account('MY_API_TOKEN')
        ```

* For executing notebooks created as a part of **IBM Quantum Challenge 2020** you will have to install the `may4_challenge` package:

    ```bash
    pip install -I git+https://github.com/qiskit-community/may4_challenge.git@0.4.30
    ```

## Execute

Open the relevant notebook and execute the cells sequentially.
