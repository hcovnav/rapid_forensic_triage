import struct
from . import read_csv_1

def method_get_f_value_data(cwd, f_value_data):
    # Assume 'f_value_data' is the 88-byte binary data from the 'F' value
    # 'L' specifies a 4-byte unsigned long integer

    # The RID is at offset 48 (0x30)
    rid = struct.unpack_from('<L', f_value_data, offset=48)[0]

    # The UAC flags are at offset 56 (0x38)
    uac_flag_sum_decimal = struct.unpack_from('<L', f_value_data, offset=56)[0]
    current_uac_flags_list = []
    full_uac_flags_list = read_csv_1.method_read_csv_to_dicts(cwd + "\\api_methods\\uac_flags.csv")
    for flag_info in full_uac_flags_list:
        if uac_flag_sum_decimal & int(flag_info['Decimal Value']) == int(flag_info['Decimal Value']):
            current_uac_flags_list.append(flag_info)
    response = {
        "rid": rid,
        "uac_flags_list": current_uac_flags_list,
        "uac_flag_sum_decimal": uac_flag_sum_decimal
    }
    return response
