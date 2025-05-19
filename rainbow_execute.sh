#!/bin/bash

# This file contains the code to execute the python function that produces the rainbow table method

if [ $# -ne 1 ]; then
  echo "Usage : $0 <hash_sha1>"
  exit 1
fi

HASH_TO_CRACK="$1"
MAX_RUNS=50

# Loop up to MAX_RUNS times
for ((i=1; i<=MAX_RUNS; i++)); do
  echo "Attempt $i of $MAX_RUNS"
  # Generate a new rainbow table
  python3 rainbow.py generate table.json
  # Try to crack the given hash using the generated table
  result=$(python3 rainbow.py crack $HASH_TO_CRACK table.json)

  # Display the result of the cracking attempt
  echo "$result"

  # If the result contains "Password found", stop the loop
  if echo "$result" | grep -q "Password found"; then
    echo "Password found on attempt number $i"
    break
  fi
done