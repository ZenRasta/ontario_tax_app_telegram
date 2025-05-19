import os
import pathlib

# Base directory name for the project
BASE_DIR_NAME = "retirement_planner_app"

# List of all files to be created.
# Parent directories will be created automatically.
# Using pathlib.Path allows for OS-agnostic path handling.
files_to_create = [
    # app/
    "app/__init__.py",
    "app/main.py",
    # app/api/
    "app/api/__init__.py",
    "app/api/v1/__init__.py",
    "app/api/v1/routes.py",
    "app/api/v1/endpoints/__init__.py",
    "app/api/v1/endpoints/simulation_controller.py",
    "app/api/v1/endpoints/explain_controller.py",
    # app/core/
    "app/core/__init__.py",
    "app/core/config.py",
    "app/core/security.py",
    # app/data_models/
    "app/data_models/__init__.py",
    "app/data_models/scenario.py",
    "app/data_models/results.py",
    "app/data_models/strategy.py",
    # app/db/
    "app/db/__init__.py",
    "app/db/session_manager.py",
    "app/db/schemas.py", # Optional, but good to have
    # app/services/
    "app/services/__init__.py",
    "app/services/monte_carlo_service.py",
    "app/services/llm_service.py",
    # app/services/strategy_engine/
    "app/services/strategy_engine/__init__.py",
    "app/services/strategy_engine/engine.py",
    "app/services/strategy_engine/tax_rules.py",
    # app/services/strategy_engine/strategies/
    "app/services/strategy_engine/strategies/__init__.py",
    "app/services/strategy_engine/strategies/base_strategy.py",
    "app/services/strategy_engine/strategies/gradual_meltdown.py",
    "app/services/strategy_engine/strategies/early_rrif_conversion.py",
    "app/services/strategy_engine/strategies/bracket_filling.py",
    "app/services/strategy_engine/strategies/delay_cpp_oas.py",
    "app/services/strategy_engine/strategies/spousal_equalization.py",
    "app/services/strategy_engine/strategies/lump_sum_withdrawal.py",
    "app/services/strategy_engine/strategies/interest_offset_loan.py",
    # app/utils/
    "app/utils/__init__.py",
    "app/utils/helpers.py",
    "app/utils/year_data_loader.py",
    # data/
    "data/tax_years.yml",
    # tests/
    "tests/__init__.py",
    "tests/conftest.py",
    # tests/unit/
    "tests/unit/__init__.py",
    "tests/unit/utils/__init__.py",
    "tests/unit/utils/test_year_data_loader.py",
    "tests/unit/services/__init__.py",
    "tests/unit/services/strategy_engine/__init__.py",
    "tests/unit/services/strategy_engine/test_tax_rules.py",
    "tests/unit/services/strategy_engine/strategies/__init__.py",
    "tests/unit/services/strategy_engine/strategies/test_gradual_meltdown.py",
    "tests/unit/services/strategy_engine/strategies/test_early_rrif_conversion.py",
    "tests/unit/services/strategy_engine/strategies/test_bracket_filling.py",
    "tests/unit/services/strategy_engine/strategies/test_delay_cpp_oas.py",
    "tests/unit/services/strategy_engine/strategies/test_spousal_equalization.py",
    "tests/unit/services/strategy_engine/strategies/test_lump_sum_withdrawal.py",
    "tests/unit/services/strategy_engine/strategies/test_interest_offset_loan.py",
    # tests/integration/
    "tests/integration/__init__.py",
    "tests/integration/api/__init__.py",
    "tests/integration/api/v1/__init__.py",
    "tests/integration/api/v1/test_simulation_controller.py",
    # tests/e2e/ (often kept minimal initially)
    "tests/e2e/__init__.py",
    # scripts/
    "scripts/purge_expired_sessions.py",
    # Root files
    ".env",
    ".env.example",
    ".gitignore",
    "Dockerfile",
    "docker-compose.yml",
    "pyproject.toml",
    "README.md",
]

