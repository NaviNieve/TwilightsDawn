from .checksum import SaveChecksum

class SaveEngine:
    def __init__(self):
        self.charset = "LKJHGFDSAPOIUYTREWQMNBVCXZasdfghjklzxcvbnmqwertyuiop9876543210&^%$#@!"
        self.charset_len = len(self.charset)
        self.checksum = SaveChecksum()

    def generate_save_string(self, raw_stats, player_name):
        raw_dash_string = "-".join(str(val) for val in raw_stats) + "-"
        player_salt = self.checksum.calculate_salt(raw_dash_string + player_name)
        final_numeric_sequence = f"{raw_dash_string}{player_salt}"

        base_10_value = 0
        multiplier = 1
        for char in reversed(final_numeric_sequence):
            val_score = 10 if char == '-' else int(char)
            base_10_value += val_score * multiplier
            multiplier *= 11

        encoded_chars = []
        temp_val = base_10_value
        while temp_val > 0:
            remainder = temp_val % self.charset_len
            encoded_chars.append(self.charset[remainder])
            temp_val //= self.charset_len
            
        raw_code = "".join(reversed(encoded_chars))
        return "-".join(raw_code[i:i+4] for i in range(0, len(raw_code), 4))
