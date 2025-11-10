# Примеры визуализации зависимостей

## Пример 1: busybox

### D2 диаграмма
```
python3 dependency_graph.py --package busybox --repo https://dl-cdn.alpinelinux.org/alpine/v3.19/main
```

Результат:
```
busybox -> so:libc.musl-x86_64.so.1
so:libc.musl-x86_64.so.1
```

Пакет busybox имеет минимальные зависимости - только основную библиотеку C (musl libc).

## Пример 2: git

### ASCII дерево
```
python3 dependency_graph.py --package git --repo https://dl-cdn.alpinelinux.org/alpine/v3.19/main --ascii-tree
```

Результат:
```
└── git
    ├── so:libc.musl-x86_64.so.1
    ├── so:libcurl.so.4
    ├── so:libexpat.so.1
    ├── so:libpcre2-8.so.0
    └── so:libz.so.1
```

Пакет git зависит от нескольких библиотек, но у них нет дальнейших зависимостей.

## Пример 3: curl

### D2 диаграмма с транзитивными зависимостями
```
python3 dependency_graph.py --package curl --repo https://dl-cdn.alpinelinux.org/alpine/v3.19/main
```

Результат показывает более сложный граф:
- curl зависит от libcurl
- libcurl зависит от ca-certificates
- ca-certificates имеет свои зависимости

Это демонстрирует транзитивные зависимости и построение полного графа.

## Сравнение с apk info

Стандартная утилита `apk info` показывает только прямые зависимости:
```bash
apk info -R curl
```

Наш инструмент строит полный граф с учетом транзитивных зависимостей, что позволяет увидеть всю цепочку зависимостей.

Различия могут возникать из-за:
1. Версий пакетов - наш инструмент использует версию 'latest' по умолчанию
2. Виртуальных пакетов - некоторые зависимости могут быть виртуальными (so:*)
3. Опциональных зависимостей - мы учитываем только обязательные зависимости из поля 'D' в APKINDEX

