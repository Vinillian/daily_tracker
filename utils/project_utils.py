def get_project_tasks(project_data):
    tasks = []
    for key, value in project_data.items():
        if key in ["metadata", "overall"]:
            continue
        if isinstance(value, list):
            for section in value:
                if isinstance(section, dict) and "задачи" in section:
                    tasks.extend(section["задачи"])
        elif isinstance(value, dict):
            for task_name, progress in value.items():
                if isinstance(progress, (int, float)):
                    tasks.append({"название": task_name, "прогресс": progress, "раздел": key})
    return tasks


def get_project_sections(project_data):
    sections = {}
    for key, value in project_data.items():
        if key in ["metadata", "overall"]:
            continue
        if isinstance(value, list):
            for section in value:
                if isinstance(section, dict) and "название" in section and "задачи" in section:
                    sections[section["название"]] = section["задачи"]
        elif isinstance(value, dict):
            sections[key] = [{"название": k, "прогресс": v} for k, v in value.items() if isinstance(v, (int, float))]
    return sections


def calculate_overall_progress(project_data):
    """Вычисляет общий прогресс проекта"""
    sections = get_project_sections(project_data)
    total_tasks = 0
    total_progress = 0

    for tasks in sections.values():
        for task in tasks:
            total_tasks += 1
            total_progress += task.get('прогресс', 0)

    if total_tasks == 0:
        return 0
    return total_progress // total_tasks