# Dependency Graph Visualizer

Tool for visualizing dependency graphs for Alpine Linux packages.

## Usage

```bash
python3 dependency_graph.py --package <name> --repo <url> [options]
```

## Options

- `--package` - Package name to analyze (required)
- `--repo` - Repository URL or path to test file (required)
- `--version` - Package version (default: latest)
- `--test-mode` - Use test repository mode
- `--ascii-tree` - Output as ASCII tree

## Examples

```bash
python3 dependency_graph.py --package python3 --repo https://dl-cdn.alpinelinux.org/alpine/v3.19/main --version 3.11.6-r0
```
