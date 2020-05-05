class ViewStudent:
    def __init__(self):
        pass

    @staticmethod
    def print_indexes(indexes):
        """Pretty-prints the three indices parsed from the student's page."""
        model = "\nIAA: \033[1m{}\033[0m \t IA: {} \t IAP: {}"
        return model.format(*list(map(lambda x: str(x)[:4], indexes)))
