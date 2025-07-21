import csv


def method_read_csv_to_dicts(filepath):
    try:
        with open(filepath, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            list_of_dicts = list(csv_reader)
            return list_of_dicts
    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []





