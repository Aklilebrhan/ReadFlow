import json
import os
import sys

# Add apps/api to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "api")))

from app.main import app

def generate_openapi():
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "packages", "contracts", "openapi"))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "readflow-openapi.json")

    spec = app.openapi()
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)

    print(f"Successfully exported OpenAPI specification to {output_path}")

if __name__ == "__main__":
    generate_openapi()
