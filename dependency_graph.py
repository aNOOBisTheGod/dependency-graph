#!/usr/bin/env python3

import argparse
import sys
import os


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
        
        print_config(args)
        
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

