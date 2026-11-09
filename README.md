# AI Email Intake Automation

A race-registration pipeline that reads free-text emails, uses an LLM to pull out the key details, checks them with deterministic Python, registers valid runners, and writes a tailored reply to every sender.

The LLM only **extracts**. Every decision, such as whether a registration is valid, is made by plain Python rules.

## How it works

The program reads a simulated inbox (`emails.txt`, one email per line). For each email it:

1. **Extracts** the runner's full name, race distance, and requested date with the OpenAI API (`gpt-4o-mini`), which returns a JSON object.
2. **Validates** the extracted data in Python against a hard-coded schedule of 16 races (four distances, four races each).
3. **Registers** the runner on the correct race roster if everything checks out.
4. **Replies** with a personalized confirmation, or a rejection that explains every problem found. If the distance and date don't match but other races run on that date, the reply lists them.

After all emails are processed, it prints a schedule table for each distance with its registrants, and writes every reply to `outbox.txt`.

## The role of AI in this project

- The LLM turns free text into a JSON object (`full_name`, `race_distance`, `race_date`). It does not validate anything and cannot register anyone.
- Validation and registration are deterministic Python. LLMs are unreliable at following exact business rules, and keeping the rules outside the model makes them testable and predictable.
- The model's output is treated as untrusted input:
  - If it isn't valid JSON, the fields are treated as missing instead of crashing the run.
  - Dates are re-parsed and rewritten as `mm/dd/yyyy` in Python, so the result doesn't depend on how the model formats them (`5/13/2026` and `05/13/2026` behave the same).

## Validation checks

Each failed check adds its own message to the reply, so one email can produce several.

| # | Check | Fails when |
|---|-------|------------|
| 1 | Name provided | No name is found |
| 2 | Full name | Only one name is given |
| 3 | Name length | One of the first two name parts is a single character |
| 4 | Valid distance | Distance isn't 5K, 10K, Half Marathon, or Marathon |
| 5 | Date provided | No date is found |
| 6 | Real date | The date can't be parsed (for example `02/30/2026`) |
| 7 | Race exists on date | No race of any distance runs on that date |
| 8 | Distance matches date | Races exist on that date, but not at the requested distance |

## Example

**Email**

> Hello, my name is Robert Kim and I want to run the Thanksgiving 10K on 5/13/2026.

**Reply** (the date and distance don't match, so alternatives are offered)

```
Dear Robert Kim,
Sorry, there are no 10K races on 05/13/2026. Here are specific race(s) taking place on the date you entered:
- Spring 5K
Let us know if you would be interested in registering for any of these races!
Thank You,
Race Registration
```

**Email**

> Hi there, this is Maria Gonzalez. Please sign me up for the Spring 5K on 05/13/2026. Thank you!

**Reply**

```
Dear Maria Gonzalez,
You have successfully registered for the Spring 5K on 05/13/2026. We look forward to seeing you there!
Thank You,
Race Registration
```

`emails.txt` has 30 sample emails (fictional names) covering valid requests, missing or partial names, unsupported distances (15K, ultramarathon), missing dates, dates with no race, and distance/date mismatches. The full output is in `outbox.txt`.

## Running it

```bash
pip install -r requirements.txt
python automation.py
```

1. You need an OpenAI API key (see [Platform OpenAI](https://platform.openai.com/home) or this [tutorial](https://info2951.infosci.cornell.edu/tutorials/openai-key.html)).
2. Copy `sk_example.py` to `sk.py` and put your key in it. `sk.py` is listed in `.gitignore` and is not included in this repository.

## Files

- `automation.py`: the main pipeline
- `emails.txt`: sample registration emails (valid and invalid)
- `outbox.txt`: the generated replies
- `sk_example.py`: template for your API key file
- `requirements.txt`: Python dependencies

## Limitations

- The race schedule is hard-coded sample data, and **past dates are accepted** (most sample races are earlier in 2026).
- Only the first two parts of a name are length-checked, so a name like "Mary J Watson" passes while a single-letter first name is rejected.
- The extraction prompt strips punctuation from names, so a name like O'Connor loses its apostrophe.
- Each email is processed with one API call, with no retries if a call fails.
- Duplicate registrations for the same person and race aren't detected.
- When a date is missing, the reply asks for one but doesn't suggest dates, even if the email named a specific race.
