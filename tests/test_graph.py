"""Тесты построения графа поиском в ширину (этап 3)."""

import os
import unittest

from depgraph.graph import bfs_iterative, load_test_repo, trace_cycle

HERE = os.path.dirname(os.path.abspath(__file__))


def data(name):
    """Путь к файлу тестового репозитория."""
    return os.path.join(HERE, "testdata", name)


def getter(graph):
    """Получить зависимости вершины из словаря."""
    return lambda node: graph.get(node, [])


class TestGraph(unittest.TestCase):
    """Проверка загрузки файла и обхода в ширину."""

    def test_load(self):
        """Файл читается в словарь смежности."""
        graph = load_test_repo(data("chain.txt"))
        self.assertEqual(graph, {"A": ["B"], "B": ["C"], "C": []})

    def test_chain_order(self):
        """Линейная цепочка обходится по порядку."""
        graph = load_test_repo(data("chain.txt"))
        order, cycles = bfs_iterative("A", getter(graph))
        self.assertEqual(order, ["A", "B", "C"])
        self.assertEqual(cycles, [])

    def test_branch_level(self):
        """Ветвление обходится по уровням."""
        graph = load_test_repo(data("branch.txt"))
        order, cycles = bfs_iterative("A", getter(graph))
        self.assertEqual(order, ["A", "B", "C", "D"])
        self.assertEqual(cycles, [])

    def test_depth_limit(self):
        """Глубина ограничивает обход."""
        graph = load_test_repo(data("branch.txt"))
        order, _ = bfs_iterative("A", getter(graph), max_depth=1)
        self.assertEqual(order, ["A", "B", "C"])

    def test_cycle_found(self):
        """Цикл находится и обход завершается."""
        graph = load_test_repo(data("cycle.txt"))
        order, cycles = bfs_iterative("A", getter(graph))
        self.assertEqual(sorted(order), ["A", "B", "C"])
        self.assertEqual(len(cycles), 1)
        self.assertEqual(cycles[0][0], cycles[0][-1])

    def test_trace(self):
        """Путь цикла восстанавливается по предкам."""
        parent = {"A": None, "B": "A", "C": "B"}
        self.assertEqual(trace_cycle(parent, "C", "A"),
                         ["A", "B", "C", "A"])


if __name__ == "__main__":
    unittest.main()
