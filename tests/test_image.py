"""Тесты генерации изображения графа (этап 5)."""

import os
import unittest

from depgraph.graph import load_test_repo
from depgraph.image import layout, to_svg, write_svg

HERE = os.path.dirname(os.path.abspath(__file__))


def data(name):
    """Путь к файлу тестового репозитория."""
    return os.path.join(HERE, "testdata", name)


class TestImage(unittest.TestCase):
    """Проверка SVG-картинки графа."""

    def test_layout_layers(self):
        """Слои идут по расстоянию от старта."""
        graph = load_test_repo(data("branch.txt"))
        pos = layout(graph, "A")
        self.assertLess(pos["A"][0], pos["B"][0])
        self.assertLess(pos["B"][0], pos["D"][0])
        self.assertEqual(pos["B"][0], pos["C"][0])

    def test_svg_frame(self):
        """Картинка обёрнута в тег svg со стрелками."""
        graph = load_test_repo(data("chain.txt"))
        text = to_svg(graph, "A")
        self.assertIn("<svg", text)
        self.assertIn("</svg>", text)
        self.assertIn("marker-end", text)
        self.assertEqual(text.count("<rect"), 3)

    def test_write_file(self):
        """Файл изображения записывается на диск."""
        graph = load_test_repo(data("cycle.txt"))
        path = os.path.join(HERE, "tmp_graph.svg")
        try:
            write_svg(graph, "A", path)
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            self.assertIn("<svg", text)
            self.assertIn("<line", text)
            self.assertIn(">A<", text)
        finally:
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    unittest.main()
