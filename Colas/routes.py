

from dataclasses import dataclass

from flask import Blueprint, render_template, request


queues_bp = Blueprint("queues", __name__,url_prefix="/queues")


@dataclass
class Task:
    id: int
    name: str
    duration: int


# Cola de tareas
tasks_queue: list[Task] = []

# Identificador para evitar IDs repetidos
next_task_id = 1


def add_task(name: str, duration: int):
    """
    Agrega una nueva tarea al final de la cola.
    """
    global next_task_id

    task = Task(
        id=next_task_id,
        name=name,
        duration=duration
    )

    tasks_queue.append(task)
    next_task_id += 1


def add_tasks_batch(tasks_text: str) -> int:
    """Add tasks from ``name,duration`` lines, preserving their input order."""
    parsed_tasks: list[tuple[str, int]] = []

    for line_number, line in enumerate(tasks_text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue

        try:
            name, duration_text = (part.strip() for part in line.rsplit(",", 1))
            duration = int(duration_text)
        except ValueError as error:
            raise ValueError(
                f"Línea {line_number}: use el formato nombre,duración."
            ) from error

        if not name or duration <= 0:
            raise ValueError(
                f"Línea {line_number}: el nombre es obligatorio y la duración debe ser mayor que cero."
            )

        parsed_tasks.append((name, duration))

    if not parsed_tasks:
        raise ValueError("Ingrese al menos una tarea con el formato nombre,duración.")

    for name, duration in parsed_tasks:
        add_task(name, duration)

    return len(parsed_tasks)


def remove_task():
    """
    Elimina la primera tarea de la cola.
    """
    if not tasks_queue:
        return None

    return tasks_queue.pop(0)


def process_tasks(processor_count: int):
    """
    Distribuye las tareas entre los procesadores.

    Se utiliza una estrategia de menor duración primero.
    Cada nueva tarea se asigna al procesador que queda
    disponible primero.
    """

    if not tasks_queue or processor_count <= 0:
        return []

    # Menor duración primero
    ordered_tasks = sorted(
        tasks_queue,
        key=lambda task: task.duration
    )

    # Tiempo en el que queda disponible cada procesador
    processors = [0] * processor_count

    results = []

    for task in ordered_tasks:

        # Buscar el procesador disponible primero
        processor_index = processors.index(
            min(processors)
        )

        start_time = processors[processor_index]
        finish_time = start_time + task.duration

        # Actualizar disponibilidad del procesador
        processors[processor_index] = finish_time

        results.append({
            "task": task,
            "processor": processor_index + 1,
            "start": start_time,
            "finish": finish_time
        })

    return results


@queues_bp.route("/", methods=["GET", "POST"])
def queues_page():

    results = None
    message = None
    message_type = None

    if request.method == "POST":

        action = request.form.get("action")

        # -----------------------------------
        # AGREGAR TAREA
        # -----------------------------------
        if action == "add":

            name = request.form.get("name", "").strip()
            duration_text = request.form.get("duration", "").strip()

            if not name:
                message = "Debe ingresar un nombre para la tarea."
                message_type = "failure"

            elif not duration_text:
                message = "Debe ingresar el tiempo de ejecución."
                message_type = "failure"

            else:
                try:
                    duration = int(duration_text)

                    if duration <= 0:
                        raise ValueError

                    add_task(name, duration)

                    message = (
                        f"La tarea '{name}' fue agregada "
                        "correctamente a la cola."
                    )
                    message_type = "success"

                except ValueError:
                    message = (
                        "El tiempo debe ser un número entero "
                        "mayor que cero."
                    )
                    message_type = "failure"

        # -----------------------------------
        # AGREGAR TAREAS EN LOTE
        # -----------------------------------
        elif action == "add_bulk":

            tasks_text = request.form.get("tasks_bulk", "")

            try:
                added_count = add_tasks_batch(tasks_text)
                message = f"Se agregaron {added_count} tarea(s) correctamente a la cola."
                message_type = "success"
            except ValueError as error:
                message = str(error)
                message_type = "failure"

        # -----------------------------------
        # ELIMINAR TAREA
        # -----------------------------------
        elif action == "remove":

            removed = remove_task()

            if removed is None:
                message = "No hay tareas en la cola para eliminar."
                message_type = "failure"
            else:
                message = (
                    f"La tarea '{removed.name}' fue eliminada "
                    "de la cola."
                )
                message_type = "success"

        # -----------------------------------
        # PROCESAR TAREAS
        # -----------------------------------
        elif action == "process":

            processor_text = request.form.get(
                "processors",
                ""
            ).strip()

            try:
                processor_count = int(processor_text)

                if processor_count <= 0:
                    raise ValueError

                if not tasks_queue:
                    message = "No hay tareas para procesar."
                    message_type = "failure"
                else:
                    results = process_tasks(processor_count)

                    message = (
                        "Las tareas fueron distribuidas "
                        "entre los procesadores."
                    )
                    message_type = "success"

            except ValueError:
                message = (
                    "El número de procesadores debe ser "
                    "un entero mayor que cero."
                )
                message_type = "failure"

        # -----------------------------------
        # SALIR / LIMPIAR
        # -----------------------------------
        elif action == "exit":

            tasks_queue.clear()

            message = "La cola fue limpiada correctamente."
            message_type = "success"

    return render_template(
        "queues/index.html",
        tasks=tasks_queue,
        results=results,
        message=message,
        message_type=message_type
    )
