#!/usr/bin/env python3
"""
AI Test Evaluator CLI

A command-line interface for the AI Test Evaluator tool.
"""

import argparse
import sys
from typing import Optional
from llm_client import LMStudioClient


def list_models(base_url: Optional[str] = None) -> None:
    """List all available models from LM Studio."""
    try:
        client_kwargs = {}
        if base_url:
            client_kwargs['base_url'] = base_url
            
        with LMStudioClient(**client_kwargs) as client:
            models_response = client.get_models()
            
            if not models_response.data:
                print("No models available.")
                return
            
            print(f"Available models ({len(models_response.data)} total):")
            print("=" * 60)
            
            for i, model in enumerate(models_response.data, 1):
                print(f"{i:2d}. {model.id}")
                if model.owned_by != "unknown":
                    print(f"    Owner: {model.owned_by}")
                print()
                
    except Exception as e:
        print(f"Error listing models: {e}", file=sys.stderr)
        sys.exit(1)


def create_model_subparser(subparsers) -> None:
    """Create the model subcommand parser."""
    model_parser = subparsers.add_parser(
        'model',
        help='Model management commands'
    )
    
    model_parser.add_argument(
        '--list',
        action='store_true',
        help='List all available models'
    )
    
    model_parser.add_argument(
        '--base-url',
        type=str,
        default=None,
        help='Base URL for the LM Studio API (default: http://localhost:1234/v1)'
    )


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='AI Test Evaluator - A tool for evaluating AI models',
        prog='ai-test-evaluator'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        required=True
    )
    
    # Add model subcommand
    create_model_subparser(subparsers)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle model command
    if args.command == 'model':
        if args.list:
            list_models(args.base_url)
        else:
            print("No action specified for model command. Use --help for options.")
            sys.exit(1)


if __name__ == '__main__':
    main()