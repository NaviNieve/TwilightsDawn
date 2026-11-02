class SaveChecksum:
    def __init__(self):
        self.s1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.s2 = "abcdefghijklmnopqrstuvwxyz"
        self.s3 = "0123456789"

    def get_char_score(self, char):
        if char in self.s1: return self.s1.index(char)
        if char in self.s2: return self.s2.index(char)
        if char in self.s3: return self.s3.index(char)
        return 0

    def calculate_salt(self, base_string):
        score_sum = 0
        for char in base_string:
            score_sum += self.get_char_score(char)
        return score_sum
