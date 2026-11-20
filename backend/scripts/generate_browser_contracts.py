"""Generate browser types/schema from frozen protocol v1; verify with --check."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def ts_type(schema):
    if "$ref" in schema:
        return schema["$ref"].split("/")[-1]
    if "const" in schema:
        return json.dumps(schema["const"])
    if "enum" in schema:
        return " | ".join(json.dumps(x) for x in schema["enum"])
    for union in ("anyOf", "oneOf"):
        if union in schema:
            return "(" + " | ".join(ts_type(x) for x in schema[union]) + ")"
    kind = schema.get("type")
    if kind == "array":
        return "Array<" + ts_type(schema["items"]) + ">"
    if kind == "object":
        fields = []
        for key, value in schema.get("properties", {}).items():
            optional = "" if key in schema.get("required", []) else "?"
            fields.append(f"  {key}{optional}: {ts_type(value)};")
        return "{\n" + "\n".join(fields) + "\n}"
    return {
        "string": "string",
        "integer": "number",
        "number": "number",
        "boolean": "boolean",
        "null": "null",
    }.get(kind, "unknown")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    raw = (ROOT / "contracts/protocol-v1.schema.json").read_bytes()
    schema = json.loads(raw)
    types = (
        "// Generated from frozen protocol v1. Run python -m scripts.generate_browser_contracts.\n"
    )
    types += "\n".join(
        f"export type {name} = {ts_type(value)};\n"
        for name, value in sorted(schema["$defs"].items())
    )
    types += "export type Event = ResponseEvent | LessonEvent;\n"
    outputs = {"protocol.json": raw, "types.ts": types.encode()}
    for name, content in outputs.items():
        path = ROOT / "frontend/lib/generated" / name
        if args.check:
            if not path.exists() or path.read_bytes() != content:
                raise SystemExit("Browser contracts differ from frozen protocol")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(
        "Browser protocol types/schema verified." if args.check else "Browser contracts generated."
    )


if __name__ == "__main__":
    main()
