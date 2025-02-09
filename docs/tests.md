---
title: Tests
---

Here is how we can run tests for this project. This will be used to make the project spec compliant and measure our goals on how to acheive the spec.

## Setup

First install the declo project in editable mode for this environment.

```bash
uv pip install -e .
```

## Running tests

Run the script in tests 
| Need to simplify this command
```bash
uv run tests/cli.py test
```

You should see the output like this:
```bash
Example 10:

Example: Double Values
╭──────────── Declo Code ────────────╮ ╭──────────── Python Code ────────────╮
│                                    │ │                                     │
│   1 nums = [1, 2, 3, 4, 5]         │ │   1 nums = [1, 2, 3, 4, 5]          │
│   2 doubles = nums.map(x => x * 2) │ │   2 doubles = [x * 2 for x in nums] │
│                                    │ │                                     │
╰────────────────────────────────────╯ ╰─────────────────────────────────────╯

Testing Steps:
✓ Compilation successful - output matches expected Python
╭───────────────────────────────────────────────────────────── Compiled Python ─────────────────────────────────────────────────────────────╮
│   1 nums = [1, 2, 3, 4, 5]                                                                                                                │
│   2 doubles = [x * 2 for x in nums]                                                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
✓ Decompilation successful
╭──────────────────────────────────────────────────────────── Decompiled Declo ─────────────────────────────────────────────────────────────╮
│   1 nums = [1, 2, 3, 4, 5]                                                                                                                │
│   2 doubles = nums.map(x => x * 2)                                                                                                        │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
✓ Roundtrip successful

Test Summary:
                Failure Statistics                
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Test Type     ┃ Failed Examples ┃ Success Rate ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ Compilation   │ 1 (8)           │ 90.0%        │
│ Decompilation │ None            │ 100.0%       │
│ Roundtrip     │ 2 (3, 5)        │ 80.0%        │
└───────────────┴─────────────────┴──────────────┘
```

