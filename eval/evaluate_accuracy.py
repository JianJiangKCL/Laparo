#!/usr/bin/env python3
import json
import re
import argparse
from pathlib import Path
from collections import Counter, defaultdict

def normalize_phase(phase_text):
    """
    Normalize the phase text by:
    1. Removing prefixes like "The phase is", "The current phase is", etc.
    2. Removing "The complete surgical action is:" prefix
    3. Removing multiple-choice option prefix (e.g., "A.", "F.")
    4. Converting to lowercase
    5. Removing whitespace
    """
    # Remove "The phase is" or "The current phase is" prefixes if present
    phase_text = re.sub(r"(?i)the\s+(current\s+)?phase\s+is\s*", "", phase_text)
    
    # Remove "The complete surgical action is:" prefix if present
    phase_text = re.sub(r"(?i)the\s+complete\s+surgical\s+action\s+is\s*:\s*", "", phase_text)
    
    # Remove multiple-choice option prefix (e.g., "A.", "F.") if present
    phase_text = re.sub(r"^[A-Z]\.\s*", "", phase_text)
    
    # Convert to lowercase and remove all whitespace
    return phase_text.lower().replace(" ", "")

def preprocess_label(label):
    """
    Preprocess a label to:
    1. Remove prefixes like "The phase is", "The current phase is", etc.
    2. Remove "The complete surgical action is:" prefix
    3. Remove multiple-choice option prefix (e.g., "A.", "F.")
    4. Trim whitespace
    """
    # Remove "The phase is" or "The current phase is" prefixes if present
    label = re.sub(r"(?i)the\s+(current\s+)?phase\s+is\s*", "", label)
    
    # Remove "The complete surgical action is:" prefix if present
    label = re.sub(r"(?i)the\s+complete\s+surgical\s+action\s+is\s*:\s*", "", label)
    
    # Remove multiple-choice option prefix if present
    label = re.sub(r"^[A-Z]\.\s*", "", label)
    
    return label.strip()

