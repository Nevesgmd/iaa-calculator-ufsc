import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
Window.clearcolor = (0.85, 0.85, 0.9, 0.8)
Window.size = (700, 400)
Window.minimum_width, Window.minimum_height = (550, 350)


class ViewLoginApp(App):
    def build(self):
        self.title = 'Login'
        return FloatLayout()


if __name__ == "__main__":
    ViewLoginApp().run()
