"""
This module contains the core DocETL reasoning pipeline for running the Bechdel Test.
"""

from docetl.api import Pipeline, Dataset, MapOp, CodeMapOp, PipelineOutput, PipelineStep
import json
import argparse
from pathlib import Path
from create_json import txt_to_json
from prompts import SYSTEM_PROMPT, CHECK_NAMES_PROMPT, BECHDEL_PROMPT
from utils import extract_dialogue, filter_dialogue_for_women, show_result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Bechdel Test on a movie script.")
    parser.add_argument("input", help="Path to the input .txt file")
    args = parser.parse_args()

    in_file = Path(args.input)
    out_file = Path("results") / f"{in_file.stem}_bechdel.json"

    in_file_json = txt_to_json(in_file)

    datasets = {
        "transcripts": Dataset(
            type="file", 
            path=str(in_file_json)
        ),
    }


    operations = [
        CodeMapOp(
            name="extract_dialogue",
            type="code_map",
            code=extract_dialogue
        ),
        MapOp(
            name="get_gendered_names",
            type="map",
            prompt=SYSTEM_PROMPT + CHECK_NAMES_PROMPT,
            output={"schema": {
                "names" : "list[string]", 
                "genders" : "list[string]"
                }},
            enable_observability=False
        ),
        CodeMapOp(
            name="get_women_dialogue",
            type="code_map",
            code=filter_dialogue_for_women
        ),
        MapOp(
            name="bechdel",
            type="map",
            prompt=SYSTEM_PROMPT + BECHDEL_PROMPT,
            output={"schema": {
                "passes_bechdel" : "boolean", 
                "justification" : "string"
                }},
            enable_observability=False
        )
    ]

    steps = [
        PipelineStep(
            name="extraction_step",
            input="transcripts",
            operations=["extract_dialogue"]
        ),
        PipelineStep(
            name="filter_names_step",
            input="extraction_step",
            operations=["get_gendered_names"]
        ),
        PipelineStep(
            name="women_dialogue_step",
            input="filter_names_step",
            operations=["get_women_dialogue"]
        ),
        PipelineStep(
            name="test_step",
            input="women_dialogue_step",
            operations=["bechdel"]
        )
    ]

    output = PipelineOutput(
        type="file",
        path=str(out_file)
    )

    pipeline = Pipeline(
        name="bechdel_test",
        steps=steps,
        output=output,
        datasets=datasets,
        operations=operations,
        default_model="gemini/gemini-2.5-flash"
    )

    results = pipeline.run()

    with open(out_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for d in data:
        show_result(d)
        break
