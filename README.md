# My Uvicorn App

This is a simple web application built using FastAPI and Uvicorn. It serves as a template for creating RESTful APIs with Python.

## Project Structure

```
my-uvicorn-app
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── api
│   │   ├── __init__.py
│   │   └── routes.py
│   └── core
│       └── config.py
├── tests
│   └── test_main.py
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .gitignore
├── Dockerfile
└── README.md
```

## Requirements

To run this application, you need to have Python 3.7 or higher installed. The required packages are listed in `requirements.txt`.

## Installation

1. Clone the repository:

   ```
   git clone <repository-url>
   cd my-uvicorn-app
   ```

2. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

3. (Optional) Copy the `.env.example` to `.env` and configure your environment variables.

## Running the Application

You can run the server using either Poetry (recommended if you use `pyproject.toml`) or pip.

- Using Poetry (recommended):

```bash
poetry install        # install dependencies from pyproject.toml
poetry run start      # uses the `start` script (runs uvicorn with --reload)
```

- Using pip/requirements.txt:

```bash
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Both options will start the application in development mode with hot-reloading.

> Note: The API router is mounted at `/api`. If you're running the frontend (Next.js) in dev, a local proxy is configured to forward `/api` to this backend for convenience.

## Testing

Run tests either from the Poetry environment or with pytest installed in your venv:

- With Poetry:

```bash
poetry run pytest -q
```

- With pip (install test deps first):

```bash
python -m pip install pytest httpx
pytest -q
```

This repository includes a simple test for the root endpoint in `tests/test_main.py`.

## Docker

To build and run the application in a Docker container, use the following commands:

1. Build the Docker image:

   ```
   docker build -t my-uvicorn-app .
   ```

2. Run the Docker container:
   ```
   docker run -p 8000:8000 my-uvicorn-app
   ```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
