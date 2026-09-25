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
i'm on it
that's on me
count me in
consider it done
leave it to me
we shall
i'm gonna
we're gonna
i'd be happy to
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

A speaker uses one of these idioms. The words look like a commitment trigger but are not one: the trigger falling inside one of these phrases is never a commitment, request or hedge.

```triggers:idiom
i'll be honest
i'll be quick
i'll tell you what
we will see
we'll see
i'll say that
i will say
let me be clear
let me put it this way
let me think
```

This list is short on purpose and cannot be exhaustive — see [../../LIMITS.md](../../LIMITS.md).

## Acceptance

Used only for a `requested` action. The very next line spoken by a different speaker must contain one of these, or a `committed` trigger below, for that speaker to be recorded as the owner — and must contain none of the refusal markers, or the acceptance does not count. A bare "yes"/"okay" is not on this list: it accepts nothing on its own ("Yes, the office is open" and "Yes, but I can't do that" are both bare agreement, not a taken-on task).

```triggers:acceptance
will do
no problem
of course
i can do that
i'll do that
i'll do it
i'll sort that
leave it with me
consider it done
that's on me
leave it to me
```

A refusal anywhere in the accepting line means it is not an acceptance, whatever else is said.

```triggers:refusal
can't
cannot
won't
unable
not able
don't think i can
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
we're going with
we are going with
settled on
done deal
```

## Questions

A line containing a question mark is a question line.

```triggers:question
?
```

## Figures

A figure is money, a percentage, a number with a thousands separator (comma- or space-grouped) or a decimal point (including a leading-dot decimal like ".5%"), or a number with a size word. A leading minus sign is part of the figure. Plain small integers, years and dates are not figures (a date that matters is caught through `due_as_said` on the action that carries it). The checker uses this exact pattern.

```pattern:figure
[-−]?[£$€]\s?\d(?:[\d, ]*\d)?(?:\.\d+)?(?:\s?(?:k|m|bn|billion|million|thousand)\b)?|[-−]?(?:\b\d(?:[\d, ]*\d)?(?:\.\d+)?|(?<![\d.])\.\d+)\s?(?:%|k\b|m\b|bn\b|billion\b|million\b|thousand\b|percent\b|per cent\b|pounds\b|pence\b|p\b|grand\b)|[-−]?\b\d{1,3}(?:(?:,\d{3})+|(?:\s\d{3})+)(?:\.\d+)?\b|[-−]?\b\d+\.\d+\b
```

The checker also requires a digit-bearing `token` to be the *whole* figure on its cited line — not a fragment of a longer one (a stray digit, a truncated thousands group, a dropped currency symbol or minus sign, a dropped decimal). A spelled-out token (no digits) must still be a whole word inside its quote.
