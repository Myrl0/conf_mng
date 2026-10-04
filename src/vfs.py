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
        target = self.current if not args else self._resolve(args[0])
        if target["type"] == "dir":
            names = sorted(target["children"].keys())
            return "\n".join(names) if names else ""
        return target["name"]

    def cmd_cd(self, args):
        if not args:
            self.current = self.root
            return ""
        target = self._resolve(args[0])
        if target["type"] != "dir":
            raise VFSException(f"Не директория: {args[0]}")
        self.current = target
        return ""

    def cmd_pwd(self, args):
        return self.pwd()

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