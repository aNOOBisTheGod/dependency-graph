#!/usr/bin/env python3

import argparse
import sys
import os
import urllib.request
import tarfile
import gzip
import tempfile
import ssl
from io import BytesIO
from collections import deque


def validate_package_name(name):
    if not name or not name.strip():
        raise ValueError("Package name cannot be empty")
    if not all(c.isalnum() or c in '-_.' for c in name):
        raise ValueError("Package name contains invalid characters")
    return name.strip()


def validate_url_or_path(value):
    if not value or not value.strip():
        raise ValueError("Repository URL or path cannot be empty")
    return value.strip()


def validate_version(version):
    if not version or not version.strip():
        raise ValueError("Version cannot be empty")
    return version.strip()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Dependency graph visualization tool for Alpine Linux packages'
    )
    
    parser.add_argument(
        '--package',
        type=str,
        required=True,
        help='Name of the package to analyze'
    )
    
    parser.add_argument(
        '--repo',
        type=str,
        required=True,
        help='Repository URL or path to test repository file'
    )
    
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Enable test repository mode'
    )
    
    parser.add_argument(
        '--version',
        type=str,
        default='latest',
        help='Package version (default: latest)'
    )
    
    parser.add_argument(
        '--ascii-tree',
        action='store_true',
        help='Output dependencies as ASCII tree'
    )
    
    parser.add_argument(
        '--reverse',
        action='store_true',
        help='Show reverse dependencies'
    )
    
    return parser.parse_args()


def fetch_apkindex(repo_url):
    index_url = f"{repo_url.rstrip('/')}/x86_64/APKINDEX.tar.gz"
    
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(index_url, timeout=30, context=ctx) as response:
            data = response.read()
        
        with tarfile.open(fileobj=BytesIO(data), mode='r:gz') as tar:
            apkindex_member = tar.getmember('APKINDEX')
            apkindex_file = tar.extractfile(apkindex_member)
            content = apkindex_file.read().decode('utf-8')
            
        return content
    except Exception as e:
        raise Exception(f"Failed to fetch APKINDEX: {e}")


def parse_apkindex(content):
    packages = []
    current_package = {}
    
    for line in content.split('\n'):
        line = line.strip()
        
        if not line:
            if current_package:
                packages.append(current_package)
                current_package = {}
            continue
        
        if ':' in line:
            key, value = line.split(':', 1)
            value = value.strip()
            
            if key == 'P':
                current_package['name'] = value
            elif key == 'V':
                current_package['version'] = value
            elif key == 'D':
                deps = []
                for dep in value.split():
                    dep_name = dep.split('=')[0].split('<')[0].split('>')[0]
                    if dep_name:
                        deps.append(dep_name)
                current_package['dependencies'] = deps
    
    if current_package:
        packages.append(current_package)
    
    return packages


def find_package(packages, name, version):
    for pkg in packages:
        if pkg.get('name') == name:
            if version == 'latest' or pkg.get('version') == version:
                return pkg
    return None


def get_dependencies(package_name, version, repo_url):
    content = fetch_apkindex(repo_url)
    packages = parse_apkindex(content)
    
    package = find_package(packages, package_name, version)
    
    if not package:
        raise Exception(f"Package {package_name} version {version} not found")
    
    return package.get('dependencies', [])


def load_test_repo(file_path):
    repo = {}
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split(':')
            if len(parts) >= 2:
                package = parts[0].strip()
                deps = [d.strip() for d in parts[1].split(',') if d.strip()]
                repo[package] = deps
    
    return repo


def get_test_dependencies(package_name, test_repo):
    return test_repo.get(package_name, [])


def build_dependency_graph_bfs(package_name, version, repo_url, test_mode, test_repo):
    graph = {}
    visited = set()
    queue = deque([package_name])
    
    while queue:
        current = queue.popleft()
        
        if current in visited:
            continue
        
        visited.add(current)
        
        if test_mode:
            deps = get_test_dependencies(current, test_repo)
        else:
            try:
                deps = get_dependencies(current, version, repo_url)
            except:
                deps = []
        
        graph[current] = deps
        
        for dep in deps:
            if dep not in visited:
                queue.append(dep)
    
    return graph


