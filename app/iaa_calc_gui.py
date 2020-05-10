from scraper.ufsc_scraper import UfscScraper
from student.student import Student
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
Window.clearcolor = (0.85, 0.85, 0.9, 0.8)
Window.size = (800, 460)
Window.minimum_width, Window.minimum_height = (700, 400)


class PageManager(ScreenManager):
    pass


class LoginPage(Screen):
    pass


class GraduatedPage(Screen):
    pass


class InvalidUserPage(Screen):
    pass


class HomePage(Screen):
    def create_x_text_inputs(self, placeholders):
        gap = -0.07
        for i, placeholder in enumerate(placeholders):
            text_input = TextInput(font_size=30-(len(placeholders)-5)*3.1,
                                   size_hint=(0.6, 0.35/len(placeholders)),
                                   background_normal='atlas://data/images/defaulttheme/textinput_active',
                                   border=(4, 4, 4, 4),
                                   multiline=False,
                                   pos_hint={'x': 0.2, 'top': 0.7+gap},
                                   cursor_color=(44 / 255, 44 / 255, 44 / 255, 0.8),
                                   hint_text=placeholder,
                                   write_tab=False
                                   )
            self.add_widget(text_input)
            self.ids['text_input_'+str(i)] = text_input
            gap -= 0.35/len(placeholders)


class IndexesErrorPage(Screen):
    pass


class NewIndexesPage(Screen):
    pass


kv = Builder.load_file("app/iaa_calc_gui.kv")


class IaaCalculator(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__scraper = UfscScraper()
        self.__student = Student()
        self.__login_page = kv.get_screen('login')
        self.__home_page = kv.get_screen('home')
        self.__new_indexes_page = kv.get_screen('new_indexes')
        self.__indexes_error_page = kv.get_screen('indexes_error')
        Window.bind(on_key_down=self._on_keyboard_down)

    def build(self):
        self.title = 'IAA Calculator'
        return kv

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 40 and kv.current == 'login':  # 40 - Enter key pressed
            self.get_login_values()
            self.update_home_page()
        elif keycode == 40 and kv.current == 'home':  # 40 - Enter key pressed
            self.update_new_indexes()
            self.clean_text_inputs()

    def get_login_values(self):
        user = self.__login_page.ids.login.text
        password = self.__login_page.ids.password.text
        self.__student.user_browser = self.__scraper.login(user, password)

        self.__login_page.ids.login.text = str()
        self.__login_page.ids.password.text = str()

    def validate_student_data(self):
        try:
            student_data = self.__scraper.get_student_data(self.__student.user_browser)
            self.__student.name = student_data['name']
            self.__student.grades = student_data['grades']
            self.__student.indexes = student_data['indexes']

            self.__student.current_classes = self.__scraper.get_current_classes(self.__student.user_browser)
            return True
        except ValueError:
            kv.current = "invalid_user"
            kv.transition.direction = "up"
        except SystemExit:
            kv.current = "graduated"
            kv.transition.direction = "down"

    def update_home_page(self):
        if self.validate_student_data():
            current_classes_names = [current_class[0] for current_class in self.__student.current_classes]

            self.__home_page.ids.name.text = self.__student.name
            self.__home_page.ids.iaa.text = 'IAA: ' + str(self.__student.indexes[0])
            self.__home_page.ids.ia.text = 'IA: ' + str(self.__student.indexes[1])
            self.__home_page.ids.iap.text = 'IAP: ' + str(self.__student.indexes[2])
            self.__home_page.create_x_text_inputs(current_classes_names)

            kv.current = "home"
            kv.transition.direction = "left"

    def update_new_indexes(self):
        try:
            possible_grades = [self.__home_page.ids['text_input_{}'.format(i)].text
                               for i in range(len(self.__student.current_classes))]
            new_indexes = self.__scraper.new_indexes(self.__student.grades,
                                                     [current_class[1] for
                                                      current_class in
                                                      self.__student.current_classes],
                                                     possible_grades)

            self.__new_indexes_page.ids.iaa.text = 'IAA: ' + str(new_indexes[0])
            self.__new_indexes_page.ids.ia.text = 'IA: ' + str(new_indexes[1])
            self.__new_indexes_page.ids.iap.text = 'IAP: ' + str(new_indexes[2])

            kv.current = "new_indexes"
            kv.transition.direction = "left"

        except ValueError:
            kv.current = "indexes_error"
            kv.transition.direction = "up"

    def clean_text_inputs(self):
        for i in range(len(self.__student.current_classes)):
            self.__home_page.ids['text_input_{}'.format(i)].text = ''


if __name__ == "__main__":
    IaaCalculator().run()
