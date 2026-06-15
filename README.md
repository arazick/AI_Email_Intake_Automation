# AI_Email_Intake_Automation
This is an automated email-processing system that reads free-text race registration requests, extracts the relevant details with an LLM, validates them against a set of races using deterministic Python, registers valid runners, and replies to each sender with a tailored confirmation or rejection. It also outputs schedule tables after the registration requests have been processed
The program reads a simulated inbox (emails.txt, one registration email per line). For each email it:
  1. Extracts the runner's full name, race distance, and requested date using the OpenAI API, which
     returns a structured JSON object.
  2. Validates that data against its own rules: is the name complete, is the distance one that's         offered, is the date real, and does the requested distance actually run on that date?
  3. Registers the runner by adding their name to the correct race roster when everything checks
     out.
  4. Replies with a personalized message - a confirmation on success, or a specific rejection            (w/suggested dates) explaining what exactly was wrong

## The Role of AI In This Project
- The LLM's only role is to extract relevant information that is laid out in its given instructions and turning the free-text into a clean JSON object. It does not check validity or make any decisions.
- The decisions and validity checking occurs in deterministic Python.
- LLMs are unreliable for following deterministic rules and pose a security and logical risk.

## Validation Logic
- A registration is only valid when all three of these are true:
  1. The name has at least two whitespace-separated parts (full name), where each part must contain
     at least two characters
  2. The distance is one of: 5K, 10K, Half Marathon, Marathon
  3. The distance, date pair points to a real race
- Each failure produces its own specific message

## Running it
```bash
pip install openai tabulate
py automation.py
```
- You will need an OpenAI API key. The script imports it from a local sk.py file that is not included in this repository (see sk_example.py)

## Files
- automation.py: the main pipeline
- emails.txt: sample registration emails (valid and invalid)
- sk_example.py: template for your API key file
- outbox.txt: the generated replies to the emails (confirmation/rejection messages)
