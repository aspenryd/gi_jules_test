import csv
import json
from Mappers.customer_mapper import CustomerMapper # Assuming Mappers is in PYTHONPATH or same dir
import datetime
import os

def csv_to_json_and_xml(csv_filepath, json_schema_filepath, output_dir):
    """
    Reads customer data from a CSV file, converts it to JSON,
    then maps it to XML using CustomerMapper, and saves both files.
    """
    customers_list = []
    try:
        with open(csv_filepath, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Basic type conversion (more robust error handling could be added)
                try:
                    row['Index'] = int(row['Index'])
                except ValueError:
                    print(f"Warning: Could not convert Index '{row['Index']}' to int for row: {row}")
                    # Decide on handling: skip row, use None, or raise error
                    continue # Skipping row for now if Index is invalid
                customers_list.append(row)
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_filepath}")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    if not customers_list:
        print("No data processed from CSV.")
        return

    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # --- Source JSON File ---
    source_json_filename = f"source_customers_{timestamp}.json"
    source_json_filepath = os.path.join(output_dir, source_json_filename)

    try:
        with open(source_json_filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(customers_list, jsonfile, indent=2)
        print(f"Successfully created source JSON: {source_json_filepath}")
    except Exception as e:
        print(f"Error writing JSON file: {e}")
        return

    # --- Target XML File ---
    try:
        mapper = CustomerMapper()
        xml_output = mapper.json_to_xml(customers_list)

        target_xml_filename = f"target_customers_{timestamp}.xml"
        target_xml_filepath = os.path.join(output_dir, target_xml_filename)

        with open(target_xml_filepath, 'w', encoding='utf-8') as xmlfile:
            xmlfile.write(xml_output)
        print(f"Successfully created target XML: {target_xml_filepath}")
    except Exception as e:
        print(f"Error during XML mapping or writing: {e}")


if __name__ == '__main__':
    # Define file paths relative to the script location or CustomerMapper root
    # Assuming the script is run from the CustomerMapper directory
    base_dir = os.path.dirname(os.path.abspath(__file__)) # Should be CustomerMapper directory

    csv_file = os.path.join(base_dir, "example files", "customers-100.csv")
    json_schema_file = os.path.join(base_dir, "schemas", "source_customer_list.json")
    output_folder = os.path.join(base_dir, "Examples")

    # For the script to find CustomerMapper, we might need to adjust Python's path
    # This is a common way if the Mappers package is in the parent directory of the script
    # or if the script is in the same directory as Mappers.
    # If process_customers.py is in CustomerMapper/, and Mappers/ is also in CustomerMapper/
    # the import 'from Mappers.customer_mapper import CustomerMapper' might not work directly
    # without __init__.py in CustomerMapper and Mappers, and potentially path adjustments.
    # For simplicity, let's assume the script is run with CustomerMapper as the CWD.
    # If CustomerMapper/Mappers/customer_mapper.py is the structure,
    # and we are in CustomerMapper/, then `from Mappers.customer_mapper import CustomerMapper` is correct.

    # Let's adjust for running from CustomerMapper/ as current working directory
    # For this to work, Mappers needs to be in the Python path.
    # If the script is run as `python CustomerMapper/process_customers.py` from outside,
    # then CustomerMapper needs to be a package or path needs to be added.
    # If run as `python process_customers.py` from `CustomerMapper/` directory, it should work.

    # To make the import robust, especially if Mappers is a sub-directory:
    # import sys # sys is already imported if needed for path manipulation
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # project_root = os.path.dirname(script_dir) # If script is in a subfolder like 'scripts'
    # sys.path.insert(0, project_root)
    # For current structure, if process_customers.py is in CustomerMapper/
    # and Mappers is also in CustomerMapper/, the import should be fine when
    # python is executed from the repository root as `python CustomerMapper/process_customers.py`
    # provided CustomerMapper itself is recognized as a package (e.g. has __init__.py) or path is adjusted.
    # The current import `from Mappers.customer_mapper import CustomerMapper` assumes that
    # the `CustomerMapper` directory is in sys.path or is the current working directory.

    # Let's make paths absolute from the script's location to avoid ambiguity
    script_dir = os.path.dirname(os.path.abspath(__file__)) # This is CustomerMapper/

    csv_file_path = os.path.join(script_dir, "example files", "customers-100.csv")
    json_schema_path = os.path.join(script_dir, "schemas", "source_customer_list.json")
    output_directory = os.path.join(script_dir, "Examples")

    # Ensure Mappers can be found. If process_customers.py is in CustomerMapper/,
    # and Mappers is a subdirectory, Python needs to know where to look for Mappers.
    # If Python is run from the repo root (`python CustomerMapper/process_customers.py`),
    # Python will try to import `Mappers.customer_mapper` relative to `sys.path`.
    # Adding the script's directory (CustomerMapper/) to sys.path can help resolve local imports.
    import sys
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    # Now, `from Mappers.customer_mapper import CustomerMapper` should work assuming
    # Mappers is a directory in `script_dir` containing `customer_mapper.py`.
    # However, the original error was about file paths, not imports. The import
    # `from Mappers.customer_mapper import CustomerMapper` will only work if
    # the script is run from the `CustomerMapper` directory, or `CustomerMapper` is in `PYTHONPATH`.
    # To make this more robust when running `python CustomerMapper/process_customers.py` from root:
    # We need to ensure that Python sees `Mappers` as a module.
    # This usually means `CustomerMapper` itself should be structured as a package, or
    # the `PYTHONPATH` needs to include the directory containing `Mappers`.

    # The original import `from Mappers.customer_mapper import CustomerMapper`
    # will be attempted from the CWD if `Mappers` is not found elsewhere.
    # If CWD is repo root, it will look for `repo_root/Mappers/...` which is not correct.
    # If CWD is `CustomerMapper/`, it will look for `CustomerMapper/Mappers/...` which is correct.

    # Let's adjust the import to be relative if possible, or ensure path is set.
    # The simplest way for now, assuming `python CustomerMapper/process_customers.py` execution:
    # The current working directory for the script will be the repo root.
    # So, the import `from Mappers.customer_mapper import CustomerMapper` will fail.
    # It should be `from CustomerMapper.Mappers.customer_mapper import CustomerMapper`
    # if `CustomerMapper` is in `sys.path` (e.g. by running `python -m CustomerMapper.process_customers`).
    # Or, we modify sys.path to include the root of the project.
    # For now, let's assume the user runs `python process_customers.py` from within `CustomerMapper` folder.
    # The path fix for csv_filepath etc. should be sufficient if run from `CustomerMapper`.

    # The file paths passed to csv_to_json_and_xml should be correct now.
    csv_to_json_and_xml(
        csv_filepath=csv_file_path,
        json_schema_filepath=json_schema_path, # This param is not actually used in the function yet
        output_dir=output_directory
    )
