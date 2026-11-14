"""Тесты ASCII-дерева (этап 4)."""

import os
import unittest

from depgraph.ascii_tree import render_tree
from depgraph.graph import load_test_repo

HERE = os.path.dirname(os.path.abspath(__file__))


def data(name):
    """Путь к файлу тестового репозитория."""
    return os.path.join(HERE, "testdata", name)


def getter(graph):
    """Получить зависимости вершины из словаря."""
    return lambda node: graph.get(node, [])


class TestAsciiTree(unittest.TestCase):
    """Проверка текстового дерева."""

    def test_chain(self):
        """Цепочка рисуется лесенкой."""
        graph = load_test_repo(data("chain.txt"))
        text = render_tree("A", getter(graph))
        self.assertEqual(text, "A\n`-- B\n    `-- C")

    def test_depth(self):
        """Глубина обрезает дерево."""
        graph = load_test_repo(data("branch.txt"))
        text = render_tree("A", getter(graph), max_depth=1)
        self.assertEqual(text, "A\n+-- B\n`-- C")

    def test_cycle_stops(self):
        """Цикл помечается и обход завершается."""
        graph = load_test_repo(data("cycle.txt"))
        text = render_tree("A", getter(graph))
        self.assertIn("A (повтор)", text)
        self.assertEqual(len(text.splitlines()), 4)


if __name__ == "__main__":
    unittest.main()
