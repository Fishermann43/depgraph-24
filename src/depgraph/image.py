"""Генерация изображения графа в формате SVG (этап 5).

Раскладка по слоям поиска в ширину от стартового пакета:
слой равен расстоянию от старта. Узлы — прямоугольники,
рёбра — стрелки. Используется только стандартная библиотека.
"""

from collections import deque

BOX_W = 90
BOX_H = 36
X_STEP = 150
Y_STEP = 70
MARGIN = 20
FONT_SIZE = 14


def spread_unreached(graph, depth):
    """Разложить недостижимые вершины: сами в слой 0, дети — ниже."""
    for name in sorted(graph):
        if name not in depth:
            depth[name] = 0
        for dep in graph.get(name) or []:
            if dep not in depth:
                depth[dep] = depth[name] + 1


def layout(graph, start):
    """Расставить вершины по слоям: имя -> (x, y)."""
    depth = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for child in graph.get(node) or []:
            if child not in depth:
                depth[child] = depth[node] + 1
                queue.append(child)
    spread_unreached(graph, depth)
    layers = {}
    for name, level in depth.items():
        layers.setdefault(level, []).append(name)
    pos = {}
    for level, names in layers.items():
        for index, name in enumerate(sorted(names)):
            pos[name] = (MARGIN + level * X_STEP,
                         MARGIN + index * Y_STEP)
    return pos


def escape(text):
    """Экранировать текст для вставки в XML."""
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;"))


def to_svg(graph, start):
    """Построить SVG-описание графа целиком."""
    pos = layout(graph, start)
    max_x = max(x for x, _ in pos.values()) + BOX_W + MARGIN
    max_y = max(y for _, y in pos.values()) + BOX_H + MARGIN
    head = ('<svg xmlns="http://www.w3.org/2000/svg" '
            'width="%d" height="%d">' % (max_x, max_y))
    parts = [head]
    parts.append('<defs><marker id="arr" markerWidth="8" '
                 'markerHeight="8" refX="8" refY="4" orient="auto">'
                 '<path d="M0,0 L8,4 L0,8 z" fill="black" />'
                 '</marker></defs>')
    for node in sorted(graph):
        if node not in pos:
            continue
        x_from, y_from = pos[node]
        for dep in graph[node]:
            if dep not in pos:
                continue
            x_to, y_to = pos[dep]
            parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" '
                         'stroke="black" marker-end="url(#arr)" />'
                         % (x_from + BOX_W, y_from + BOX_H // 2,
                            x_to, y_to + BOX_H // 2))
    for node in sorted(pos):
        x_box, y_box = pos[node]
        parts.append('<rect x="%d" y="%d" width="%d" height="%d" '
                     'fill="white" stroke="black" />'
                     % (x_box, y_box, BOX_W, BOX_H))
        parts.append('<text x="%d" y="%d" font-size="%d">%s</text>'
                     % (x_box + 8, y_box + BOX_H // 2 + 5,
                        FONT_SIZE, escape(node)))
    parts.append("</svg>")
    return "\n".join(parts)


def write_svg(graph, start, path):
    """Записать изображение графа в файл."""
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(to_svg(graph, start))
