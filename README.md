# Northbeam Docs Studio

A documentation application built with Vue 3, Python Flask,
and SQLite. Writers can manage drafts and version history;
public readers see only published content.

## Technology Stack

- Python
- Flask
- Vue 3
- SQLite

## Running the Application

Run the backend and frontend in two separate terminals.

### Start the Backend

Open a terminal in the `backend` folder, activate your Python
virtual environment if applicable, and run:

```bash
python run.py
```

### Start the Frontend

Open another terminal in the `frontend` folder and run:

```bash
npm run dev
```

## Running Tests

From the `backend` folder, with the virtual environment activated:

```bash
python -m pytest -q
```

### Open the Application

Open the local URL displayed by the frontend terminal in your
browser. Keep both terminals running while using the application.

To stop either server, press `Ctrl+C` in its terminal.

## Tradeoff

I chose SQLite to keep local setup simple and avoid requiring
a separate database server. This suits the assignment's small,
local scope, but SQLite serializes writes. If the application
needed to support significantly more concurrent writers,
I would evaluate PostgreSQL and test the transaction behavior
under that workload.

Given the time budget, I prioritized the core article lifecycle, data integrity, and automated tests. With more time, I would add an optional LLM writing assistant to review drafts and suggest improvements to grammar, clarity, tone, and structure. Writers would review and accept suggestions before applying them to the draft, with publishing remaining an explicit action. This would also require handling API failures, protecting draft privacy, and ensuring the application works without an LLM connection.