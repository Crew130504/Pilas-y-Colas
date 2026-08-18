# Data Structures: Stacks and Queues

One web application and one Docker container. The navigation menu switches between the Stacks and Queues modules.

- `Pilas/routes.py`: Stacks module.
- `Colas/routes.py`: Queues module.
- `templates/`: HTML templates shared by the application.
- `static/`: shared CSS styles.
- `app.py`: common application entry point.

## Run the application

```powershell
docker compose up --build
```

Open `http://localhost:8080` and use the navigation menu to switch modules.

## Add queue tasks in batch

The Queues module retains the individual task form and also provides a batch form.
Enter one task per line with the format `task name,execution time`, for example:

```text
Task 1,5
Task 2,10
Task 3,2
```

Blank lines are ignored. All nonblank lines are validated before any task is added, so an invalid line leaves the queue unchanged. Task names may contain commas; the final comma separates the name from the execution time.
