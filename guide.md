# Cipher

This is [a prompt](prompt.md) which evaluates LLMs on their instruction
following capability. The goal is to test one thing really well: can an LLM
strictly follow a long and complex set of instructions without deviation? The
[evaluation script](evaluator.py) does output fluid scores, but 100% is the
desired score for any LLM being evaluated.


This is a large prompt that requires an LLM to perform several tasks
simultaneously. At a high level, it evaluates:

- **Attention to Detail:** Can the model find specific, needle-in-a-haystack
  facts from a large body of text filled with irrelevant information?
- **Rule Hierarchy:** The prompt contains conflicting information from different
  sources. The model must follow a strict rule about which source supersedes all
  others to find the correct facts.
- **Calculation & Logic:** The model needs to retrieve numbers from the text and
  perform a few basic arithmetic operations.
- **Hallucinations:** It must correctly identify when a question cannot be
  answered from the text and output a specific "I don't know" string, resisting
  the urge to hallucinate an answer.
- **Strict Formatting:** The instructions include a list of very specific
  formatting rules for the output, covering dates, currency, percentages, units,
  abbreviations, and numerical counts.

The evaluation script simply takes the last 16 lines of the model's output
and compares it to the expected answer using Levenshtein distance.

## Results
Here are the results so far, sorted by score:

| Model                  | Score (%) | Notes                                                                                              |
| ---------------------- | --------- | ---------------------------------------------------------------------------------------------------|
| deepseek-r1            | 100.00    |                                                                                                    |
| gemini-2.5-flash-lite  | 100.00    |                                                                                                    |
| gemini-2.5-pro         | 100.00    |                                                                                                    |
| gpt-5-thinking-mini    | 100.00    |                                                                                                    | 
| gpt-oss-120b           | 100.00    |                                                                                                    |
| gpt-oss-20b            | 100.00    | It's just 21b!                                                                                     |
| grok-3                 | 100.00    |                                                                                                    |
| grok-4                 | 100.00    |                                                                                                    |
| gemma-3-27b            | 96.09     | Strong, but missed one formatting rule.                                                            |
| mistral-small-3.2      | 96.09     | Mistral's 24b model. Performed well, just one formatting error.                                    |
| qwen3-30b-a3b          | 96.09     | Qwen's open 30b MoE. Made the same single error as others in this tier.                            |
| gemma-3-12b            | 92.45     | Missed a formatting rule ("MB") and made one calculation error. Decent for its size.               |
| llama-3.3              | 89.16     | Meta's 70b model. Multiple formatting errors. Underwhelming                                        |
| llama-4-scout          | 85.69     | Similar formatting errors to Llama 3.3, plus one calculation mistake. Underwhelming.               |
| gemma-3-4b             | 74.82     | Struggled significantly with multiple calculation errors, formatting mistakes, and hallucinations. |
| gemma-3-1b             | 16.16     | A total failure to follow instructions. Ignored all formatting rules, and made numerous errors.    |

As expected, the large models from all labs got a perfect score. But, what
impressed me is _gpt-oss-20b_'s performance. It is in the size sweet spot for a
16GB GPU (test on _AMD RX 7600XT_) and yet reliably scores 100%.

Gemma 3 27B, Mistral Small and Qwen 3 30B failed to follow just one little
instruction and hence penalized.

## Evaluator
The [evaluation script](evaluator.py) can be used in multiple ways:
1. Run `python evaluator.py` and paste the output followed by a `Ctrl-D`
2. Run `python evaluator.py <path/to/llm/output>`
3. Pipe stdin to the evaluator: `cat <path/to/llm/output> | python evaluator.py`

For bulk evaluation, you can run:
```
ls results/* | xargs -I {} python evaluator.py {}
```
