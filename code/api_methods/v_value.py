import struct
from . import read_csv_1
from datetime import datetime, timedelta

def convert_windows_time(win_time):
    """Converts a 64-bit Windows NT time value to a Python datetime object."""
    if win_time == 0:
        return "Never"
    # Windows NT time is the number of 100-nanosecond intervals since Jan 1, 1601
    epoch = datetime(1601, 1, 1)
    # Convert to seconds and create a timedelta
    delta = timedelta(microseconds=win_time / 10)
    return epoch + delta

def method_get_v_value_data(cwd, v_value_data):
    data_location_list = []
    full_data_location_list_from_csv = read_csv_1.method_read_csv_to_dicts(cwd + "\\api_methods\\v_value_header_offsets.csv")

    for data_location_from_csv in full_data_location_list_from_csv:
        v_info = {}
        h_offset_str = data_location_from_csv['Header Offset'].replace("0x","")
        v_info['address_address'] = int(h_offset_str, 16)
        v_info['field'] = data_location_from_csv['Data Field']

        # Check if the current field is a timestamp
        if "Timestamp" in v_info['field'] or "Password Last Set" in v_info['field'] or "Account Expiration" in v_info['field']:
            # Timestamps are 8-byte values stored directly at the header offset
            # We read them as a 64-bit unsigned long long ('<Q')
            raw_timestamp = struct.unpack_from('<Q', v_value_data, offset=v_info['address_address'])[0]
            v_info['actual_data'] = str(convert_windows_time(raw_timestamp))
            v_info['actual_address'] = "N/A (Direct Value)"
            v_info['actual_length'] = 8 # Timestamps are 8 bytes
            v_info['length_address'] = "N/A (Direct Value)"

        else:
            # This is the original logic for strings, which is correct
            v_info['length_address'] = v_info['address_address'] + 4
            v_info['actual_address'] = struct.unpack_from('<L', v_value_data, offset=v_info['address_address'])[0]
            v_info['actual_length'] = struct.unpack_from("<L", v_value_data, offset=v_info['length_address'])[0]

            if v_info['actual_length'] > 0:
                # The data area starts at a fixed offset of 204
                data_area_start_offset = 204
                final_data_offset = data_area_start_offset + v_info['actual_address']

                length_val = "<" + str(v_info['actual_length']) + "s"
                raw_data = struct.unpack_from(length_val, v_value_data, offset=final_data_offset)[0]
                v_info['actual_data'] = raw_data.decode('utf-16-le', errors='ignore')
            else:
                v_info['actual_data'] = ""

        data_location_list.append(v_info)
    return data_location_list
