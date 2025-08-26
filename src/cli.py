#!/usr/bin/env python3
"""
AI Test Evaluator CLI

A command-line interface for the AI Test Evaluator tool.
"""

import argparse
import logging
from pathlib import Path
import sys
from typing import Optional
from llm_client import LMStudioClient, Message, Role
from evaluator import match_line, GOLD

CUR_DIR = Path(__file__).resolve().parent

# setting logging with a format
logging.basicConfig(
    level=logging.INFO,
    # format="%(asctime)s - %(levelname)s - %(message)s"
    format="%(message)s"
)
log = logging.getLogger(__name__)



def list_models(base_url: Optional[str] = None) -> None:
    """List all available models from LM Studio."""
    try:
        client_kwargs = {}
        if base_url:
            client_kwargs['base_url'] = base_url
            
        with LMStudioClient(**client_kwargs) as client:
            models_response = client.get_models()
            
            if not models_response.data:
                log.info("No models available.")
                return

            log.info(f"Available models ({len(models_response.data)} total):")
            log.info("=" * 60)

            for i, model in enumerate(models_response.data, 1):
                log.info(f"{i:2d}. {model.id}")
                if model.owned_by != "unknown":
                    log.info(f"    Owner: {model.owned_by}")
                log.info("")  # Empty line for spacing
                
    except Exception as e:
        log.error(f"Error listing models: {e}")
        sys.exit(1)


def run_benchmark(model: str, base_url: Optional[str] = None, iterations: int = 1) -> None:
    """Run benchmark evaluation using the specified model."""
    try:
        # Read the prompt from prompt.md
        prompt_path = CUR_DIR / "prompt.md"
        if not prompt_path.exists():
            log.error(f"Prompt file not found: {prompt_path}")
            sys.exit(1)
            
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
        
        # Set up the client
        client_kwargs = {}
        if base_url:
            client_kwargs['base_url'] = base_url
            
        log.info(f"Running benchmark with model: {model}")
        log.info(f"Prompt size: {len(prompt_content)} characters")
        log.info(f"Number of iterations: {iterations}")
        
        # Use longer timeout for large prompts
        client_kwargs['timeout'] = 120  # 2 minutes timeout
        
        iteration_scores = []
        
        with LMStudioClient(**client_kwargs) as client:
            for iteration in range(1, iterations + 1):
                log.info("=" * 60)
                log.info(f"ITERATION {iteration}/{iterations}")
                log.info("=" * 60)
                
                # Create the message for the LLM
                messages = [Message(role=Role.USER, content=prompt_content)]
                
                # Get response from the model
                log.info("Sending prompt to model (this may take a while for large prompts)...")
                try:
                    response_content = client.simple_chat(
                        user_message=prompt_content,
                        model=model,
                        temperature=0.1
                    )
                except Exception as e:
                    log.error(f"Chat completion failed for iteration {iteration}: {e}")
                    log.error("This could be due to:")
                    log.error("1. Model context length limitations")
                    log.error("2. LM Studio server timeout")
                    log.error("3. Model not properly loaded")
                    raise

                log.debug(f"Received response from model: {response_content}")

                # Parse the response to extract Q1: through Q16: lines
                lines = response_content.strip().split('\n')
                answer_lines = []
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('Q') and ':' in line:
                        # Extract just the answer part after the colon
                        answer = line.split(':', 1)[1].strip()
                        answer_lines.append(line)

                log.debug(f"Answer lines are:\n{answer_lines}")

                # Take the last 16 answers (in case there are duplicates or extras)
                if len(answer_lines) >= len(GOLD):
                    answer_lines = answer_lines[-len(GOLD):]
                else:
                    log.warning(f"Only found {len(answer_lines)} answers, expected {len(GOLD)}")
                    # Pad with empty strings if needed
                    while len(answer_lines) < len(GOLD):
                        answer_lines.append("")
                
                # Evaluate using match_line
                log.info(f"Answer lines: {answer_lines}")
                log.info("Evaluating responses...")
                scores = []
                for i, (answer, gold) in enumerate(zip(answer_lines, GOLD), 1):
                    score = match_line((answer, gold))
                    scores.append(score)
                    log.info(f"Q{i}: {score:.2f}% - '{answer}' vs '{gold}'")
                
                # Calculate iteration score
                iteration_score = sum(scores) / len(scores) if scores else 0.0
                iteration_scores.append(iteration_score)
                
                log.info("-" * 60)
                log.info(f"Iteration {iteration} Score: {iteration_score:.2f}%")
                log.info(f"Correct answers: {sum(1 for s in scores if s == 100.0)}/{len(scores)}")
            
            # Calculate and display final results
            log.info("=" * 60)
            log.info("FINAL RESULTS")
            log.info("=" * 60)
            
            if len(iteration_scores) > 1:
                log.info("Individual iteration scores:")
                for i, score in enumerate(iteration_scores, 1):
                    log.info(f"  Iteration {i}: {score:.2f}%")
                log.info("-" * 60)
            
            average_score = sum(iteration_scores) / len(iteration_scores) if iteration_scores else 0.0
            log.info(f"Average Score: {average_score:.2f}%")
            log.info(f"Model: {model}")
            log.info(f"Iterations: {iterations}")
            
            if len(iteration_scores) > 1:
                min_score = min(iteration_scores)
                max_score = max(iteration_scores)
                log.info(f"Best Score: {max_score:.2f}%")
                log.info(f"Worst Score: {min_score:.2f}%")
                log.info(f"Score Range: {max_score - min_score:.2f}%")
            
    except Exception as e:
        log.error(f"Error running benchmark: {e}")
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


def create_bench_subparser(subparsers) -> None:
    """Create the bench subcommand parser."""
    bench_parser = subparsers.add_parser(
        'bench',
        help='Run benchmark evaluation with a specified model'
    )
    
    bench_parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Model name to use for the benchmark (required)'
    )
    
    bench_parser.add_argument(
        '--base-url',
        type=str,
        default=None,
        help='Base URL for the LM Studio API (default: http://localhost:1234/v1)'
    )
    
    bench_parser.add_argument(
        '-n',
        type=int,
        default=1,
        help='Number of iterations to run the benchmark (default: 1)'
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
    
    # Add bench subcommand
    create_bench_subparser(subparsers)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle model command
    if args.command == 'model':
        if args.list:
            list_models(args.base_url)
        else:
            print("No action specified for model command. Use --help for options.")
            sys.exit(1)
    
    # Handle bench command
    elif args.command == 'bench':
        run_benchmark(args.model, args.base_url, args.n)


if __name__ == '__main__':
    main()