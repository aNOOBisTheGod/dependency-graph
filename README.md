# Dependency Graph Visualizer

Инструмент визуализации графа зависимостей для пакетов Alpine Linux (apk).

## Возможности

- Получение информации о зависимостях из репозитория Alpine Linux
- Построение полного графа зависимостей с учетом транзитивности
- Обработка циклических зависимостей
- Поиск обратных зависимостей
- Визуализация в формате D2 диаграмм
- Визуализация в виде ASCII дерева
- Тестовый режим для отладки

## Использование

```bash
python3 dependency_graph.py --package <имя> --repo <url|путь> [опции]
```

## Опции

- `--package` - Имя пакета для анализа (обязательно)
- `--repo` - URL репозитория или путь к тестовому файлу (обязательно)
- `--version` - Версия пакета (по умолчанию: latest)
- `--test-mode` - Использовать тестовый режим
- `--ascii-tree` - Вывод в виде ASCII дерева
- `--reverse` - Показать обратные зависимости

## Примеры

### Получение графа зависимостей (D2)
```bash
python3 dependency_graph.py --package curl --repo https://dl-cdn.alpinelinux.org/alpine/v3.19/main
```

### Визуализация в виде ASCII дерева
```bash
python3 dependency_graph.py --package git --repo https://dl-cdn.alpinelinux.org/alpine/v3.19/main --ascii-tree
```

### Обратные зависимости
```bash
python3 dependency_graph.py --package busybox --repo https://dl-cdn.alpinelinux.org/alpine/v3.19/main --reverse
```

### Тестовый режим
```bash
python3 dependency_graph.py --package A --repo test_repo_simple.txt --test-mode --ascii-tree
```

## Формат тестового репозитория

Тестовый файл содержит зависимости в формате:
```
A: B, C
B: D
C: D
D:
```

где A, B, C, D - имена пакетов (большие латинские буквы).

## Реализация

- Алгоритм обхода: BFS с рекурсией
- Обработка циклов: отслеживание посещенных узлов
- Парсинг APKINDEX: без использования сторонних библиотек
- Визуализация: D2 и ASCII дерево
