# ai-test-evaluator
Based on https://github.com/educc/ai-test-evaluator

The propmt.md has 6000 tokens aprox.

# Example Usage of the Enhanced Bench Command

## New `-n` Parameter

The bench command now supports an optional `-n` parameter to specify the number of iterations to run:

### Single iteration (default behavior):
```bash
python src/cli.py bench --model "your-model-name"
# or explicitly:
python src/cli.py bench --model "qwen/qwen3-1.7b" -n 1
```

### Multiple iterations:
```bash
# Run 3 iterations
python src/cli.py bench --model "qwen/qwen3-1.7b" -n 3

# Run 5 iterations
python src/cli.py bench --model "your-model-name" -n 5
```

## Expected Output for Multiple Iterations

When running with `-n 3`, you'll see output like:

```
Running benchmark with model: your-model-name
Prompt size: 12345 characters
Number of iterations: 3

============================================================
ITERATION 1/3
============================================================
Sending prompt to model (this may take a while for large prompts)...
Answer lines: [...]
Evaluating responses...
Q1: 100.00% - 'answer1' vs 'gold1'
Q2: 75.00% - 'answer2' vs 'gold2'
...
------------------------------------------------------------
Iteration 1 Score: 87.50%
Correct answers: 14/16

============================================================
ITERATION 2/3
============================================================
...
------------------------------------------------------------
Iteration 2 Score: 85.25%
Correct answers: 13/16

============================================================
ITERATION 3/3
============================================================
...
------------------------------------------------------------
Iteration 3 Score: 91.75%
Correct answers: 15/16

============================================================
FINAL RESULTS
============================================================
Individual iteration scores:
  Iteration 1: 87.50%
  Iteration 2: 85.25%
  Iteration 3: 91.75%
------------------------------------------------------------
Average Score: 88.17%
Model: your-model-name
Iterations: 3
Best Score: 91.75%
Worst Score: 85.25%
Score Range: 6.50%
```

## Benefits

- **Reliability**: Multiple runs help account for model variability
- **Statistics**: See min, max, average, and range of scores
- **Consistency**: Evaluate how consistent the model's performance is
- **Better evaluation**: More accurate assessment of model capabilities
