from scraper.ufsc_scraper import UfscScraper
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
Window.clearcolor = (0.85, 0.85, 0.9, 0.8)
Window.size = (700, 400)
Window.minimum_width, Window.minimum_height = (700, 400)
Window.maximum_width, Window.maximum_height = (1000, 700)


class LoginPage(Screen):
    pass


class NewIndexesPage(Screen):
    pass


class IndexesErrorPage(Screen):
    pass


class InvalidUserPage(Screen):
    pass


class HomePage(Screen):
    def __init__(self, **kwargs):
        super(HomePage, self).__init__(**kwargs)

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


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("app/iaa_calc_gui.kv")


class IaaCalculator(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__scraper = UfscScraper()
        self.__login_page = kv.get_screen('login')
        self.__home_page = kv.get_screen('home')
        self.__new_indexes_page = kv.get_screen('new_indexes')
        self.__indexes_error_page = kv.get_screen('indexes_error')
        self.__user = str()
        self.__password = str()
        self.__user_browser = None
        self.__student_name = str()
        self.__student_grades = list()
        self.__student_indexes = list()
        self.__student_current_classes = list()

    def build(self):
        self.title = 'IAA Calculator'
        return kv

    def get_login_values(self):
        self.__user = self.__login_page.ids.login.text
        self.__password = self.__login_page.ids.password.text
        print("Name:", self.__user,
              "\nPassword:", self.__password)
        self.__user_browser = self.__scraper.login(self.__user, self.__password)

        self.__login_page.ids.login.text = str()
        self.__login_page.ids.password.text = str()

    def validate_student_data(self):
        try:
            student_data = self.__scraper.get_student_data(self.__user_browser)
            self.__student_name = student_data['name']
            self.__student_grades = student_data['grades']
            self.__student_indexes = student_data['indexes']

            self.__student_current_classes = self.__scraper.get_current_classes(self.__user_browser)
            return True
        except ValueError:
            kv.current = "invalid_user"
            kv.transition.direction = "up"
        except SystemExit:
            print('Usuário já formado')

    def update_home_page(self):
        if self.validate_student_data():
            current_classes_names = [current_class[0] for current_class in self.__student_current_classes]

            self.__home_page.ids.name.text = self.__student_name
            self.__home_page.ids.iaa.text = 'IAA: ' + str(self.__student_indexes[0])
            self.__home_page.ids.ia.text = 'IA: ' + str(self.__student_indexes[1])
            self.__home_page.ids.iap.text = 'IAP: ' + str(self.__student_indexes[2])
            self.__home_page.create_x_text_inputs(current_classes_names)

            kv.current = "home"
            kv.transition.direction = "left"

    def update_new_indexes(self):
        try:
            possible_grades = [self.__home_page.ids['text_input_{}'.format(i)].text
                               for i in range(len(self.__student_current_classes))]
            new_indexes = self.__scraper.new_indexes(self.__student_grades,
                                                     [current_class[1] for current_class in self.__student_current_classes],
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
        for i in range(len(self.__student_current_classes)):
            self.__home_page.ids['text_input_{}'.format(i)].text = ''


if __name__ == "__main__":
    IaaCalculator().run()
