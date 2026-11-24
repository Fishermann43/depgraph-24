"""Разбор и проверка параметров командной строки (этап 1)."""

import argparse
import os

from depgraph.cargo import direct_dependencies
from depgraph.graph import bfs_iterative, load_test_repo


class ConfigError(Exception):
    """Ошибка в параметрах запуска."""


def parse_flag(value):
    """Превратить строку в логическое значение флага."""
    text = value.strip().lower()
    if text in ("1", "true", "on", "yes"):
        return True
    if text in ("0", "false", "off", "no"):
        return False
    raise ConfigError("флаг должен быть on/off, true/false или 1/0")


def parse_depth(value):
    """Проверить глубину: целое неотрицательное, 0 — без предела."""
    try:
        depth = int(value)
    except (TypeError, ValueError):
        raise ConfigError("глубина должна быть целым числом")
    if depth < 0:
        raise ConfigError("глубина не должна быть отрицательной")
    return depth


def build_parser():
    """Создать парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализация графа зависимостей Cargo")
    parser.add_argument("--package", required=True,
                        help="имя анализируемого пакета")
    parser.add_argument("--repo", required=True,
                        help="URL репозитория или файл тестового репозитория")
    parser.add_argument("--test-mode", default="off",
                        help="режим тестового репозитория (on/off)")
    parser.add_argument("--image", required=True,
                        help="имя файла с изображением графа")
    parser.add_argument("--ascii-tree", default="off",
                        help="вывод дерева ASCII (on/off)")
    parser.add_argument("--max-depth", default="0",
                        help="максимальная глубина анализа, 0 — без предела")
    return parser


def parse_args(argv=None):
    """Разобрать аргументы и вернуть параметры запуска."""
    return build_parser().parse_args(argv)


def check_package(value):
    """Проверить имя пакета: не должно быть пустым."""
    if not value or not value.strip():
        raise ConfigError("имя пакета не должно быть пустым")
    return value.strip()


def check_repo(value):
    """Проверить адрес репозитория: URL или существующий файл."""
    text = (value or "").strip()
    if text.startswith("http://") or text.startswith("https://"):
        return text
    if text and os.path.isfile(text):
        return text
    raise ConfigError("repo должен быть URL или существующим файлом")


def check_image(value):
    """Проверить имя файла изображения: не должно быть пустым."""
    if not value or not value.strip():
        raise ConfigError("имя файла изображения не должно быть пустым")
    return value.strip()


def validate(args):
    """Проверить все параметры, вернуть словарь настроек."""
    return {
        "package": check_package(args.package),
        "repo": check_repo(args.repo),
        "test_mode": parse_flag(args.test_mode),
        "image": check_image(args.image),
        "ascii_tree": parse_flag(args.ascii_tree),
        "max_depth": parse_depth(args.max_depth),
    }


def format_params(settings):
    """Отформатировать настройки строками ключ-значение."""
    keys = ("package", "repo", "test_mode", "image",
            "ascii_tree", "max_depth")
    lines = []
    for key in keys:
        lines.append("%s=%s" % (key, settings[key]))
    return "\n".join(lines)


def print_test_graph(settings):
    """Построить и вывести граф из тестового файла (этапы 3-5)."""
    from depgraph.ascii_tree import render_tree
    graph = load_test_repo(settings["repo"])
    get_deps = graph.get
    order, cycles = bfs_iterative(settings["package"], get_deps,
                                  settings["max_depth"])
    print("graph order:")
    for name in order:
        print("  " + name)
    if cycles:
        print("cycles:")
        for found in cycles:
            print("  " + " -> ".join(found))
    if settings["ascii_tree"]:
        print("ascii tree:")
        print(render_tree(settings["package"], get_deps,
                          settings["max_depth"]))
    return 0


def main(argv=None):
    """Точка входа: параметры, затем зависимости (этапы 2-3)."""
    try:
        settings = validate(parse_args(argv))
    except ConfigError as err:
        print("ошибка: %s" % err)
        return 2
    print(format_params(settings))
    if settings["test_mode"] and os.path.isfile(settings["repo"]):
        return print_test_graph(settings)
    try:
        deps = direct_dependencies(settings["package"],
                                   settings["repo"])
    except Exception as err:
        print("ошибка: %s" % err)
        return 1
    print("dependencies:")
    for name in deps:
        print("  " + name)
    return 0