def build_dependency_graph_recursive(package_name, version, repo_url, test_mode, test_repo, graph=None, visited=None):
    if graph is None:
        graph = {}
    if visited is None:
        visited = set()
    
    if package_name in visited:
        return graph
    
    visited.add(package_name)
    
    if test_mode:
        deps = get_test_dependencies(package_name, test_repo)
    else:
        try:
            deps = get_dependencies(package_name, version, repo_url)
        except:
            deps = []
    
    graph[package_name] = deps
    
    for dep in deps:
        if dep not in visited:
            build_dependency_graph_recursive(dep, version, repo_url, test_mode, test_repo, graph, visited)
    
    return graph


def generate_d2_diagram(graph, package_name):
    lines = []
    lines.append(f"# Dependency graph for {package_name}")
    lines.append("")
    
    for package, deps in graph.items():
        if deps:
            for dep in deps:
                lines.append(f"{package} -> {dep}")
        else:
            lines.append(f"{package}")
    
    return "\n".join(lines)


def print_ascii_tree(graph, root, prefix="", is_last=True, visited=None):
    if visited is None:
        visited = set()
    
    if root in visited:
        print(f"{prefix}{'└── ' if is_last else '├── '}{root} (circular)")
        return
    
    visited.add(root)
    
    print(f"{prefix}{'└── ' if is_last else '├── '}{root}")
    
    deps = graph.get(root, [])
    for i, dep in enumerate(deps):
        is_last_dep = i == len(deps) - 1
        new_prefix = prefix + ("    " if is_last else "│   ")
        print_ascii_tree(graph, dep, new_prefix, is_last_dep, visited.copy())


def find_reverse_dependencies(target_package, repo_url, test_mode, test_repo):
    all_packages = []
    
    if test_mode:
        all_packages = list(test_repo.keys())
    else:
        content = fetch_apkindex(repo_url)
        packages = parse_apkindex(content)
        all_packages = [pkg['name'] for pkg in packages]
    
    reverse_deps = {}
    
    for package in all_packages:
        graph = build_dependency_graph_recursive(
            package,
            'latest',
            repo_url,
            test_mode,
            test_repo
        )
        
        if target_package in graph and target_package != package:
            reverse_deps[package] = graph.get(package, [])
    
    return reverse_deps


def print_config(args):
    print("Configuration parameters:")
    print(f"package: {args.package}")
    print(f"repo: {args.repo}")
    print(f"test_mode: {args.test_mode}")
    print(f"version: {args.version}")
    print(f"ascii_tree: {args.ascii_tree}")


def main():
    try:
        args = parse_arguments()
        
        args.package = validate_package_name(args.package)
        args.repo = validate_url_or_path(args.repo)
        args.version = validate_version(args.version)
        
        if args.test_mode and not os.path.exists(args.repo):
            raise FileNotFoundError(f"Test repository file not found: {args.repo}")
        
        test_repo = None
        if args.test_mode:
            test_repo = load_test_repo(args.repo)
        
        if args.reverse:
            reverse_deps = find_reverse_dependencies(
                args.package,
                args.repo,
                args.test_mode,
                test_repo
            )
            
            print(f"\nReverse dependencies for {args.package}:")
            print(f"Packages that depend on {args.package}:")
            if reverse_deps:
                for package in sorted(reverse_deps.keys()):
                    print(f"  - {package}")
            else:
                print("  No packages depend on this package")
        else:
            graph = build_dependency_graph_recursive(
                args.package,
                args.version,
                args.repo,
                args.test_mode,
                test_repo
            )
            
            if args.ascii_tree:
                print(f"\nASCII tree for {args.package}:")
                print_ascii_tree(graph, args.package)
            else:
                d2_diagram = generate_d2_diagram(graph, args.package)
                print(f"\nD2 diagram for {args.package}:")
                print(d2_diagram)
        
        return 0
        
    except ValueError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"File error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

