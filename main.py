import json
import random
import pygame
from statistics import mean

pygame.font.init()
FPS = 60


# Класс кнопки
class Button(pygame.Rect):
    def __init__(self, x, y, w, h, script):
        super().__init__(x, y, w, h)
        self.script = script

    # Функция нажатия
    def trigger(self):
        self.script()


# Основной класс
class App:
    def __init__(self):
        # Окно
        self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption('Тренировщик ударений')
        ico = pygame.image.load('icon.png')
        pygame.display.set_icon(ico)
        self.wn_w, self.wn_h = self.window.get_size()
        # Загрузка слов
        with open('words.json', 'r') as save_file:
            self.word_list, self.word_weights = map(list, zip(*json.load(save_file)))
            print(f'Загружено {len(self.word_list)} слов')
        self.current_word = random.choices(self.word_list, weights=self.word_weights)[0]
        self.prev_word = self.current_word
        self.vowels = ['у', 'е', 'ы', 'ё', 'а', 'о', 'э', 'я', 'и', 'ю']  # Список гласных
        self.is_textfield_active = False  # Вводится ли слово
        self.new_word = ''  # Строка нового вводимого слова
        self.result_text = ''  # Строка итога
        # Шрифты
        self.big_font = pygame.font.SysFont('Courier', 125)
        self.standard_font = pygame.font.SysFont('Times New Roman', 45)
        self.text = self.standard_font.render(self.new_word, False, (0, 0, 0))
        self.font_color = [240, 240, 240]
        # Кнопки
        self.buttons = []
        even_weights_button = Button(self.wn_w - 50, self.wn_h-50, 50, 50, self.even_weights)
        add_new_word_button = Button(0, self.wn_h - 50, 50, 50, self.add_new_button_f)
        delete_button = Button(self.wn_w / 2 - 25, self.wn_h / 2 + 75, 50, 50, self.delete_word_f)
        self.buttons.append(add_new_word_button)
        self.buttons.append(delete_button)
        self.buttons.append(even_weights_button)
        self.temp_buttons = []
        self.working = True
        self.clock = pygame.time.Clock()

    # Фунция кнопки добавления слов
    def add_new_button_f(self):
        self.is_textfield_active = True

    # Функция кнопки удаления слов
    def delete_word_f(self):
        print(f'Слово {self.current_word} было удалено')
        idx = self.word_list.index(self.current_word)
        self.word_list.pop(idx)
        self.word_weights.pop(idx)
        self.save_words()
        self.current_word = random.choices(self.word_list, weights=self.word_weights)[0]

    # Неправильный ответ
    def wrong_one(self):
        index = self.word_list.index(self.current_word)
        self.word_weights[index] *= 25
        self.save_words()
        prev_word = self.current_word
        self.current_word = random.choices(self.word_list, weights=self.word_weights)[0]
        self.result_text = ('Неверно!' + prev_word)
        self.font_color = [240, 0, 0]
        print('Неверно!')

    # Правильный ответ
    def right_one(self):
        index = self.word_list.index(self.current_word)
        self.word_weights[index] *= 0.75
        self.save_words()
        prev_word = self.current_word
        self.current_word = random.choices(self.word_list, weights=self.word_weights)[0]
        self.result_text = ('Верно! ' + prev_word)
        self.font_color = [240, 240, 240]
        print('Верно!')

    # Отрисовка слова
    def word_draw(self, word, x_center=None, y_center=None, is_interactive=True, font=None, symbol_size=70):
        if x_center is None:
            x_center = self.wn_w / 2
        if y_center is None:
            y_center = self.wn_h / 2 - 100
        if font is None:
            font = self.big_font
        left_most = x_center - symbol_size * (len(word) / 2)
        index = 0
        if is_interactive:
            txt = word.lower()
        else:
            txt = word
        for letter in txt:
            current_letter_text = font.render(letter, True, (0, 0, 0))
            self.window.blit(current_letter_text, (index * symbol_size + left_most, y_center))
            if is_interactive:
                if letter in self.vowels:
                    if word[index].islower():
                        self.temp_buttons.append(
                            Button(index * symbol_size + left_most, self.wn_h / 2 - 56, symbol_size + 5, symbol_size,
                                   self.wrong_one))
                    else:
                        self.temp_buttons.append(
                            Button(index * symbol_size + left_most, self.wn_h / 2 - 56, symbol_size + 5, symbol_size,
                                   self.right_one))
            index += 1

    # Проверка нажатых кнопок
    def button_check(self, pos):
        for btn in self.buttons:
            if btn.collidepoint(pos):
                btn.trigger()
        for btn in self.temp_buttons:
            if btn.collidepoint(pos):
                btn.trigger()

    # Функция, равняющая веса
    def even_weights(self):
        self.word_weights = [100] * len(self.word_weights)
        self.save_words()
        print('Веса уравняны')

    # Функция сохранения слов
    def save_words(self):
        with open('words.json', 'w') as save_file:
            json.dump(list(map(list, zip(self.word_list, self.word_weights))), save_file)

    # Функция, добавляющая слова в список
    def add_word(self, word):
        capital_vowels = 0
        if word not in self.word_list:
            for letter in word:
                if letter.isupper():
                    if letter.lower() in self.vowels:
                        capital_vowels += 1
                    else:
                        print(f'В слове {word} не должно быть заглавных согласных')
            if capital_vowels == 1:
                self.word_list.append(word)
                self.word_weights.append(mean(self.word_weights))
                self.save_words()
                print(f'добавлено слово {word}')
            else:
                print(f'В слове {word} быть лишь одна заглавная гласная')
        else:
            print(f'Слово {word} уже присутствует в списке')

    # Управление
    def controls(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Выход путем нажатия крестика
                self.working = False
            if event.type == pygame.MOUSEBUTTONDOWN:  # Обработка клика в окне
                self.button_check(pygame.mouse.get_pos())
            if event.type == pygame.KEYDOWN:  # Обработка событий клавиатуры
                if event.key == pygame.K_ESCAPE:  # Выход путем нажатия escape
                    self.working = False
                if self.is_textfield_active:  # Редактор текста
                    if event.key == pygame.K_RETURN:  # Подтверждение нового слова
                        for word in self.new_word.split(' '):
                            self.add_word(word)
                        self.new_word = ''
                        self.is_textfield_active = False
                    elif event.key == pygame.K_BACKSPACE:  # Стереть букву
                        self.new_word = self.new_word[:-1]
                    else:
                        self.new_word += event.unicode  # Добавить букву
                else:
                    pass

    # Рендер
    def draw(self):
        # Заливка фона и его возвращуние к белому цвету
        self.window.fill(self.font_color)
        self.font_color = [min(channel_color + 4, 240) for channel_color in self.font_color]
        for button in self.buttons:
            pygame.draw.rect(self.window, (253, 106, 2), button)
        for button in self.temp_buttons:
            pygame.draw.rect(self.window, (253, 106, 2), button)
        text = self.standard_font.render(self.new_word, True, (0, 0, 0))
        self.window.blit(text, (50, self.wn_h - 50))
        self.temp_buttons = []  # Кнопки на гласных
        self.word_draw(self.current_word)
        self.word_draw(self.result_text, self.wn_w / 2, self.wn_h / 2 + 20, False, self.standard_font, 27)
        pygame.display.flip()

    # Основной цикл
    def run(self):
        self.draw()
        self.controls()
        self.clock.tick(FPS)


def main():
    app = App()
    while app.working:
        app.run()


if __name__ == '__main__':
    main()
