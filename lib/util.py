decimal_degree = {
    'K': 3,
    'M': 6,
    'G': 9,
    'T': 12,
    'P': 15,
    'E': 18,
    'Z': 21,
    'Y': 24,
}


def text_to_num(text):
    if len(text) == 0 or text == " ":
        return 0
    elif text[-1] == "B":
        return int(text[:-1])
    elif text[-1] in decimal_degree:
        num, magnitude = text[:-1], text[-1]
        return float(num) * 10 ** decimal_degree[magnitude]
    elif text[-1] == "%":
        return float(text[:-1])
    else:
        if text[0].isalpha() and text[-1].isalpha():
            return None
        if "." in text:
            return float(text)
        else:
            return int(text)
