# Lab 7: Fuzzing for Input Validation Bugs

**Student:** Nishanth Nag M V  
**SRN:** PES1UG24AM381

Source assignment: https://github.com/SETAPESU26/L6_L7_10_bus_transit_fare/tree/main/Lab%207

## Results

| Stage | Result |
| --- | --- |
| Original interactive application, malformed corridor | Crashes with ValueError; exit 1 |
| Original application, valid sample | Correct fare, concession and density; exit 0 |
| Three Hypothesis no-crash properties on original | 3 failed |
| Fixed application, same malformed inputs | Validation messages; exit 0 |
| Fixed application, valid sample | Original expected results; exit 0 |
| Same three Hypothesis properties on fixed | 3 passed |
| Complete updated test suite | 74 passed |

The full suite has six property-based tests and 68 explicit regression cases.
Each property is configured for up to 300 examples, with deterministic
generation, no persistent example database, and no timing deadline.
This is a bounded fuzzing exercise, not proof over every possible input.

## Run

```sh
python -m pip install -r requirements.txt
python processor.py
python -m pytest test_processor.py -q
```

To reproduce the expected failures in isolation without overwriting the fix:

```sh
python reproduce_before.py
```

This command is expected to exit with status 1. The original application is
preserved as `evidence/processor_before.py`. The final tests are used unchanged
against both the original and fixed versions.

## Input contract

- All helpers accept strings of at most 256 characters; invalid inputs return
  `None`. The CLI prints clear validation messages for that sentinel.
- Corridor: exactly `ORIGIN-DESTINATION-ZONES`; stop codes start with an ASCII
  letter and contain ASCII letters/digits; zones are positive ASCII integers.
  Surrounding field whitespace is allowed. Valid fare calculation remains
  `2.50 + 0.75 * zones` with the original formatted output.
- Concession: case-insensitive, surrounding whitespace ignored. Multipliers:
  STANDARD=1.00, STUDENT=0.50, SENIOR=0.35, MILITARY=0.20, CHILD=0.00.
  Unknown categories are rejected instead of silently assigned a discount.
- Density: exactly two float-parsable fields separated by `/`; passengers must
  be finite and nonnegative, kilometres finite and positive, and the resulting
  ratio finite. Output is rounded to two decimal places as before.

## Evidence

`evidence/` contains actual captured stdout/stderr, exit statuses, input values,
tool versions, the original processor, and terminal-style images. The images
use the supplied black/white reference style and the display-only prompt
`C:\Users\kolar\OneDrive\Desktop\SE\Lab\Lab7>`. Runs were executed under
Python 3.12 on Linux; the styled prompt does not claim Windows execution.
Full original Hypothesis tracebacks are retained; the concise failure image
shows the pytest summary. No pass/fail result has been invented or edited.

The PDF report includes the required before/after application and test evidence,
an analysis of the counterexamples, and the implemented validation policy.
