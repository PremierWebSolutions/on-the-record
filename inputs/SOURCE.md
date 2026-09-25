# Where the inputs come from

## pac-hmrc-2026-05-18.txt: real, public, checkable

An excerpt of the House of Commons Public Accounts Committee's oral evidence session *Large business tax compliance* (HC 86), Monday 18 May 2026, with HMRC's chief executive and directors as witnesses.

- Publisher's copy: https://committees.parliament.uk/oralevidence/17594/html/
- Excerpt: the committee name and date from the page header, then questions 14 to 19 in full, one published paragraph per line.
- Fidelity: every line is the publisher's paragraph text byte for byte. The file's SHA-256 (`5cb66675eab0bc91b7302b932c3f5c76230e7dd49440e3c9b6fdf5bd160e9faa`) was matched against the same paragraphs hashed inside the publisher's page on 25 September 2026. Nothing within a line was changed.
- Why this one: a witness takes on a real follow-up ("we will have to write to you to give you the precise number"), is pressed for the figure, and gives only "in the hundreds". A translator that fills that number in has invented it.

Contains Parliamentary information licensed under the [Open Parliament Licence v3.0](https://www.parliament.uk/site-information/copyright-parliament/open-parliament-licence/).

## accountant-yearend-call.txt, project-kickoff.vtt, quick-checkin.txt: constructed

Written for this repo to carry the traps listed in [TRAPS.md](TRAPS.md). All people and businesses in them are fictional. They are modelled on real machine transcripts from an accountancy practice's client calls, which carry exactly these faults: the accounting package transcribed as "zero", a firm's name misheard, a date garbled into one that does not exist, and a correction made later in the call. The real calls are client-confidential and are not in this repo.

- `accountant-yearend-call.txt`: plain `Speaker: text` lines with a header, the format most meeting tools export as text.
- `project-kickoff.vtt`: WebVTT with `<v Speaker>` voice tags, the format Microsoft Teams and Zoom export, including a cue split over two lines and an "Unknown speaker".
- `quick-checkin.txt`: a short call with nothing to map, to show every section is still present and empty.
