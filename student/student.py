class Student:
    def __init__(self):
        self.__user_browser = None
        self.__name = str()
        self.__grades = list()
        self.__indexes = list()
        self.__current_classes = list()

    @property
    def user_browser(self):
        return self.__user_browser

    @user_browser.setter
    def user_browser(self, user_browser):
        self.__user_browser = user_browser

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def grades(self):
        return self.__grades

    @grades.setter
    def grades(self, grades):
        self.__grades = grades

    @property
    def indexes(self):
        return self.__indexes

    @indexes.setter
    def indexes(self, indexes):
        self.__indexes = indexes

    @property
    def current_classes(self):
        return self.__current_classes

    @current_classes.setter
    def current_classes(self, current_classes):
        self.__current_classes = current_classes
