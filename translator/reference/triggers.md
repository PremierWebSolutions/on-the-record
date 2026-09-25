# Trigger phrases

This file is read by both the translator and the checker, so the two can never disagree about what counts. Each fenced block is one list. Matching is case-insensitive, treats curly and straight apostrophes as the same, and only matches whole words: `agreed` does not match inside `disagreed`.

A line that contains no trigger of a kind cannot produce a row of that kind. A line that does contain one must be accounted for: either a row cites it, or `not_mapped` lists it with a reason.

## Why these lists

Real commitments are rare in meetings. In a public release of the ICSI meeting corpus the dialogue-act tag for a speaker committing to a future action covers 0.34% of utterances, and action-item research annotates the owner as its own part of the utterance rather than guessing it from context. So the translator separates three things that summarisers blur together: a speaker taking something on (`committed`), a speaker asking someone else to (`requested`), and a speaker hedging (`tentative`). Sources are listed in [../../evidence/SOURCES.md](../../evidence/SOURCES.md).

## Actions

A speaker takes something on. The owner is that speaker.

```triggers:committed
i'll
i will
i'm going to
i am going to
we'll
we will
we're going to
we are going to
let me
leave it with me
i can do that
will do
```

A speaker asks someone else to do something. The owner is whoever the transcript shows accepting it, or the person named on the line, or `not in source`.

```triggers:requested
can you
could you
would you
will you
can someone
could someone
would someone
can somebody
could somebody
please
would you mind
i need you to
can we get
```

A speaker hedges. A hedge is never upgraded to a commitment: if a line has a tentative trigger, the action is `tentative` even if a committed trigger is also present.

```triggers:tentative
i'll try
i will try
i'll probably
i will probably
we'll probably
we will probably
we'll try
i'll see if
we'll see if
i might
we might
maybe i'll
maybe we'll
hopefully
i'll aim to
we'll aim to
i should be able to
we should be able to
```

## Acceptance

Used only for a `requested` action. The very next line spoken by a different speaker must contain one of these for that speaker to be recorded as the owner.

```triggers:acceptance
yes
yeah
yep
sure
okay
ok
will do
no problem
of course
i can do that
i'll do that
i'll do it
i'll sort that
```

## Decisions

```triggers:decision
agreed
we've agreed
we have agreed
let's go with
we'll go with
decided
we've decided
that's settled
go ahead
let's do that
```

## Questions

A line containing a question mark is a question line.

```triggers:question
?
```

## Figures

A figure is money, a percentage, a number with a thousands separator or a decimal point, or a number with a size word. Plain small integers, years and dates are not figures (a date that matters is caught through `due_as_said` on the action that carries it). The checker uses this exact pattern.

```pattern:figure
[£$€]\s?\d(?:[\d,]*\d)?(?:\.\d+)?(?:\s?(?:k|m|bn|billion|million|thousand)\b)?|\b\d(?:[\d,]*\d)?(?:\.\d+)?\s?(?:%|k\b|m\b|bn\b|billion\b|million\b|thousand\b|percent\b|per cent\b|pounds\b|pence\b|p\b|grand\b)|\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b|\b\d+\.\d+\b
```
