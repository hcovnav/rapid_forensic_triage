import struct
from . import read_csv_1

def method_get_v_value_data(cwd, v_value_data):


    data_location_list = []
    full_data_location_list_from_csv = read_csv_1.method_read_csv_to_dicts(cwd + "\\api_methods\\v_value_header_offsets.csv")
    for data_location_from_csv in full_data_location_list_from_csv:
        v_info = {}
        h_offset = data_location_from_csv['Header Offset'].replace("0x","")
        v_info['address_address'] = int(h_offset, 16)
        v_info['field'] = data_location_from_csv['Data Field']
        v_info['length_address'] = v_info['address_address'] + 4
        v_info['actual_address'] = struct.unpack_from('<L', v_value_data, offset=v_info['address_address'])[0]
        v_info['actual_length'] = struct.unpack_from("<L", v_value_data, offset=v_info['length_address'])[0]
        length_val = "<" + str(v_info['actual_length']) + "s"
        offset_val = v_info['actual_address'] + 204
        raw_data = struct.unpack_from(length_val, v_value_data, offset=offset_val)[0]
        v_info['actual_data'] = raw_data.decode('utf-16-le')

        data_location_list.append(v_info)
    return data_location_list
