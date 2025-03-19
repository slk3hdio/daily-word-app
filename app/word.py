
class Word:
    def __init__(self, word_id, word, pronunciation_uk, pronunciation_us):
        self.id = word_id
        self.word = word
        self.pronunciation_uk = pronunciation_uk
        self.pronunciation_us = pronunciation_us
        self.meanings = []

    def add_meaning(self, part_of_speech, definition):
        self.meanings.append((part_of_speech, definition))

    def get_dictation(self):
        s = f'[英]/{self.pronunciation_us}/ [美]/{self.pronunciation_uk}/ '
        for meaning in self.meanings:
            s += f'<{meaning[0]}>.{meaning[1]}; '
        return s

    def __str__(self):
        s = f'{self.word} [英]/{self.pronunciation_us}/ [美]/{self.pronunciation_uk}/ '
        for meaning in self.meanings:
            s += f'<{meaning[0]}>.{meaning[1]}; '
        return s

    # def __eq__(self, other):
    #     return self.word == other