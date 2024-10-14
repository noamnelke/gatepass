# GatePass

GatePass is a project designed to manage and streamline the process of granting access permissions. This README provides an overview of the project, setup instructions, and usage guidelines.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

GatePass aims to simplify the management of access permissions by providing a user-friendly interface and robust backend support.

## Features

- User authentication and authorization
- Role-based access control
- Audit logs for tracking access events
- API for integration with other systems

## Installation

To install GatePass, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/noamnelke/gatepass.git
    ```
2. Navigate to the project directory:
    ```sh
    cd gatepass
    ```
3. Install dependencies:
    ```sh
    # Create a virtual environment
    python -m venv venv

    # Activate the virtual environment
    # On Windows
    venv\\Scripts\\activate
    # On Unix or MacOS
    source venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt
    ```

## SSL Setup for Development

Browsers block passkeys for websites that don't use SSL. To work around this for development purposes, follow these steps:
1. Add the following line to your `/etc/hosts` file:
    ```
    127.0.0.1	gatepass.local
    ```

2. Generate a self-signed certificate, by running:
    ```sh
    openssl req -x509 -nodes -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -config openssl.cnf
    ```

3. Add this certificate to your local keychain and trust it. On a mac, you open Keychain Access, click on the System keychain and then navigate to Certificates. You drag the certificate generated in the previous step (`cert.pem`) to the list, double click it, expand Trust and select Always Trust.

## Usage

To start the application, run:
```sh
flask run
```

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.