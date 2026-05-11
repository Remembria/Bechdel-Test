"""
Contains util functions for both the pipeline, and pretty print used by run_bechdel.py
"""

from rich.console import Console
from rich.panel import Panel

def extract_dialogue(doc: dict) -> dict:
    """
    Uses a combination of indentation and regex to extract conversations
    from a movie script. 
    
    The output is a list of dialogue strings.
    """
    import re

    def get_indentation(line):
        """Returns the number of leading spaces (indentation level)."""
        return len(line) - len(line.lstrip(' '))

    def list_hamming_distance(s1, s2):
        """Returns the hamming distance between two lists"""
        if len(s1) != len(s2):
            raise ValueError("Lists must have equal length")

        return sum(el1 != el2 for el1, el2 in zip(s1, s2))

    def get_sections(text):
        """
        Splits the text into a list of sections, where 
        each section corresponds to a contiguous element of the 
        script (e.g. one section for dialogue, one section for 
        stage directions, etc)
        """
        sections = []
        current_section = []

        prev_indent = None

        for raw_line in text.splitlines():
            line = raw_line.rstrip("\n")

            # Check for blank lines
            if line.strip() == "":
                if current_section:
                    sections.append("\n".join(current_section))
                    current_section = []
                prev_indent = None
                continue

            indent = get_indentation(line)

            # Start a new section if first line or indentation increases
            if prev_indent is not None and indent < prev_indent:
                if current_section:
                    sections.append("\n".join(current_section))
                    current_section = []

            current_section.append(line)
            prev_indent = indent

        if current_section:
            sections.append("\n".join(current_section))

        return sections

    def get_name_mentions(name_list, text, max_context_size=500):
        """
        Returns a dictionary of format 
        {<name> : <excerpt of first instance mentioned in text>}
        """

        names = list(set(name_list))
        name_dict = {}
        for n in names:
            match = re.search(rf'[\s].*{n}.*[\s\.]', text, re.IGNORECASE)
            if match:
                name_dict[n] = " ".join(match.group().split())[:max_context_size]

        return name_dict

    def retrieve_dialogue(dialogue_sections, merged_sections):
        """
        Merges contiguous dialogue in merged_sections to create
        a list of conversations
        """
        dialogue = []
        c = -2
        cd = ""
        for i in dialogue_sections:
            if i != c + 1:
                if cd != "":
                    dialogue.append(cd)
                cd = merged_sections[i]
                c = i
            else:
                cd += "\n" + merged_sections[i]
                c += 1

        return dialogue

    text = doc["text"]
    sections = get_sections(text)

    name_limit = 5 # Merged names must be less than or equal to name_limit words
    hamming_limit = 2 # Merged names only hamming_limit words can be uncapitalized

    name_start = r'^(?:[A-Z]{3,10}\s?){0,3}[\n:]'

    name_list = []
    dialogue_sections = []
    merged_sections = []
    joined_section = ""
    for s in sections:
        if len(s.split()) <= name_limit and list_hamming_distance(s.upper(), s) <= hamming_limit:
            joined_section += s + "\n"
            name_list.append(s.strip())
        else:
            names = re.findall(name_start, s.strip(), flags=re.MULTILINE)
            if joined_section != "" or names:
                dialogue_sections.append(len(merged_sections))
            if names:
                name_list.extend(list(map(lambda x: x.strip(), names)))

            joined_section += s
            merged_sections.append(joined_section)
            joined_section = ""


    # Retrieve the dialogue alone
    dialogue = retrieve_dialogue(dialogue_sections, merged_sections)

    # Remove redundant spaces from dialogue to lower token count for LLMs later
    dialogue = list(map(lambda d : " ".join(filter(lambda x: x != '', d.split(" "))), dialogue))

    # Retrieve the first mention of each name
    name_dict = get_name_mentions(name_list, text)

    return {"people": name_dict, "dialogue": dialogue}

def filter_dialogue_for_women(doc: dict) -> dict:
    """
    Removes dialogue where no women are present.
    """

    names = doc["names"]
    genders = doc["genders"]

    assert len(names) == len(genders)

    gender_dict = dict(zip(names, genders))

    name_set = set(gender_dict)

    filtered_dialogue = []

    for d in doc["dialogue"]:
        wcount = 0
        tagged_d = d
        for name in name_set:
            if name in d: 
                tagged_d = tagged_d.replace(name, f'{name} ({gender_dict[name]})')
                if gender_dict[name] == "female":
                    wcount += 1

        # At least one woman in the conversation
        if wcount >= 1:
            filtered_dialogue.append(tagged_d)

    return {"women_dialogue": filtered_dialogue}

def show_result(d):
    """
    Creates a colour output for test results
    
    :param d: Dictionary with keys "passes_bechdel" and "justification"
    """

    console = Console()
    result = "Pass" if d["passes_bechdel"] else "Fail"
    status_color = "green" if d["passes_bechdel"] else "red"
    panel_content = f"[bold {status_color}]{result}[/bold {status_color}]" + \
                    f"\n\n[bold {status_color}]{d['justification']}[/bold {status_color}]"
    console.print(Panel(panel_content, title="Bechdel Test Result"))