def create_project_structure(base_dir_name):
    """Creates the project directory structure and empty files."""
    base_path = pathlib.Path(base_dir_name)
    print(f"Creating project structure in: {base_path.resolve()}")

    # Create the base project directory
    base_path.mkdir(exist_ok=True)

    for file_rel_path_str in files_to_create:
        file_path = base_path / file_rel_path_str

        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create the file if it doesn't exist
        if not file_path.exists():
            with open(file_path, 'w') as f:
                if file_rel_path_str.endswith(".py"):
                    f.write("# TODO: Implement Python module\n")
                elif file_rel_path_str.endswith(".yml"):
                    f.write("# TODO: Add YAML configuration\n")
                elif file_rel_path_str == ".gitignore":
                    f.write(
                        "# Git ignore rules\n"
                        "__pycache__/\n"
                        "*.pyc\n"
                        "*.pyo\n"
                        "*.pyd\n"
                        ".Python\n"
                        "env/\n"
                        "venv/\n"
                        ".venv/\n"
                        "*.egg-info/\n"
                        "dist/\n"
                        "build/\n"
                        ".env\n"
                        ".vscode/\n"
                        ".idea/\n"
                        ".pytest_cache/\n"
                        ".mypy_cache/\n"
                        "htmlcov/\n" # Coverage reports
                        "instance/\n" # Flask instance folder
                        "*.sqlite3\n"
                        "*.db\n"
                    )
                elif file_rel_path_str == "pyproject.toml":
                    f.write(
                        "[tool.poetry]\n"
                        "name = \"retirement-planner-app\"\n"
                        "version = \"0.1.0\"\n"
                        "description = \"Ontario Retirement Withdrawal Planning App\"\n"
                        "authors = [\"Your Name <you@example.com>\"]\n"
                        "readme = \"README.md\"\n"
                        "\n"
                        "[tool.poetry.dependencies]\n"
                        "python = \"^3.10\" # Or your preferred Python version\n"
                        "fastapi = \"^0.100.0\"\n"
                        "uvicorn = {extras = [\"standard\"], version = \"^0.23.2\"}\n"
                        "pydantic = \"^2.0.0\" # Check compatibility if using older Pydantic features\n"
                        "pydantic-settings = \"^2.0.0\"\n"
                        "psycopg2-binary = \"^2.9.6\" # For PostgreSQL\n"
                        "python-jose = {extras = [\"cryptography\"], version = \"^3.3.0\"} # For JWTs if needed\n"
                        "passlib = {extras = [\"bcrypt\"], version = \"^1.7.4\"} # For password hashing if needed\n"
                        "PyYAML = \"^6.0\" # For reading YAML files\n"
                        "numpy = \"^1.25.0\" # For Monte Carlo\n"
                        "pandas = \"^2.0.0\" # For data manipulation in Monte Carlo\n"
                        # Add other dependencies like httpx for calling LLM APIs, etc.
                        "\n"
                        "[tool.poetry.group.dev.dependencies]\n"
                        "pytest = \"^7.4.0\"\n"
                        "pytest-asyncio = \"^0.21.0\"\n"
                        "httpx = \"^0.24.0\" # For testing API calls\n"
                        "ruff = \"^0.0.285\" # For linting\n"
                        "\n"
                        "[build-system]\n"
                        "requires = [\"poetry-core\"]\n"
                        "build-backend = \"poetry.core.masonry.api\"\n"
                        "\n"
                        "[tool.ruff]\n"
                        "line-length = 88\n"
                        "select = [\"E\", \"W\", \"F\", \"I\", \"C\", \"B\"] # flake8 error, warning, pyflakes, isort, flake8-comprehensions, flake8-bugbear\n"
                        "ignore = [\"E501\"] # Allow longer lines if necessary, handled by formatter (like Black)\n"

                    )
                elif file_rel_path_str == "README.md":
                    f.write(f"# {BASE_DIR_NAME}\n\nProject description here.\n")
                elif file_rel_path_str == ".env.example":
                    f.write(
                        "DATABASE_URL=postgresql://user:password@localhost:5432/retirement_sessions_db\n"
                        "TAX_YEARS_FILE=data/tax_years.yml\n"
                        "SESSION_DATA_TTL_HOURS=24\n"
                        "# OPENAI_API_KEY=\n"
                        "# ANTHROPIC_API_KEY=\n"
                    )
                elif file_rel_path_str == "Dockerfile":
                    f.write(
                        "# Stage 1: Build the application with Poetry\n"
                        "FROM python:3.10-slim as builder\n\n"
                        "WORKDIR /app\n\n"
                        "# Install poetry\n"
                        "RUN pip install poetry\n\n"
                        "# Copy only files necessary for dependency installation\n"
                        "COPY pyproject.toml poetry.lock* ./\n\n"
                        "# Install dependencies\n"
                        "# --no-root: don't install the project itself yet\n"
                        "# --no-dev: don't install dev dependencies\n"
                        "RUN poetry config virtualenvs.create false && poetry install --no-root --no-dev --no-interaction --no-ansi\n\n"
                        "# Stage 2: Create the runtime image\n"
                        "FROM python:3.10-slim\n\n"
                        "WORKDIR /app\n\n"
                        "# Copy installed dependencies from builder stage\n"
                        "COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages\n"
                        "COPY --from=builder /usr/local/bin /usr/local/bin\n\n"
                        "# Copy the application code\n"
                        "COPY ./app /app/app\n"
                        "COPY ./data /app/data\n\n" # If data files need to be in the image
                        "# Expose the port the app runs on\n"
                        "EXPOSE 8000\n\n"
                        "# Command to run the application\n"
                        "# Adjust if your main.py is elsewhere or app instance is named differently\n"
                        "CMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n"
                    )
                elif file_rel_path_str == "docker-compose.yml":
                    f.write(
                        "version: '3.8'\n\n"
                        "services:\n"
                        "  backend:\n"
                        "    build: .\n"
                        "    ports:\n"
                        "      - \"8000:8000\"\n"
                        "    volumes:\n"
                        "      - ./app:/app/app  # Mount app code for development\n"
                        "      - ./data:/app/data # Mount data for development\n"
                        "    env_file:\n"
                        "      - .env\n"
                        "    depends_on:\n"
                        "      - db\n"
                        "    # command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload # For development with reload\n\n"
                        "  db:\n"
                        "    image: postgres:15\n"
                        "    volumes:\n"
                        "      - postgres_data:/var/lib/postgresql/data/\n"
                        "    ports:\n"
                        "      - \"5432:5432\"\n"
                        "    environment:\n"
                        "      - POSTGRES_USER=user # Should match .env or config\n"
                        "      - POSTGRES_PASSWORD=password # Should match .env or config\n"
                        "      - POSTGRES_DB=retirement_sessions_db # Should match .env or config\n\n"
                        "volumes:\n"
                        "  postgres_data:\n"
                    )

                print(f"Created: {file_path}")
        else:
            print(f"Exists, skipped: {file_path}")


    print(f"\nProject '{base_path.name}' structure created successfully in '{base_path.parent.resolve()}'!")
    print("Next steps suggestion:")
    print("1. Review the generated files, especially pyproject.toml, Dockerfile, and .env.example.")
    print(f"2. Navigate into the project: `cd {base_path.name}`")
    print("3. Initialize Git: `git init && git add . && git commit -m \"Initial project structure\"`")
    print("4. If using Poetry: `poetry install` (to install dependencies and create .lock file)")
    print("5. If using PDM: `pdm install`")
    print("6. Start developing!")

if __name__ == "__main__":
    create_project_structure(BASE_DIR_NAME)
