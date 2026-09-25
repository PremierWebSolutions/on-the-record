# Sources

### 1. Microsoft Teams Copilot Accuracy Disclaimers

Microsoft's Teams support documentation states that AI meeting recap content may be inaccurate or incomplete and advises verifying important details.

"AI-generated content might be missing key information and contain inaccurate content."

https://support.microsoft.com/en-us/teams/meetings-events/frequently-asked-questions-about-meeting-audio-recap

Checked 25 September 2026

### 2. Purver et al. 2006 Action-Item Annotation

Purver, Ehlen, and Niekrasz's 2006 work treats action-item components as separate annotated sub-parts: owner, description, timeframe, and agreement within a hierarchical annotation scheme.

"Four components of an action item – task description, owner, agreement, explicit timeframe."

https://www.researchgate.net/figure/Defining-an-action-item-by-classifying-multiple-utterances-with-dialog-subclasses_fig1_221250966

Checked 25 September 2026

### 3. Koenecke et al. 2024 Whisper Hallucinations

Koenecke et al. 2024 found approximately 1% of Whisper transcriptions contained hallucinated content, with 38% of those containing harmful material.

"Roughly 1% of audio transcriptions contained entire hallucinated phrases."

https://arxiv.org/abs/2402.08021

Checked 25 September 2026

### 4. Chartered Governance Institute Meeting Minutes Guidance

CGI guidance states that minutes should provide an accurate, impartial, and balanced record of business transacted.

"Provide an accurate, impartial and balanced internal record of the business transacted."

https://www.cgi.org.uk/media/mpjeexxj/minute-taking.pdf

Checked 25 September 2026

### 5. How rare commitments are in meetings

In a public release of the ICSI Meeting Recorder Dialogue Act (MRDA) corpus, the "commit" tag covers 371 utterances, 0.34% of the corpus. A figure of 0.24% that circulates in secondary summaries did not match the data, so it is not used here.

https://github.com/NathanDuran/MRDA-Corpus/blob/master/README.md

Checked 25 September 2026

## How these are used

Source 5 grounds the split between committed, requested and tentative actions in [../translator/reference/triggers.md](../translator/reference/triggers.md). Sources 1 and 3 are why mishearings are kept as heard and never silently corrected. Source 2 is why the owner is read off the utterance, never assumed. Source 4 is why the output records what was said and agreed rather than summarising it.
