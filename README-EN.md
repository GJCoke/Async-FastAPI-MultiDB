<div align="center">
	<h1>Async-FastAPI-MultiDB</h1>
  <span><a href="./README.md">中文</a> | English</span>
</div>

Async-FastAPI-MultiDB is an asynchronous FastAPI template project designed to seamlessly integrate both SQL (e.g., PostgreSQL, MySQL) and NoSQL (e.g., MongoDB) databases. This template offers a modern and efficient web framework solution supporting asynchronous request handling, making it ideal for building scalable API services.

## Features
- **Asynchronous Architecture:** Full support for `async/await`, enhancing performance.
- **SQL & NoSQL Integration:** Compatible with SQLAlchemy and Motor for database operations.
- **Modular Design:** Clean and maintainable code structure with easy extensibility.
- **Automatic Documentation Generation:** Utilizes FastAPI's built-in capabilities for generating API documentation.
- **Environment-Based Configuration Management:** Simplifies configuration switching for different environments.

## Installation
1. Clone the repository:
```bash
    git clone https://github.com/GJCoke/Async-FastAPI-MultiDB.git
    cd Async-FastAPI-MultiDB
```
2. Install dependencies:
```bash
    pip install -r requirements.txt
```

## Usage
1. Create and apply migrations for SQL database (e.g., PostgreSQL):
```bash
    alembic upgrade head
```
2. Run the server:
```bash
    uvicorn main:app --reload
```
3. Access the automatically generated documentation at:
```
    http://127.0.0.1:8000/docs
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
