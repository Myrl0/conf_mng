import os
import sys
import argparse
import pr1

VFS_PATH = None
SCRIPT_PATH = None

def run_script(script_path):
    if not os.path.isfile(script_path):
        print(f"Ошибка: файл скрипта не найден: {script_path}", file=sys.stderr)
        sys.exit(1)

    with open(script_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.strip().startswith("#"):
                continue

            print(f"VFS {os.path.basename(VFS_PATH)} % {line}")

            try:
                result = pr1.command(line)
            except SystemExit:
                raise
            except Exception as e:
                print(f"Ошибка при выполнении '{line}': {e}", file=sys.stderr)
                sys.exit(1)

            if result == "Неизвестная команда":
                print(f"Ошибка: неизвестная команда '{line}'", file=sys.stderr)
                sys.exit(1)

            print(f"VFS $ {result}")


def main():
    parser = argparse.ArgumentParser(description="Эмулятор VFS. Этап 2: Конфигурация")
    parser.add_argument("--vfs-path", required=True,
                        help="Путь к физическому расположению VFS")
    parser.add_argument("--script", required=True,
                        help="Путь к стартовому скрипту")
    args = parser.parse_args()

    global VFS_PATH, SCRIPT_PATH
    VFS_PATH = args.vfs_path
    SCRIPT_PATH = args.script

    print("=== Параметры запуска эмулятора ===")
    print(f"Путь к VFS:          {VFS_PATH}")
    print(f"Путь к скрипту:      {SCRIPT_PATH}")
    print(f"Абсолютный путь VFS: {os.path.abspath(VFS_PATH)}")
    print("===================================\n")

    # Проверяем существование VFS
    if not os.path.isdir(VFS_PATH):
        print(f"Ошибка: каталог VFS не найден: {VFS_PATH}", file=sys.stderr)
        sys.exit(1)

    run_script(SCRIPT_PATH)


if __name__ == "__main__":
    main()