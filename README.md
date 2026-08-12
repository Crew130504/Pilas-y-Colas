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
