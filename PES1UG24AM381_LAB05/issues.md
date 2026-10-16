# Static Code Analysis Issues Report

**Target Program:** `scholarship_disbursement.py`  
**Tools Used:** Bandit v1.9.4, Pylint v4.1.3, Flake8 v7.4.1  
**Author:** NISHANTH NAG M V (SRN: PES1UG24AM381)  

---

## Identified Issues Table

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| **SQL Injection Vector (B608)** | Vulnerability (Medium Severity / CWE-89) | 10 | The SQL query in `grant()` was constructed using string formatting (`% (student, scheme, amount)`). If untrusted user inputs are supplied for `student` or `scheme`, malicious SQL fragments can be injected and executed. | Replaced dynamic string formatting with parameterized SQL queries (`INSERT INTO awards (...) VALUES (?, ?, ?, 0)`) passing `(student, scheme, amount)` as a parameterized tuple. |
| **Shell Command Execution (B605, B607)** | Vulnerability (Low Severity / CWE-78) | 26 | `os.system("echo archiving awards")` invoked a system shell using a partial executable path. Shell execution introduces command injection attack surfaces and platform incompatibility. | Replaced shell execution via `os.system` with Python's built-in `print("archiving awards")` to achieve the intended output safely without spawning a shell. |
| **Broad Exception with Silent Pass (B110, W0718)** | Reliability / Quality (Bandit B110, Pylint W0718) | 27–28 | Catching overly broad `Exception` and silently suppressing it with `pass` hides critical runtime errors, diagnostic information, and unexpected process interruptions. | Caught the specific `OSError` exception and printed an informative failure message instead of silently passing. |
| **Mutable Default Argument (W0102)** | Bug / Logic Flaw (Pylint W0102) | 9 | The `grant()` function defined `audit=[]` as a default parameter. In Python, default parameter expressions are evaluated once at function definition time, meaning all invocations share the identical list instance across calls. | Changed the default value to `audit=None` and conditionally initialized a fresh list (`if audit is None: audit = []`) inside the function body. |
| **Global Variable Mutation (W0603, C0103)** | Maintainability / Design (Pylint W0603, C0103) | 6, 16 | Modifying `global disbursed_total` inside `disburse()` creates hidden dependencies and state side-effects. The variable name also violated naming conventions (C0103). | Replaced the mutable global accumulator with a database-backed aggregate query (`SELECT COALESCE(SUM(amount), 0) FROM awards WHERE disbursed = 1`) via `get_total_disbursed()`. |
| **Inconsistent Return Statements (R1710)** | Reliability / Logic (Pylint R1710) | 15–22 | `disburse()` explicitly returned `row[0]` when an award existed, but omitted a return statement when `row` was not found, resulting in implicit `None` returns. | Added an explicit `return None` at the end of `disburse()` to guarantee consistent, explicit control flow across all branches. |
| **Singleton Equality Comparison (C0121, E711)** | Style / PEP 8 (Pylint C0121, Flake8 E711) | 32 | `scheme == None` compared a singleton object (`None`) using value equality (`==`) rather than identity comparison (`is`). | Replaced `if scheme == None:` with PEP 8 compliant identity comparison `if scheme is None:`. |
| **Line Length Exceeding 79 Characters (E501, C0301)** | Style / PEP 8 (Flake8 E501, Pylint C0301) | 5, 10, 17, 19, 34 | Several lines exceeded the PEP 8 recommended maximum line length of 79 characters (with some lines reaching up to 130 characters). | Reformatted queries and statements across multiple lines using clean parenthesized wrapping. |
| **Function Naming Convention Violation (C0103)** | Style / PEP 8 (Pylint C0103) | 31 | `bySchemeCount()` used camelCase instead of standard Python snake_case (`by_scheme_count`). | Renamed the function to `by_scheme_count()` and added backward compatibility via module-level `__getattr__`. |
| **Missing Module & Function Docstrings (C0114, C0116)** | Documentation (Pylint C0114, C0116) | 1, 9, 15, 24, 31, 37 | The module and its exported functions lacked docstrings explaining their purpose, parameters, and return types. | Added comprehensive PEP 257 compliant docstrings to the module and all constituent functions. |

---

## Summary of Results

- **Bandit:** Reduced from 4 issues (1 Medium, 3 Low) down to **0 issues**.
- **Pylint:** Score improved from **5.00/10** to a perfect **10.00/10**.
- **Flake8:** Resolved all style and line-length warnings down to **0 errors**.
