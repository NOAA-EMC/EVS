#!/usr/bin/env python3

import csv
import sys

def check_csv(filepath):
        try:
            with open(filepath, 'r', newline='') as f:
              reader = csv.reader(f)
              header = next(reader)
              num_cols = len(header)

              for i, row in enumerate(reader):
               if len(row) != num_cols:
                  print(f"Warning: Inconsistent column count on line {i+2}. Expected {num_cols}, got {len(row)}.", file=sys.stderr)
                  return 1 # Corrupt
            return 0 # Good
        except FileNotFoundError:
              print(f"Warning: File not found at {filepath}", file=sys.stderr)
              return 1
        except Exception as e:
              print(f"An error occurred: {e}", file=sys.stderr)
              return 1

if __name__ == "__main__":
     if len(sys.argv) < 2:
        print("Usage: python check_csv.py <filepath>", file=sys.stderr)
        sys.exit(1)
                                                                                                                                                                                                     
     result = check_csv(sys.argv[1])
     sys.exit(result) # Exit code 0 for good, 1 for corrupt
