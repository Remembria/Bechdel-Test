import json
import argparse
from pathlib import Path

def txt_to_json(filepath):
    """
    Creates a new .json file of format {text : <content of filepath>}
    
    :param filepath: A path to a .txt file of a movie script
    """
    txt_in = Path(filepath)

    if not txt_in.exists():
        print(f"Error: File '{txt_in}' not found.")
        return
    
    output_dir = Path("data/processed")
    json_out = output_dir / txt_in.with_suffix(".json").name

    output_dir.mkdir(parents=True, exist_ok=True)

    text_content = txt_in.read_text(encoding="utf-8")
    json_data = [{"text": text_content}]

    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)

    print(f"Successfully processed: {txt_in.name} -> {json_out}")

    return json_out

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert movie script .txt to .json for DocETL")
    parser.add_argument("input", help="Path to the raw .txt movie script")
    args = parser.parse_args()

    txt_to_json(args.input)