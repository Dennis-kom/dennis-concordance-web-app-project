linking_words = [
    "a", "an", "the",
    "and", "or", "but", "nor", "so", "yet", "for",
    "if", "then", "else", "because", "although", "though", "while", "whereas",
    "unless", "until", "when", "whenever", "before", "after", "since", "once", "that",
    "in", "on", "at", "to", "from", "with", "without", "by", "for", "of", "about",
    "between", "among", "under", "over", "above", "below", "through", "across",
    "into", "onto", "during", "against", "within", "beyond",
    "am", "is", "are", "was", "were", "be", "been", "being",
    "can", "could", "may", "might", "must", "shall", "should", "will", "would",
    "I", "you", "he", "she", "it", "we", "they",
    "me", "him", "her", "us", "them",
    "my", "your", "his", "her", "its", "our", "their",
    "this", "that", "these", "those",
    "some", "any", "no", "every", "each", "all", "both", "either", "neither",
    "many", "much", "few", "little", "several",
    "who", "whom", "whose", "which", "where", "when",
    "also", "too", "very", "just", "only", "even", "still", "already",
    "always", "never", "often", "sometimes",
    "therefore", "however", "moreover", "nevertheless", "otherwise",
    "instead", "meanwhile", "consequently", "additionally", "similarly",
    "not", "n't",
    "as", "than", "like",
    "up", "down", "out", "off"
]


class DataStack:
    stack = {}


class Stack:

    def __init__(self):
        self.stack = []

    def push_step(self,value):
        ...

    def push_flag(self):
        ...

    def push_value(self):
        ...

    def pop(self):
        ...

    def last_type(self):
        ...

