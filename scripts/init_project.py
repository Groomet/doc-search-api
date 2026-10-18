import subprocess
import sys


def main():
    commands = [
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        [sys.executable, "-m", "scripts.import_data"],
        [sys.executable, "-m", "scripts.create_index"],
        [sys.executable, "-m", "scripts.index_documents"],
    ]

    for command in commands:
        print(f"Запуск: {' '.join(command)}", flush=True)
        subprocess.run(command, check=True)

    print("Инициализация завершена!")


if __name__ == "__main__":
    main()