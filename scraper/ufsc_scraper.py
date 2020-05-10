from __future__ import absolute_import, division
from re import compile as _compile
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from robobrowser import RoboBrowser


class UfscScraper:
    def __init__(self):
        pass

    @staticmethod
    def login(user: str, passwd: str):
        """
        Logs the user into CAGR
        :param user: student user
        :param passwd: student password
        :return: Robobrowser instance with logged user
        """
        browser = RoboBrowser(history=True, parser="html.parser")
        browser.open("https://sistemas.ufsc.br/login")

        form = browser.get_form(id="fm1")
        form["username"].value = user
        form["password"].value = passwd
        browser.submit_form(form)

        return browser

    @staticmethod
    def get_student_data(browser):
        """
        Get student name, grades and indexes from CAGR
        :param browser: Robobrowser instance with logged user
        :return: student name, grades and indexes (dict)
        """
        url = "https://cagr.sistemas.ufsc.br/modules/aluno/historicoEscolar/"
        browser.open(url)

        if "collecta" in browser.url:
            browser.submit_form(browser.get_form(id="j_id20"))

        if browser.url != url:
            raise ValueError

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
        """
        Get student current classes names and credits from CAGR
        :param browser: Robobrowser instance with logged user
        :return: student current classes credits and names (list)
        """
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
    def round_ufsc(grade: float):
        """
        Round UFSC grade following the university's rule
        :param grade: grade (between 0 and 10)
        :return: rounded grade (float)
        """
        decimal = grade % 1
        if decimal < 0.25:
            return float(int(grade))
        elif 0.25 <= decimal < 0.75:
            return float(int(grade) + 0.5)
        return float(int(grade) + 1)

    @staticmethod
    def ia_calc(grades):
        return round(sum(h * g for h, g in grades) / sum(h for h, _ in grades), 2)

    def new_indexes(self, current_grades, current_classes_credits, grades):
        new_history = current_grades[:]

        for i in range(len(current_classes_credits)):
            if not (10 >= float(grades[i]) >= 0):
                raise ValueError
            new_history.append([current_classes_credits[i] * 18,
                                self.round_ufsc(float(grades[i]))])

        new_indexes = list(
            map(
                self.ia_calc,
                [
                    new_history,
                    new_history[-len(current_classes_credits):],
                    list(filter(lambda x: x[1] >= 6, new_history)),
                ],
            )
        )

        return new_indexes
