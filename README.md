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

To start the Uvicorn server, run the following command:

```
uvicorn app.main:app --reload
```

This will start the application in development mode, allowing for hot-reloading.

## Testing

To run the tests, use the following command:

```
pytest tests/test_main.py
```

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