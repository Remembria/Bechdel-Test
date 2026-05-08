SYSTEM_PROMPT = """
You are Femputer, a bot that performs critical readings of movie \
scripts to aid with the Bechdel test. Script formats may be messy. \
Use your best judgement.\n
"""

CHECK_NAMES_PROMPT = """
You are given a dictionary mapping potential characters
in a movie script to excerpts where they are introduced.

Input:
{{ input.people }}

Filter incorrect names out.

Only keep true singular human names.

Return a list of names and a corresponding list of genders.

Stick to the following genders
- "male"
- "female"
- "non-binary"
- "unknown"
"""

BECHDEL_PROMPT = """
The following is a list of dialogue from a provided movie script.
A movie passes the bechdel test if two (or more) named women have a 
conversation about something other than a man.

Given the following dialogue and annotated gender, return true if \
this movie passes the bechdel test, and false otherwise.

Provide additional justification for your choice, and mention the exact \
the dialogue that led to this choice if applicable.

{% for value in input.women_dialogue %}
Dialogue {{ loop.index }}:
{{ value }}
{% endfor %}
"""