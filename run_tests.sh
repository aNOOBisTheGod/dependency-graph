#!/bin/bash

Этап 1 - Запуск с параметрами
python3 dependency_graph.py --package python3 --repo https://dl-cdn.alpinelinux.org/alpine/v3.19/main --version 3.11.6-r0

Этап 1 - Тест ошибки пустого имени
python3 dependency_graph.py --package "" --repo test 2>&1

Этап 1 - Тест ошибки несуществующего файла
python3 dependency_graph.py --package A --repo nonexistent.txt --test-mode 2>&1

Этап 2 - Прямые зависимости busybox
python3 dependency_graph.py --package busybox --repo https://dl-cdn.alpinelinux.org/alpine/v3.19/main

Этап 2 - Прямые зависимости python3
python3 dependency_graph.py --package python3 --repo https://dl-cdn.alpinelinux.org/alpine/v3.19/main

Этап 3 - Простой граф
python3 dependency_graph.py --package A --repo test_repo_simple.txt --test-mode

Этап 3 - Граф с циклами
python3 dependency_graph.py --package A --repo test_repo_cycles.txt --test-mode

Этап 3 - Сложный граф
python3 dependency_graph.py --package A --repo test_repo_complex.txt --test-mode

Этап 4 - Обратные зависимости D
python3 dependency_graph.py --package D --repo test_repo_simple.txt --test-mode --reverse

Этап 4 - Обратные зависимости E с циклами
python3 dependency_graph.py --package E --repo test_repo_cycles.txt --test-mode --reverse

Этап 4 - Обратные зависимости K
python3 dependency_graph.py --package K --repo test_repo_complex.txt --test-mode --reverse

Этап 5 - D2 диаграмма busybox
python3 dependency_graph.py --package busybox --repo https://dl-cdn.alpinelinux.org/alpine/v3.19/main

Этап 5 - ASCII дерево git
python3 dependency_graph.py --package git --repo https://dl-cdn.alpinelinux.org/alpine/v3.19/main --ascii-tree

Этап 5 - D2 диаграмма curl
python3 dependency_graph.py --package curl --repo https://dl-cdn.alpinelinux.org/alpine/v3.19/main

Этап 5 - ASCII дерево gnupg (большой граф)
python3 dependency_graph.py --package gnupg --repo https://dl-cdn.alpinelinux.org/alpine/v3.19/main --ascii-tree

Этап 5 - ASCII дерево с циклами
python3 dependency_graph.py --package A --repo test_repo_cycles.txt --test-mode --ascii-tree

Этап 5 - ASCII дерево сложный граф
python3 dependency_graph.py --package A --repo test_repo_complex.txt --test-mode --ascii-tree

Этап 5 - Генерация SVG для busybox
python3 dependency_graph.py --package busybox --repo https://dl-cdn.alpinelinux.org/alpine/v3.19/main | grep -v "^D2 diagram" > busybox.d2 && d2 busybox.d2 busybox.svg

Этап 5 - Генерация SVG для curl
python3 dependency_graph.py --package curl --repo https://dl-cdn.alpinelinux.org/alpine/v3.19/main | grep -v "^D2 diagram" > curl.d2 && d2 curl.d2 curl.svg

Этап 5 - Генерация SVG для тестового графа
python3 dependency_graph.py --package A --repo test_repo_complex.txt --test-mode | grep -v "^D2 diagram" > test_graph.d2 && d2 test_graph.d2 test_graph.svg

