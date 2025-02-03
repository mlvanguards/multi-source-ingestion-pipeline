# Multi-source Ingestion Pipeline
## A Scalable Pipeline for Extracting and Processing data

### Overview
This repository provides a robust, scalable solution for ingesting and processing data from various sources. Built with a modular pipeline architecture, it enables efficient data extraction, transformation, and loading of Jira issues for various applications such as analytics, reporting, and data migrations.

## Table of Contents
- [What is the Multi-source Ingestion Pipeline?](#what-is-the-multi-source-ingestion-pipeline)
- [Key Features](#key-features)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [Local Development](#local-development)
  - [Configuration](#configuration)
- [Pipeline Architecture](#pipeline-architecture)
- [Usage Examples](#usage-examples)
- [Contributing](#contributing)
- [License](#license)

## What is the Multi-source Ingestion Pipeline?
The Multi-source Ingestion Pipeline is a Python-based system designed to efficiently extract and process data using an event-driven architecture. It leverages Ray for distributed processing and implements a modular pipeline pattern for extensibility and maintainability.

### Key Features:
- Modular pipeline architecture for flexible data processing
- Distributed processing using Ray
- Comprehensive error handling and logging
- Automatic pagination for large datasets
- Configurable authentication and API settings
- Extensible design for custom processing steps

## Prerequisites
Before using this repository, ensure you have:
- Python 3.8 or higher
- Atlassian account with API access
- Jira instance (Cloud or Server)
- Ray distributed computing framework
- Required Python packages (see requirements.txt)

## Setup Instructions

### Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/jira-ingestion.git
   cd jira-ingestion
   ```
2. Install Poetry (if not already installed)
    ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
3. Install dependencies
    ```bash
   make install
   ```

4. Create .env and add variables \
 ``ATLASSIAN_DOMAIN = "your-company.atlassian.net"
    ATLASSIAN_EMAIL = "your-email@company.com"
    ATLASSIAN_API_TOKEN = "your-api-token"``

5. Activate the virtual environment
    ```bash
   make shell
    ```
6. Run the pipeline

    ```bash
   make run
   ```



