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
        
        if not args.test_mode:
            dependencies = get_dependencies(args.package, args.version, args.repo)
            
            print(f"\nDirect dependencies for {args.package}:")
            if dependencies:
                for dep in dependencies:
                    print(f"  - {dep}")
            else:
                print("  No dependencies")
        
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

