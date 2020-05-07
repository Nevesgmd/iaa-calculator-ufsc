from __future__ import absolute_import, division
from model.student import Student
from view.view_student import ViewStudent
from re import compile as _compile
from getpass import getpass
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from robobrowser import RoboBrowser


class ControllerStudent:
    def __init__(self):
        self.__student = Student()
        self.__view = ViewStudent()

    @staticmethod
    def login(user, passwd):
        browser = RoboBrowser(history=True, parser="html.parser")
        browser.open("https://sistemas.ufsc.br/login")

        form = browser.get_form(id="fm1")
        form["username"].value = user
        form["password"].value = passwd
        browser.submit_form(form)

        print(browser)
        return browser

    def get_student_data(self, browser):
        url = "https://cagr.sistemas.ufsc.br/modules/aluno/historicoEscolar/"
        browser.open(url)

        if "collecta" in browser.url:
            browser.submit_form(browser.get_form(id="j_id20"))

        if browser.url != url:
            raise SystemExit("Falha de autenticação!")

        hist = browser.find_all(class_="rich-table-cell")

        if hist[1::7][-1].text == "FORMADO":
            raise SystemExit("Usuário já formado.")

        grades = [
            [int(hours.text), float(grade.text)]
            for hours, grade in zip(hist[2::7], hist[3::7])
            if hours.text
        ]

        try:
            base = "disciplina_footer_col{}"
            indexes = [
                browser.find_all(class_=base.format(i))[-1].text for i in [4, 2, 6]
            ]
        except IndexError:
            raise SystemExit("CAGR indisponível.")

        self.__student.name = browser.find(class_="rich-panel-header").text
        self.__student.grades = grades
        self.__student.indexes = indexes

    def get_current_classes(self, browser):
        url = "https://cagr.sistemas.ufsc.br/modules/aluno/espelhoMatricula/"
        cls = "rich-table-cell"
        browser.open(url)

        cur = browser.find_all(class_=cls, id=_compile("id2"))
        classes = [
            (n.text, int(c.text))
            for n, c in zip(cur[3::10], cur[5::10])
            if len(c.text)
        ]

        if not classes:
            cur = browser.find_all(class_=cls, id=_compile("id15"))
            classes = [
                (n.text, int(h.text))
                for n, h, c in zip(cur[8::9], cur[4::9], cur[5::9])
                if "_" not in c.text
            ]

        self.__student.current_classes = classes

    @staticmethod
    def round_ufsc(grade):
        decimal = grade % 1
        if decimal < 0.25:
            return float(int(grade))
        if 0.25 <= decimal < 0.75:
            return float(int(grade) + 0.5)
        return float(int(grade) + 1)

    @staticmethod
    def ia_calc(grades):
        return sum(h * g for h, g in grades) / sum(h for h, _ in grades)

    @staticmethod
    def loop_input(msg, _type, cond):
        while True:
            try:
                var = _type(input(msg))
                if cond(var):
                    raise ValueError
                return var
            except ValueError:
                pass

    def get_input(self):
        new_history = self.__student.grades

        for name, hours in self.__student.current_classes:
            grade = self.loop_input(
                "Possível nota em {}: ".format(name),
                float,
                lambda x: not 0 <= x <= 10,
            )
            if not hours:
                hours = self.loop_input("Seu número de créditos: ", int, lambda x: x < 0)
            new_history.append([hours * 18, self.round_ufsc(grade)])

        new_indexes = list(
            map(
                self.ia_calc,
                [
                    new_history,
                    new_history[-len(self.__student.current_classes):],
                    list(filter(lambda x: x[1] >= 6, new_history)),
                ],
            )
        )

        print(
            "Com as notas informadas, seus índices serão: {}".format(
                self.__view.print_indexes(new_indexes)
            )
        )

        return lambda x: x and self.get_input()

    def main(self):
        browser = self.login(
            input("Insira sua matrícula ou idUFSC: "),
            getpass("Insira sua senha do CAGR: "),
        )
        self.get_student_data(browser)
        self.get_current_classes(browser)

        print(
            "Olá, {}! Seus índices são: {}".format(
                self.__student.name, self.__view.print_indexes(self.__student.indexes)
            )
        )

        self.loop_input(
            "ENTER para sair, digite algo para novo cálculo: ",
            bool,
            self.get_input(),
        )
