# First-pass checker output

Checked 25 September 2026 21:45 with the checker at the commit that archived these runs. These runs were made before three folder changes (see ../../evidence/RESULTS.md), and are kept unedited.

```
Checking runs/first-pass/accountant-yearend-call.json against inputs/accountant-yearend-call.txt
  shape        PASS
  trace        PASS
  speaker      PASS
  owner        PASS
  trigger      FAIL (6)
      - actions A3: the quote stops before the end of the sentence holding 'can you'; a condition or qualifier may have been cut
      - actions A4: the quote stops before the end of the sentence holding 'could you'; a condition or qualifier may have been cut
      - actions A5: the quote stops before the end of the sentence holding "i'll try"; a condition or qualifier may have been cut
      - actions A6: the quote stops before the end of the sentence holding 'can you'; a condition or qualifier may have been cut
      - actions A8: the quote stops before the end of the sentence holding "i'll"; a condition or qualifier may have been cut
      - actions A11: the quote stops before the end of the sentence holding 'can you'; a condition or qualifier may have been cut
  due          PASS
  coverage     PASS
  corrections  PASS

RESULT: FAIL

```

```
Checking runs/first-pass/pac-hmrc-2026-05-18.json against inputs/pac-hmrc-2026-05-18.txt
  shape        PASS
  trace        PASS
  speaker      PASS
  owner        PASS
  trigger      FAIL (1)
      - actions A2: the quote stops before the end of the sentence holding 'we will'; a condition or qualifier may have been cut
  due          PASS
  coverage     PASS
  corrections  PASS

RESULT: FAIL

```

```
Checking runs/first-pass/project-kickoff.json against inputs/project-kickoff.vtt
  shape        PASS
  trace        PASS
  speaker      PASS
  owner        PASS
  trigger      FAIL (1)
      - actions A1: the quote stops before the end of the sentence holding 'can you'; a condition or qualifier may have been cut
  due          PASS
  coverage     FAIL (1)
      - L0020: action trigger 'could someone' is neither cited nor listed in not_mapped (dropped)
      L0020 says: Could someone loop in our copywriter this week, she'll need the tone of voice doc?
  corrections  PASS

RESULT: FAIL

```

```
Checking runs/first-pass/quick-checkin.json against inputs/quick-checkin.txt
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

