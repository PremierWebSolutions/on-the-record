# Second-pass checker output

Checked 25 September 2026 23:30 with the checker after the two red-team rounds. These runs were made blind under the rules as they stood before the rounds (quotes could start late, the lexicon was nine phrases shorter) and are kept unedited. The failures below are the new gates working on old outputs: a quote that starts mid-sentence, and a decision the old lexicon could not see.

## accountant-yearend-call
```
  shape        PASS
  trace        PASS
  speaker      FAIL (1)
      - questions Q4: L0032 is spoken by 'Tom Hartley', the row says 'Priya Nair'
  owner        PASS
  trigger      FAIL (8)
      - actions A1: the quote is not the whole sentence holding "i'll" (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A4: the quote is not the whole sentence holding "we'll" (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A6: the quote is not the whole sentence holding "we'll" (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A9: the quote is not the whole sentence holding "i'll" (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A10: the quote is not the whole sentence holding "i'll" (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A13: the quote is not the whole sentence holding "i'll" (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A15: the quote is not the whole sentence holding "i'll" (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A17: the quote is not the whole sentence holding "i'll" (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
  due          PASS
  coverage     FAIL (1)
      - L0085: decision trigger "we're going with" is neither cited nor listed in not_mapped (dropped)
      L0085 says: So to sum up, turnover eighty-five thousand pounds near enough, we're going with the cash basis, stove installs are zero-rated not exempt, and I need the payroll summary today and the stove invoice from Tom.
  corrections  PASS

RESULT: FAIL

```

## haiku-accountant-yearend-call
```
  shape        PASS
  trace        PASS
  speaker      FAIL (1)
      - questions Q4: L0032 is spoken by 'Tom Hartley', the row says 'Priya Nair'
  owner        PASS
  trigger      FAIL (8)
      - actions A1: the quote is not the whole sentence holding "i'll" (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A4: the quote is not the whole sentence holding "we'll" (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A6: the quote is not the whole sentence holding "we'll" (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A9: the quote is not the whole sentence holding "i'll" (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A10: the quote is not the whole sentence holding "i'll" (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A13: the quote is not the whole sentence holding "i'll" (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A15: the quote is not the whole sentence holding "i'll" (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A17: the quote is not the whole sentence holding "i'll" (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
  due          PASS
  coverage     FAIL (1)
      - L0085: decision trigger "we're going with" is neither cited nor listed in not_mapped (dropped)
      L0085 says: So to sum up, turnover eighty-five thousand pounds near enough, we're going with the cash basis, stove installs are zero-rated not exempt, and I need the payroll summary today and the stove invoice from Tom.
  corrections  PASS

RESULT: FAIL

```

## haiku-pac-hmrc-2026-05-18
```
  shape        PASS
  trace        PASS
  speaker      PASS
  owner        PASS
  trigger      FAIL (4)
      - actions A2: the quote is not the whole sentence holding 'we will' (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A3: the quote is not the whole sentence holding 'we will' (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A6: 'we will' lies inside the idiom 'we will see', not a commitment; file it in not_mapped as not_a_commitment instead
      - questions Q3: the quote is not the whole question (must run from the sentence start to its '?')
  due          PASS
  coverage     PASS
  corrections  PASS

RESULT: FAIL

```

## pac-hmrc-2026-05-18
```
  shape        PASS
  trace        PASS
  speaker      PASS
  owner        PASS
  trigger      FAIL (4)
      - actions A2: the quote is not the whole sentence holding 'we will' (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A3: the quote is not the whole sentence holding 'we will' (must run from sentence start to sentence end, so a negation or a condition can't be cut off)
      - actions A6: 'we will' lies inside the idiom 'we will see', not a commitment; file it in not_mapped as not_a_commitment instead
      - questions Q3: the quote is not the whole question (must run from the sentence start to its '?')
  due          PASS
  coverage     PASS
  corrections  PASS

RESULT: FAIL

```

## project-kickoff
```
  shape        PASS
  trace        PASS
  speaker      PASS
  owner        PASS
  trigger      PASS
  due          PASS
  coverage     PASS
  corrections  PASS

RESULT: PASS, every value traces to its line and speaker

```

## quick-checkin
```
  shape        PASS
  trace        PASS
  speaker      PASS
  owner        PASS
  trigger      PASS
  due          PASS
  coverage     PASS
  corrections  PASS

RESULT: PASS, every value traces to its line and speaker

```

