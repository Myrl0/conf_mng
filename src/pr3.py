import os
import sys
import argparse
from vfs import VFS, VFSException

VFS_PATH = None
SCRIPT_PATH = None


def run_script(vfs, script_path):
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
                result = vfs.execute(line)
            except SystemExit:
                raise
            except VFSException as e:
                print(f"Ошибка: {e}", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Непредвиденная ошибка: {e}", file=sys.stderr)
                sys.exit(1)

            if result:
                print(f"VFS $ {result}")


def main():
    parser = argparse.ArgumentParser(description="Эмулятор VFS. Этап 3: VFS")
    parser.add_argument("--vfs-path", required=True,
                        help="Путь к JSON-файлу VFS")
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

    try:
        vfs = VFS(VFS_PATH)
    except VFSException as e:
        print(f"Ошибка инициализации VFS: {e}", file=sys.stderr)
        sys.exit(1)

    run_script(vfs, SCRIPT_PATH)


if __name__ == "__main__":
    main()