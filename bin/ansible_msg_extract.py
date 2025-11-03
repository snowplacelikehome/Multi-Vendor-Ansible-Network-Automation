#!/usr/bin/python3
import re
import sys

def get_matches_from_log(log_file_path, regex1, regex2):
    """
    Reads a log file, finds lines matching regex1, and for each match, 
    finds the next line matching regex2.

    Args:
        log_file_path (str): Path to the log file.
        regex1 (str): First regular expression.
        regex2 (str): Second regular expression.
    """

    try:
        with open(log_file_path, 'r') as log_file:
            for line in log_file:
                #matches = re.findall(regex1, line)
                #if matches:
                #    for match in matches:
                #        print(match)
                matches = re.search(regex1, line)
                if matches:
                    for match in matches:
                        print(match)
    except FileNotFoundError:
        print(f"Error: Log file not found at '{log_file_path}'", file=sys.stderr)
    except re.error as e:
         print(f"Error: Invalid regex pattern: {e}", file = sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

        #if re.search(regex1, line):
        #    for j in range(i + 1, len(lines)):
        #        if re.search(regex2, lines[j]):
        #            print(lines[j].strip())


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <log_file_path> <regex_pattern1> <regex_pattern2", file=sys.stderr)
        sys.exit(1)

    log_file_path = sys.argv[1]
    regex_pattern1 = sys.argv[2]
    regex_pattern2 = sys.argv[3]

    get_matches_from_log(log_file_path, regex_pattern1, regex_pattern2)