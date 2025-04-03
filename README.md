# Surgical Phase Classification Evaluation

This tool evaluates the accuracy of a surgical phase classification model by comparing the predicted phase labels with the ground truth labels.

## ORM
in swift default settings, the string "accuracy" directly maps to the MathAccuracy class.
refer to ms-swift/swift/plugin/orm.py
Similarly, the string "format" maps to the Format class (which is defined in this second snippet).

Note that mathacc cannot be used in our case, as explained by gemini. And our results show the mathacc rewards remains 1 during the training.

If the solution (ground truth) cannot be parsed into a valid mathematical expression by math_verify.parse, the ORM assigns a reward of 1.0. This essentially skips the example, assuming the ground truth format is incorrect or not what the verifier expects, thus avoiding penalizing the model for an issue with the benchmark data itself.

## Features

- Calculates overall accuracy
- Computes per-class precision, recall, and F1-scores
- Generates a confusion matrix
- Provides macro and weighted averages of metrics
- Handles normalization of phase labels (case-insensitive, ignores whitespace, etc.)
- Option to save results in JSON format
- Option to save incorrect predictions to a separate file

## Usage

```
python evaluate_accuracy.py [input_file] [options]
```

### Arguments

- `input_file`: Path to the JSONL file containing predictions and ground truth labels

### Options

- `--output`, `-o`: Path to save results in JSON format
- `--verbose`, `-v`: Show detailed information including incorrect predictions
- `--debug`, `-d`: Show debug information including normalized labels
- `--output_failure`: Path to save full details of incorrect predictions in JSONL format

### Input File Format

The input file should be in JSONL format with each line containing a JSON object with at least the following fields:

```json
{
  "response": "The phase is CleaningCoagulation",
  "labels": "The phase is Cleaning Coagulation"
}
```

The script will ignore the "The phase is" prefix, case differences, and whitespace when comparing labels.

## Examples

### Basic Usage

```bash
python evaluate_accuracy.py predictions.jsonl
```

### Save Results to JSON

```bash
python evaluate_accuracy.py predictions.jsonl --output results.json
```

### Show Incorrect Predictions

```bash
python evaluate_accuracy.py predictions.jsonl --verbose
```

### Save Incorrect Predictions

```bash
python evaluate_accuracy.py predictions.jsonl --output_failure incorrect.jsonl
```

### Debug Mode

```bash
python evaluate_accuracy.py predictions.jsonl --debug
```

## Normalization Process

The script normalizes the phase labels in the following ways:

1. Removes the prefix "The phase is" (case-insensitive)
2. Converts the text to lowercase
3. Removes all whitespace

This ensures accurate comparison regardless of formatting differences.

## Output Example

```
Overall Accuracy: 0.6000 (3/5)

Per-Class Metrics:
Class            Precision     Recall   F1-Score    Support
------------------------------------------------------------
CalotTriangleDi     0.5000     1.0000     0.6667          1
Cleaning Coagul     0.6667     1.0000     0.8000          2
Gallbladder Dis     0.0000     0.0000     0.0000          1
Preparation         0.0000     0.0000     0.0000          1
------------------------------------------------------------
Macro Average       0.2917     0.5000     0.3667          5
Weighted Average     0.3667     0.6000     0.4533          5

Confusion Matrix:
True\Pred | CalotTrian | Cleaning C | Gallbladde | Preparatio
-------------------------------------------------------------
CalotTrian |   1 (100.0%) |   0 ( 0.0%) |   0 ( 0.0%) |   0 ( 0.0%)
Cleaning C |   0 ( 0.0%) |   2 (100.0%) |   0 ( 0.0%) |   0 ( 0.0%)
Gallbladde |   1 (100.0%) |   0 ( 0.0%) |   0 ( 0.0%) |   0 ( 0.0%)
Preparatio |   0 ( 0.0%) |   1 (100.0%) |   0 ( 0.0%) |   0 ( 0.0%)
``` 