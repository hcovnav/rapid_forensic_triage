from Registry import Registry

try:
    # Provide the path to your offline registry file
    registry_file = "C:\\non_os\\project\\7030\\py\\extracted_SAM" 
    
    with open(registry_file, "rb") as f:
        registry = Registry.Registry(f)

        # Get a specific key
        run_key = registry.open("SAM\\Domains\\Account\\Users\\Names")

        # List all values under the key
#       for value in run_key.values():
#           print(f"Name: {value.name()}, Value: {value.value()}")
        for value in run_key.subkeys():
            print(f"Name: {value.name()}")

except FileNotFoundError:
    print(f"Error: The file '{registry_file}' was not found.")
except Registry.RegistryParse.ParseException as e:
    print(f"Error parsing the registry file: {e}")