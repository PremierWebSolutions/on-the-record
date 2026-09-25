# Field definitions

The machine-readable contract is [output-schema.json](output-schema.json). This page says what each field means. `not in source` is the only way to say a value is absent.

## Top level (always all present, always in this order)

| Field | Meaning |
|---|---|
| `translator` | Always `on-the-record`. |
| `version` | Always `1`. |
| `source.file` | The input file name as given. Must match the transcript this record is actually checked against, and — for a filed run — the run's own filename. |
| `source.last_line` | The id of the transcript's last numbered line, so a truncated read is visible. |
| `meeting` | Title, date, participants. |
| `actions` | Commitments, requests and hedges. |
| `decisions` | Lines where a decision phrase was said. |
| `figures` | Numbers as transcribed. |
| `questions` | Lines with a question mark. |
| `not_mapped` | Every worklist entry not used in a row, with a reason. |

## Fields every row shares

| Field | Meaning |
|---|---|
| `quote` | An exact, unbroken piece of the cited line's text. |
| `line` | The cited line, `L####`. |
| `speaker` | The cited line's speaker label, copied exactly. `(none)` for an unlabelled header line. |
| `corrections` | Ids from a user-supplied corrections file (`C001`…), or an empty list. |

## `meeting`

| Field | Meaning |
|---|---|
| `title` | `{quote, line, speaker}` from an unlabelled header line before anyone speaks — the cited line must come before the first line carrying a real speaker label — or `not in source`. |
| `date` | Same. The date exactly as written or said, never reformatted. |
| `participants` | Every speaker label in order of first appearance. |

## `actions[]`

| Field | Meaning |
|---|---|
| `id` | `A1`, `A2`… in transcript order. |
| `kind` | `committed`: the speaker takes it on. `requested`: the speaker asks someone else. `tentative`: the speaker hedges. |
| `trigger` | The entry from [triggers.md](triggers.md) that matched, exactly as listed there. |
| `owner` | `committed`/`tentative`: the speaker. `requested`: the speaker of the accepting line, or — with no acceptance — the addressee named as a sentence-opening vocative ("Tom, can you…"), exactly as spelled, or `not in source`. A name anywhere else in the sentence (a bystander, the object of the request, a date) is never an owner. |
| `due_as_said` | The due words as said ("by Friday"), or `not in source`. Never a calculated date. Never taken from words immediately preceded by a negation ("not", "n't", "never"), and always in the same sentence as the words that gave it. |
| `accepted_line` | For an accepted request: the next line by a different speaker. Otherwise `not in source`. |
| `accepted_quote` | The accepting words from that line. Otherwise `not in source`. |

## `decisions[]`

| Field | Meaning |
|---|---|
| `id` | `D1`, `D2`… |
| `trigger` | The decision phrase from [triggers.md](triggers.md), inside the quote. |

## `figures[]`

| Field | Meaning |
|---|---|
| `id` | `F1`, `F2`… |
| `token` | The number exactly as transcribed ("85k", "£1,412.50", "twenty percent"), inside the quote. Cited whole, never a fragment of a longer figure (a stray digit, a truncated thousands group, a dropped currency symbol, minus sign or decimal point). A spelled-out token is a whole word in its quote. |

## `questions[]`

| Field | Meaning |
|---|---|
| `id` | `Q1`, `Q2`… |

The quote includes the question mark. Whether the question was answered is not recorded.

## `not_mapped[]`

| Field | Meaning |
|---|---|
| `line` | The line the trigger is on. |
| `category` | `action`, `decision`, `figure` or `question`. |
| `trigger` | The trigger exactly as the index shows it. |
| `reason` | One of: `not_a_commitment` (also covers a trigger inside one of the fixed idioms in [triggers.md](triggers.md)), `hypothetical`, `reported_speech` (a reporting frame — "Tom said…" — or the trigger inside quotation marks), `repeat`, `not_a_decision`, `rhetorical`, `inaudible`, `label_or_reference`, `procedural`. |
| `see_line` | For `repeat`, the earlier line where it was recorded. Otherwise `not in source`. |

## What the contract has no place for

A summary, a sentiment, a priority, a suggested next step, a calendar date worked out from "Friday", a corrected spelling, an owner for a request nobody took. These are left out deliberately: if the schema had a field for them, one would eventually get filled.
