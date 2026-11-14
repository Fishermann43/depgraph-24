"""Тесты прототипа CLI (этап 1)."""

import unittest

from depgraph.cli import (
    ConfigError,
    check_image,
    check_package,
    check_repo,
    format_params,
    main,
    parse_args,
    parse_depth,
    parse_flag,
    validate,
)


class TestParseArgs(unittest.TestCase):
    """Проверка разбора аргументов."""

    def base(self):
        """Минимальный набор аргументов."""
        return ["--package", "A", "--repo", "https://x/y",
                "--image", "graph.png"]

    def test_defaults(self):
        """Значения по умолчанию для флагов и глубины."""
        args = parse_args(self.base())
        self.assertEqual(args.test_mode, "off")
        self.assertEqual(args.ascii_tree, "off")
        self.assertEqual(args.max_depth, "0")

    def test_missing_value_exits(self):
        """Отсутствие значения завершает работу с кодом 2."""
        with self.assertRaises(SystemExit) as ctx:
            parse_args(["--package"])
        self.assertEqual(ctx.exception.code, 2)

    def test_flag_values(self):
        """Флаг понимает on/off, true/false, 1/0."""
        for good in ("on", "true", "1", "yes", "OFF", "False", "0"):
            self.assertIn(parse_flag(good), (True, False))

    def test_flag_bad_value(self):
        """Мусор во флаге даёт ошибку настроек."""
        with self.assertRaises(ConfigError):
            parse_flag("maybe")

    def test_depth(self):
        """Глубина — целое неотрицательное."""
        self.assertEqual(parse_depth("3"), 3)
        self.assertEqual(parse_depth("0"), 0)
        with self.assertRaises(ConfigError):
            parse_depth("-1")
        with self.assertRaises(ConfigError):
            parse_depth("много")


class TestValidate(unittest.TestCase):
    """Проверка настроек целиком."""

    def test_empty_package(self):
        """Пустое имя пакета запрещено."""
        with self.assertRaises(ConfigError):
            check_package("   ")

    def test_repo_must_exist(self):
        """Несуществующий путь отклоняется."""
        with self.assertRaises(ConfigError):
            check_repo("/нет/такого/файла.txt")

    def test_empty_image(self):
        """Пустое имя файла запрещено."""
        with self.assertRaises(ConfigError):
            check_image("  ")

    def test_format(self):
        """Вывод настроек идёт строками ключ-значение."""
        args = parse_args(["--package", "A",
                           "--repo", "https://x/y",
                           "--image", "g.png",
                           "--ascii-tree", "on",
                           "--max-depth", "2"])
        text = format_params(validate(args))
        self.assertIn("package=A", text)
        self.assertIn("ascii_tree=True", text)
        self.assertIn("max_depth=2", text)

    def test_main_bad_flag(self):
        """Программа возвращает 2 при плохом флаге."""
        code = main(["--package", "A", "--repo", "https://x/y",
                     "--image", "g.png", "--test-mode", "maybe"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
