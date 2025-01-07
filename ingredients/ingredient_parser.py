import subprocess
import tempfile
from typing import List
from ingredient_phrase_tagger.training import utils

def parse_ingredients_crf(ingredient_lines: List[str], model_path: str) -> List[dict]:
    """Parse ingredient lines using the CRF model and return structured data."""
    crf_output = _exec_crf_test(ingredient_lines, model_path)
    return utils.import_data(crf_output.split('\n'))

def _exec_crf_test(input_text, model_path):
    
    """Execute CRF++ test with the given input and model."""
    with tempfile.NamedTemporaryFile(mode='w') as input_file:
        input_file.write(utils.export_data(input_text))
        input_file.flush()
        return subprocess.check_output(
            ['crf_test', '--verbose=1', '--model', model_path,
             input_file.name]).decode('utf-8') 