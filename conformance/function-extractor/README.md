# function-extractor

The `function` method. `expected.json` lists the extractor the case needs under `requiresExtractors`, with its contract in prose; a reader's test harness registers an implementation under that key before running the case.

What it checks:

- The registry-key call contract: `(fullPath, levelName, dataLocationIdentifier)` → typed value or null.
- A null return with no `defaultValue` → field absent, `extraction-failed`.
- A reader that has **not** registered the key must not fail silently: it emits `unresolved-extractor` on every record the rule applies to, with the field absent. A harness without the extractor should skip this case rather than compare records.
