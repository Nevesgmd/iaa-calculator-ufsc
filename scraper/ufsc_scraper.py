from __future__ import absolute_import, division
from re import compile as _compile
from getpass import getpass

import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from robobrowser import RoboBrowser


class UfscScraper:
    def __init__(self):
        pass

    @staticmethod
    def login(user, passwd):
        browser = RoboBrowser(history=True, parser="html.parser")
        browser.open("https://sistemas.ufsc.br/login")

        form = browser.get_form(id="fm1")
        form["username"].value = user
        form["password"].value = passwd
        browser.submit_form(form)

        return browser

    @staticmethod
    def get_student_data(browser):
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

        return {
            "name": browser.find(class_="rich-panel-header").text,
            "grades": grades,
            "indexes": indexes,
        }

    @staticmethod
    def get_current_classes(browser):
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

        return classes

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
    def print_indexes(indexes):
        model = "\nIAA: \033[1m{}\033[0m \t IA: {} \t IAP: {}"
        return model.format(*list(map(lambda x: str(x)[:4], indexes)))

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

    def get_input(self, student, current):
        new_history = student["grades"][:]

        for name, hours in current:
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
                    new_history[-len(current) :],
                    list(filter(lambda x: x[1] >= 6, new_history)),
                ],
            )
        )

        print(
            "Com as notas informadas, seus índices serão: {}".format(
                self.print_indexes(new_indexes)
            )
        )

        return lambda x: x and self.get_input(student, current)

    def main(self):
        browser = self.login(
            input("Insira sua matrícula ou idUFSC: "),
            getpass("Insira sua senha do CAGR: "),
        )

        student, current = self.get_student_data(browser), self.get_current_classes(browser)

        print(
            "Olá, {}! Seus índices são: {}".format(
                student["name"], self.print_indexes(student["indexes"])
            )
        )

        self.loop_input(
            "ENTER para sair, digite algo para novo cálculo: ",
            bool,
            self.get_input(student, current),
        )
