import struct
from . import read_csv_1
from datetime import datetime, timedelta

# This is the largest possible 64-bit integer, often used as a "never expires" placeholder.
NEVER_EXPIRES_SENTINEL = 0x7FFFFFFFFFFFFFFF

def convert_windows_time(win_time):
    """Converts a 64-bit Windows NT time value to a Python datetime object."""
    # Check for both 0 and the max value sentinel for "Never"
    if win_time == 0 or win_time == NEVER_EXPIRES_SENTINEL:
        return "Never"

    # Windows NT time is the number of 100-nanosecond intervals since Jan 1, 1601
    epoch = datetime(1601, 1, 1)
    # Convert to seconds and create a timedelta
    try:
        delta = timedelta(microseconds=win_time / 10)
        return str(epoch + delta)
    except OverflowError:
        # Failsafe for any other unexpectedly large timestamp
        return "Invalid (date out of range)"


def method_get_f_value_data(cwd, f_value_data):
    data_list = []
    data_address_list = read_csv_1.method_read_csv_to_dicts(cwd + "\\api_methods\\f_value_offsets.csv")

    for data_address in data_address_list:
        f_info = {}
        f_info['field'] = data_address['Field Name']
        data_offset = int(data_address['Offset (Decimal)'])
        data_type = data_address['Data Type']
        size_bytes = int(data_address['Size (Bytes)'])

        value = None

        # Use the 'Data Type' from the CSV to decide how to unpack the data
        if data_type == 'Windows NT Time':
            # Timestamps are 8-byte unsigned long longs
            raw_val = struct.unpack_from('<Q', f_value_data, offset=data_offset)[0]
            value = convert_windows_time(raw_val)

        elif 'Integer' in data_type: # Catches 'Integer', 'Unsigned Integer', and 'Unsigned Integer (Bitmask)'
            # Handle different integer sizes
            if size_bytes == 4:
                # 4-byte unsigned integer (for RID, Flags)
                value = struct.unpack_from('<L', f_value_data, offset=data_offset)[0]
            elif size_bytes == 2:
                # 2-byte integer (for Revision, Counts)
                value = struct.unpack_from('<H', f_value_data, offset=data_offset)[0]

        # If the type is unknown, just show the raw bytes
        if value is None:
            raw_data = f_value_data[data_offset : data_offset + size_bytes]
            value = str(raw_data)

        f_info['value'] = value
        data_list.append(f_info)

    return data_list
