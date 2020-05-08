from controller.controller_student import ControllerStudent
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
Window.clearcolor = (0.85, 0.85, 0.9, 0.8)
Window.size = (700, 400)
Window.minimum_width, Window.minimum_height = (700, 400)
Window.maximum_width, Window.maximum_height = (1000, 700)


class NewIndexesPage(Screen):
    def __init__(self, **kwargs):
        super(NewIndexesPage, self).__init__(**kwargs)
        self.display_indexes([8.51, 9, 8.51])

    def display_indexes(self, indexes):
        iaa = Label(text='IAA: ' + str(indexes[0]),
                    font_size=50,
                    color=(54 / 255, 54 / 255, 54 / 255, 0.8),
                    pos_hint={'x': -0.2, 'top': 1})
        ia = Label(text='IA: ' + str(indexes[1]),
                   font_size=50,
                   color=(54 / 255, 54 / 255, 54 / 255, 0.8),
                   pos_hint={'x': 0, 'top': 1})
        iap = Label(text='IAP: ' + str(indexes[2]),
                    font_size=50,
                    color=(54 / 255, 54 / 255, 54 / 255, 0.8),
                    pos_hint={'x': 0.2, 'top': 1})
        self.add_widget(iaa)
        self.add_widget(ia)
        self.add_widget(iap)


class LoginPage(Screen):
    def __init__(self, **kwargs):
        super(LoginPage, self).__init__(**kwargs)
        self.__user = str()
        self.__password = str()


class HomePage(Screen):
    def __init__(self, **kwargs):
        super(HomePage, self).__init__(**kwargs)
        self.display_student_name('Gabriel Medeiros das Neves')
        self.show_current_indexes([8.27, 8.00, 8.27])
        self.create_x_text_inputs(['Geração de Idéias e Criatividade em Informática',
                                   'Programação Econômica e Financeira',
                                   'Estruturas de Dados',
                                   'Programação para Web',
                                   'Técnicas Estatísticas de Predição'])

    def display_student_name(self, name):
        student_name = Label(text=name,
                             font_size=60,
                             color=(24/255, 24/255, 24/255, 0.8),
                             pos_hint={'x': 0, 'top': 1.4})
        self.add_widget(student_name)

    def show_current_indexes(self, indexes):
        iaa = Label(text='IAA: ' + str(indexes[0]),
                    font_size=40,
                    color=(44 / 255, 44 / 255, 44 / 255, 0.8),
                    pos_hint={'x': -0.2, 'top': 1.3})
        ia = Label(text='IA: ' + str(indexes[1]),
                   font_size=40,
                   color=(44 / 255, 44 / 255, 44 / 255, 0.8),
                   pos_hint={'x': 0, 'top': 1.3})
        iap = Label(text='IAP: ' + str(indexes[2]),
                    font_size=40,
                    color=(44 / 255, 44 / 255, 44 / 255, 0.8),
                    pos_hint={'x': 0.2, 'top': 1.3})
        self.add_widget(iaa)
        self.add_widget(ia)
        self.add_widget(iap)

    def create_x_text_inputs(self, placeholders):
        gap = -0.07
        for i, placeholder in enumerate(placeholders):
            text_input = TextInput(id='text_input_'+str(i),
                                   font_size=30-(len(placeholders)-5)*3.1,
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
            gap -= 0.35/len(placeholders)


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("iaa_calc_gui.kv")


class IaaCalculator(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__controller = ControllerStudent()
        self.__login_page = kv.get_screen('login')
        self.__home_page = kv.get_screen('home')
        self.__new_indexes_page = kv.get_screen('new_indexes')
        self.__user = str()
        self.__password = str()
        self.__user_browser = None

    def build(self):
        self.title = 'IAA Calculator'
        return kv

    def get_login_values(self):
        self.__user = self.__login_page.ids.login.text
        self.__password = self.__login_page.ids.password.text
        print("Name:", self.__user,
              "\nPassword:", self.__password)
        self.__user_browser = self.__controller.login(self.__user, self.__password)

        self.__login_page.ids.login.text = str()
        self.__login_page.ids.password.text = str()


if __name__ == "__main__":
    IaaCalculator().run()
