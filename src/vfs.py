import json
import base64
import os


class VFSException(Exception):
    """Ошибка при работе с VFS."""
    pass


class VFS:
    def __init__(self, json_path):
        self.json_path = json_path
        self.root = None
        self.current = None
        self._load()

    def _load(self):
        if not os.path.isfile(self.json_path):
            raise VFSException(f"VFS JSON не найден: {self.json_path}")
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.root = self._build(data, None)
        self.current = self.root

    def _build(self, data, parent):
        t = data.get("type")
        if t == "dir":
            node = {"type": "dir", "name": data.get("name", ""),
                    "parent": parent, "children": {}}
            for name, child in data.get("children", {}).items():
                child["name"] = name
                node["children"][name] = self._build(child, node)
            return node
        elif t == "file":
            enc = data.get("encoding", "utf-8")
            raw = data.get("content", "")
            if enc == "base64":
                try:
                    content = base64.b64decode(raw).decode("utf-8", errors="replace")
                except Exception as e:
                    raise VFSException(f"Ошибка base64 в '{data.get('name')}': {e}")
            else:
                content = raw
            return {"type": "file", "name": data.get("name", ""),
                    "parent": parent, "content": content,
                    "encoding": enc, "raw": raw}
        else:
            raise VFSException(f"Неизвестный тип узла: {t}")

    def _resolve(self, path):
        if not path or path == ".":
            return self.current
        if path == "/":
            return self.root
        node = self.root if path.startswith("/") else self.current
        for part in path.strip("/").split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                if node["parent"] is not None:
                    node = node["parent"]
                continue
            if node["type"] != "dir":
                raise VFSException(f"Не директория: {path}")
            if part not in node["children"]:
                raise VFSException(f"Нет такого файла или каталога: {path}")
            node = node["children"][part]
        return node

    def pwd(self):
        parts, node = [], self.current
        while node is not None and node is not self.root:
            parts.append(node["name"])
            node = node["parent"]
        return "/" + "/".join(reversed(parts)) if parts else "/"

    def cmd_ls(self, args):
        """ls [путь ...] — вывод содержимого каталога."""
        if not args:
            targets = [self.current]
        else:
            targets = [self._resolve(a) for a in args]

        out_lines = []
        multi = len(targets) > 1
        for i, node in enumerate(targets):
            if multi:
                if i > 0:
                    out_lines.append("")
                out_lines.append(f"{args[i]}:" if args else f"{node['name']}:")
            if node["type"] == "dir":
                names = sorted(node["children"].keys())
                out_lines.extend(names)
            else:
                out_lines.append(node["name"])
        return "\n".join(out_lines)

    def cmd_cd(self, args):
        """cd [путь] — переход в каталог."""
        if len(args) > 1:
            raise VFSException("cd: слишком много аргументов")
        if not args or args[0] == "~":
            self.current = self.root
            return ""
        target = self._resolve(args[0])
        if target["type"] != "dir":
            raise VFSException(f"cd: не директория: {args[0]}")
        self.current = target
        return ""

    def cmd_pwd(self, args):
        """pwd — текущий путь."""
        return self.pwd()

    def cmd_echo(self, args):
        """echo аргументы... — выводит аргументы через пробел."""
        return " ".join(args)

    def cmd_cat(self, args):
        """cat файл [файл ...] — вывод содержимого файлов."""
        if not args:
            raise VFSException("cat: не указан файл")
        chunks = []
        for path in args:
            node = self._resolve(path)
            if node["type"] != "file":
                raise VFSException(f"cat: {path}: это директория")
            chunks.append(node["content"])
        return "\n".join(chunks)

    def cmd_tail(self, args):
        """tail [-n N] файл — последние N строк (по умолчанию 10)."""
        n = 10
        if not args:
            raise VFSException("tail: не указан файл")
        if args[0] == "-n":
            if len(args) < 3:
                raise VFSException("tail: -n требует число и файл")
            try:
                n = int(args[1])
            except ValueError:
                raise VFSException(f"tail: неверное число: {args[1]}")
            args = args[2:]
        if not args:
            raise VFSException("tail: не указан файл")
        node = self._resolve(args[0])
        if node["type"] != "file":
            raise VFSException(f"tail: {args[0]}: это директория")
        lines = node["content"].splitlines()
        return "\n".join(lines[-n:]) if lines else ""

    def cmd_exit(self, args):
        raise SystemExit(0)

    def execute(self, line):
        parts = line.split()
        if not parts:
            return ""
        cmd, args = parts[0], parts[1:]
        method = getattr(self, "cmd_" + cmd, None)
        if method is None:
            raise VFSException(f"Неизвестная команда: {cmd}")
        return method(args)