def extract_answer_from_cot(text):
    """
    Extract the answer from a chain-of-thought format response.
    The answer should be between <answer> and </answer> tags.
    """
    match = re.search(r'<answer>(.*?)</answer>', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text

def calculate_accuracy(jsonl_file, mode="normal"):
    """Calculate the accuracy from the JSONL file"""
    correct = 0
    total = 0
    predictions = []
    true_labels_counter = Counter()
    pred_labels_counter = Counter()
    norm_to_orig = {}
    original_items = []
    
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
                
            data = json.loads(line)
            
            # Support different JSON formats by checking multiple possible field names
            response = (
                data.get("response") or 
                data.get("prediction") or 
                data.get("predicted_phase") or
                data.get("output")
            )
            
            labels = (
                data.get("labels") or 
                data.get("label") or 
                data.get("ground_truth") or 
                data.get("true_phase") or
                data.get("target")
            )
            
            # Skip entries with missing response or labels
            if not response or not labels:
                continue
            
            # Handle cases where response/labels might be in a nested structure
            if isinstance(response, dict):
                response = response.get("text", "") or response.get("value", "")
            if isinstance(labels, dict):
                labels = labels.get("text", "") or labels.get("value", "")
            
            # Convert to string if necessary
            response = str(response).strip()
            labels = str(labels).strip()
            
            # Extract answer from CoT format if mode is "cot"
            if mode == "cot":
                response = extract_answer_from_cot(response)
                labels = extract_answer_from_cot(labels)
            
            # Store original item
            original_items.append(data)
            
            # Clean for human-readable display - ignore the MCQ letters
            clean_response = preprocess_label(response)
            clean_labels = preprocess_label(labels)
            
            # Store original MCQ format for incorrect prediction display
            original_response = response
            original_labels = labels
            
            # Normalize for comparison
            norm_response = normalize_phase(response)
            norm_labels = normalize_phase(labels)
            
            # Store mapping from normalized to original (without MCQ letters)
            norm_to_orig[norm_response] = clean_response
            norm_to_orig[norm_labels] = clean_labels
            
            # Track for statistics
            true_labels_counter[norm_labels] += 1
            pred_labels_counter[norm_response] += 1
            
            # Store prediction
            predictions.append({
                'true': norm_labels,
                'pred': norm_response,
                'true_display': clean_labels,
                'pred_display': clean_response,
                'original_response': original_response,  # Store original with MCQ format
                'original_labels': original_labels,      # Store original with MCQ format
                'correct': norm_response == norm_labels,
                'original_item': data  # Store original item
            })
            
            # Check if normalized strings match
            if norm_response == norm_labels:
                correct += 1
            
            total += 1
    
    # Build confusion matrix (using normalized labels)
    confusion = defaultdict(lambda: defaultdict(int))
    for pred in predictions:
        confusion[pred['true']][pred['pred']] += 1
    
    accuracy = correct / total if total > 0 else 0
    return accuracy, confusion, correct, total, true_labels_counter, pred_labels_counter, predictions, norm_to_orig

def get_max_class_name_length(classes, norm_to_orig):
    """Get the maximum length of class names for formatting"""
    max_length = 0
    for cls in classes:
        display_name = norm_to_orig.get(cls, cls)
        max_length = max(max_length, len(display_name))
    return max_length

def print_confusion_matrix(confusion, true_labels_counter, norm_to_orig):
    """Print a better formatted confusion matrix"""
    # Get all unique class labels
    all_classes = set()
    for true_label in confusion:
        all_classes.add(true_label)
        for pred_label in confusion[true_label]:
            all_classes.add(pred_label)
    
    all_classes = sorted(all_classes)
    
    # Get maximum class name length for better formatting
    max_class_length = get_max_class_name_length(all_classes, norm_to_orig) + 2  # Add padding
    max_class_length = min(max_class_length, 30)  # Cap at reasonable length
    
    # Print header
    print("\nConfusion Matrix:")
    header = f"{'True\\Pred':{max_class_length}}"
    for cls in all_classes:
        display_cls = norm_to_orig.get(cls, cls)
        header += f" | {display_cls[:12]:<12}"
    print(header)
    print("-" * len(header))
    
    # Print rows
    for true_label in sorted(confusion.keys(), key=lambda x: norm_to_orig.get(x, x)):
        display_true = norm_to_orig.get(true_label, true_label)
        row = f"{display_true:{max_class_length}}"
        for pred_label in all_classes:
            count = confusion[true_label][pred_label]
            # Calculate percentage of this class
            total_for_class = true_labels_counter[true_label]
            percentage = (count / total_for_class) * 100 if total_for_class > 0 else 0
            row += f" | {count:>3} ({percentage:>4.1f}%)"
        print(row)

def calculate_class_metrics(predictions):
    """Calculate per-class precision, recall, and F1 scores using normalized labels"""
    # Get unique normalized class labels
    class_labels = set()
    for p in predictions:
        class_labels.add(p['true'])
    
    metrics = {}
    for cls in class_labels:
        # For each class, count metrics using normalized labels
        tp = sum(1 for p in predictions if p['pred'] == cls and p['true'] == cls)
        fp = sum(1 for p in predictions if p['pred'] == cls and p['true'] != cls)
        fn = sum(1 for p in predictions if p['pred'] != cls and p['true'] == cls)
        
        # Calculate standard metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Calculate support
        support = sum(1 for p in predictions if p['true'] == cls)
        
        metrics[cls] = {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'support': support,
            'tp': tp,
            'fp': fp,
            'fn': fn
        }
    
    return metrics

def calculate_precision_recall_curve(predictions, class_label):
    """Calculate precision and recall values for a specific class"""
    tp = 0  # True positives
    fp = 0  # False positives
    fn = sum(1 for p in predictions if p['true'] == class_label)  # False negatives
    
    precisions = []
    recalls = []
    
    # For each prediction, calculate precision and recall
    for pred in predictions:
        if pred['pred'] == class_label:
            if pred['true'] == class_label:
                tp += 1
            else:
                fp += 1
            
            # Calculate current precision and recall
            current_precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            current_recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            
            precisions.append(current_precision)
            recalls.append(current_recall)
    
    # Add the final point (0,0) if not present
    if not precisions or precisions[-1] != 0:
        precisions.append(0)
        recalls.append(0)
    
    return precisions, recalls

def calculate_average_precision(precisions, recalls):
    """Calculate average precision using 11-point interpolation"""
    if not precisions or not recalls:
        return 0.0
    
    # 11-point interpolation
    recall_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    interpolated_precisions = []
    
    for r in recall_levels:
        # Find the maximum precision for recall >= r
        max_precision = 0.0
        for p, rec in zip(precisions, recalls):
            if rec >= r:
                max_precision = max(max_precision, p)
        interpolated_precisions.append(max_precision)
    
    return sum(interpolated_precisions) / len(recall_levels)

def calculate_map(predictions):
    """Calculate mean Average Precision for all classes"""
    # Get unique class labels
    class_labels = set(p['true'] for p in predictions)
    aps = []
    
    for cls in class_labels:
        precisions, recalls = calculate_precision_recall_curve(predictions, cls)
        ap = calculate_average_precision(precisions, recalls)
        aps.append(ap)
    
    return sum(aps) / len(aps) if aps else 0.0

def main():
    parser = argparse.ArgumentParser(description="Evaluate accuracy from a JSONL file")
    parser.add_argument("--input_file", help="Path to the JSONL file")
    parser.add_argument("--output", "-o", help="Path to save results in JSON format", default=None)
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed information including incorrect predictions")
    parser.add_argument("--debug", "-d", action="store_true", help="Show debug information")
    parser.add_argument("--output_failure", help="Path to save full details of incorrect predictions in JSONL format", default="fails.jsonl")
    parser.add_argument("--mode", choices=["normal", "cot"], default="normal", help="Evaluation mode: 'normal' for standard format, 'cot' for chain-of-thought format")
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if args.output:
        output_dir = Path(args.output).parent
        output_dir.mkdir(parents=True, exist_ok=True)
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File {args.input_file} does not exist")
        return
    
    accuracy, confusion, correct, total, true_labels_counter, pred_labels_counter, predictions, norm_to_orig = calculate_accuracy(args.input_file, mode=args.mode)
    
    # Calculate mAP
    map_score = calculate_map(predictions)
    
    print(f"\nOverall Accuracy: {accuracy:.4f} ({correct}/{total})")
    print(f"Mean Average Precision (mAP): {map_score:.4f}")
    
    # Debug print
    if args.debug:
        print("\nPredictions (Normalized):")
        for i, pred in enumerate(predictions, 1):
            print(f"{i}. True: '{pred['true']}' (Display: '{pred['true_display']}'), "
                  f"Pred: '{pred['pred']}' (Display: '{pred['pred_display']}'), "
                  f"Correct: {pred['correct']}")
        
        print("\nNormalized Mappings:")
        for norm, orig in norm_to_orig.items():
            print(f"Normalized: '{norm}' -> Original: '{orig}'")
        
        print("\nConfusion Matrix (Raw):")
        for true_label in confusion:
            for pred_label in confusion[true_label]:
                print(f"True: '{true_label}' (Display: '{norm_to_orig.get(true_label, true_label)}'), "
                      f"Pred: '{pred_label}' (Display: '{norm_to_orig.get(pred_label, pred_label)}'), "
                      f"Count: {confusion[true_label][pred_label]}")
    
    # Calculate and print class metrics
    class_metrics = calculate_class_metrics(predictions)
    
    # Get maximum class name length for better formatting
    sorted_classes = sorted(class_metrics.keys(), key=lambda x: norm_to_orig.get(x, x))
    max_class_length = get_max_class_name_length(sorted_classes, norm_to_orig)
    # Cap at reasonable length to prevent overly wide output
    max_class_length = min(max_class_length, 30)
    
    print("\nPer-Class Metrics:")
    metrics_header = f"{'Class':{max_class_length}} {'Precision':>10} {'Recall':>10} {'F1-Score':>10} {'Support':>10}"
    print(metrics_header)
    print("-" * len(metrics_header))
    
    # Calculate macro and weighted averages
    macro_precision = 0
    macro_recall = 0
    macro_f1 = 0
    weighted_precision = 0
    weighted_recall = 0
    weighted_f1 = 0
    total_support = 0
    
    # Sort by display name
    num_classes = len(sorted_classes)
    
    for cls in sorted_classes:
        metrics = class_metrics[cls]
        display_name = norm_to_orig.get(cls, cls)
        
        # Debug print
        if args.debug:
            print(f"\nClass: {display_name} (Normalized: {cls})")
            print(f"TP: {metrics['tp']}, FP: {metrics['fp']}, FN: {metrics['fn']}, Support: {metrics['support']}")
        
        print(f"{display_name:{max_class_length}} {metrics['precision']:>10.4f} {metrics['recall']:>10.4f} {metrics['f1']:>10.4f} {metrics['support']:>10}")
        
        support = metrics['support']
        total_support += support
        macro_precision += metrics['precision']
        macro_recall += metrics['recall']
        macro_f1 += metrics['f1']
        
        # For weighted average
        weighted_precision += metrics['precision'] * support
        weighted_recall += metrics['recall'] * support
        weighted_f1 += metrics['f1'] * support
    
    # Print macro and weighted averages
    if num_classes > 0:
        print("-" * len(metrics_header))
        print(f"{'Macro Average':{max_class_length}} {macro_precision/num_classes:>10.4f} {macro_recall/num_classes:>10.4f} {macro_f1/num_classes:>10.4f} {total:>10}")
        
        if total_support > 0:
            print(f"{'Weighted Average':{max_class_length}} {weighted_precision/total_support:>10.4f} {weighted_recall/total_support:>10.4f} {weighted_f1/total_support:>10.4f} {total:>10}")
    
    # Print detailed confusion matrix
    print_confusion_matrix(confusion, true_labels_counter, norm_to_orig)
    
    # Print incorrect predictions if verbose mode is enabled - show original MCQ format
    incorrect = [p for p in predictions if not p['correct']]
    if args.verbose and incorrect:
        print("\nIncorrect Predictions:")
        for i, pred in enumerate(incorrect, 1):
            print(f"{i}. True: '{pred['original_labels']}', Predicted: '{pred['original_response']}'")
    
    # Save results to JSON if output path is provided
    if args.output:
        # Convert to serializable format
        serializable_confusion = {k: dict(v) for k, v in confusion.items()}
        results = {
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'class_metrics': class_metrics,
            'confusion_matrix': serializable_confusion,
            'norm_to_orig': norm_to_orig
        }
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to {args.output}")
    
    # Save full details of incorrect predictions if output_failure path is provided
    if args.output_failure and incorrect:
        with open(args.output_failure, 'w', encoding='utf-8') as f:
            for pred in incorrect:
                # Write the original item to the file
                json.dump(pred['original_item'], f)
                f.write('\n')
        
        print(f"\nIncorrect predictions saved to {args.output_failure}")

if __name__ == "__main__":
    main() 