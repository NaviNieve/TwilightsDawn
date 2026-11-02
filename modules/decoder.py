class SaveDecoder:
    def __init__(self):
        self.charset = "LKJHGFDSAPOIUYTREWQMNBVCXZasdfghjklzxcvbnmqwertyuiop9876543210&^%$#@!"
        self.charset_len = len(self.charset)

    def decode_to_array(self, save_code):
        """Reverses Base-68 and Base-11 algorithms to extract raw integers."""
        clean_code = save_code.replace("-", "").strip()
        
        base_10_value = 0
        for char in clean_code:
            if char not in self.charset:
                raise ValueError(f"Character '{char}' not found in verification dictionary matrix.")
            base_10_value = base_10_value * self.charset_len + self.charset.index(char)

        digits = []
        temp_val = base_10_value
        while temp_val > 0:
            remainder = temp_val % 11
            if remainder == 10:
                digits.append("-")
            else:
                digits.append(str(remainder))
            temp_val //= 11
            
        unmasked_string = "".join(reversed(digits))
        
        elements = unmasked_string.split("-")
        if not elements or elements[-1] == "":
            elements.pop()
            
        raw_stats = [int(x) for x in elements[:-1] if x != ""]
        return raw_stats
