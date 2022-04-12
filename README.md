# Metadata

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.9](https://img.shields.io/badge/python-3.9-green?style=for-the-badge)](https://www.python.org/)
![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/pilotdataplatform/metadata/Run%20Docker%20Compose%20Tests/develop?style=for-the-badge)


## About
Manages metadata such as file hierarchy, project and user ownership, names, types, etc.

### Built With
- Python
- FastAPI
- Alembic

## Getting Started

### Prerequisites
- Docker
- Gitlab Package Registry credentials for Poetry installation

### Installation
Run Docker compose with Package Registry credentials.

    PIP_USERNAME=[...] PIP_PASSWORD=[...] docker-compose up

## Usage
Local URLs:
- API service: http://localhost:8000
- API documentation: http://localhost:8000/v1/api-doc
- pgAdmin: http://localhost:8750

pgAdmin's local config files have been committed to this repo for ease of development. Without the files, a connection between pgAdmin and Postgres will have to be manually established by the developer.
