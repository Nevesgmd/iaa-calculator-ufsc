from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
Window.clearcolor = (0.85, 0.85, 0.9, 0.8)
Window.size = (700, 400)
Window.minimum_width, Window.minimum_height = (550, 350)


class LoginPage(Screen):
    def return_values(self):
        login = self.ids.login.text
        password = self.ids.password.text

        print("Name:", login,
              "\nPassword:", password)
        self.ids.login.text = ""
        self.ids.password.text = ""


class SecondWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("iaa_calc_gui.kv")


class MyMainApp(App):
    def build(self):
        self.title = 'Login'
        return kv


if __name__ == "__main__":
    MyMainApp().run()