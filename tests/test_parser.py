from validator.parser import parse_file
from pathlib import Path
import tempfile

def test_parse_json():
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as f:
        f.write('{"foo": "bar"}')
        f.flush()
        result = parse_file(Path(f.name))
        assert result["foo"] == "bar"

# Add more tests for HCL/YAML as needed
