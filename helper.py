import re
import copy
from collections import deque
from enum import Enum


class Tuile:

    class Status(Enum):
        clean = 0
        suspect = 1

        def __repr__(self):
            return '<{c!s}.{str!s}>'.format(c=self.__class__.__name__, str=self)

        def __str__(self):
            return self.name

    class Color(Enum):
        rose = 1
        gris = 2
        rouge = 3
        marron = 4
        bleu = 5
        violet = 6
        blanc = 7
        noir = 8

        def __repr__(self):
            return '<{c!s}.{str!s}>'.format(c=self.__class__.__name__, str=self)

        def __str__(self):
            return self.name

    def __init__(self, color: Color, status: Status=None, position: int=None):
        self._color = color
        self._position = position
        self._status = status

    def __repr__(self):
        return '<{c!s}: {str!s}>'.format(c=self.__class__.__name__, str=self)

    def __str__(self):
        return '{_color!s}-{_position!s}-{_status!s}'.format(**self.__dict__)

    @property
    def color(self):
        return self._color

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        self._position = position

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status


class World():

    file_question = 'questions.txt'
    file_response = 'reponses.txt'
    file_info = 'infos.txt'

    class Score():
        def __init__(self, value=None, max=None):
            self.value = value
            self.max = max

        def __repr__(self):
            return '<{c!s}: {str!s}>'.format(c=self.__class__.__name__, str=self)

        def __str__(self):
            return '{value!s}/{max!s}'.format(**self.__dict__)

    class _Parse():

        @staticmethod
        def tuile_dispo(line: str):
            """ ex: Tuiles disponibles : [rose-3-clean, gris-4-clean] choisir entre 0 et 2 """
            q = line
            new_tuiles = {
                Tuile.Color[x[0]]: Tuile(
                    Tuile.Color[x[0]],
                    Tuile.Status[x[2].strip()],
                    int(x[1].strip())
                ) for x in [x.strip().split('-') for x in q[q.index('[') + 1: q.index(']')].split(',')]
            }
            return new_tuiles

        @staticmethod
        def position_dispo(line: str):
            """ positions disponibles : {1, 3}, choisir la valeur """
            q = line
            return [int(x) for x in q[q.index('{') + 1:q.index('}')].split(',')]

        @staticmethod
        def activer_pouvoir(line: str):
            """ Voulez-vous activer le pouvoir (0/1) ?  """
            return [0, 1]

        @staticmethod
        def pouvoir_gris(line: str):
            """ Quelle salle obscurcir ? (0-9) """
            return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        @staticmethod
        def pouvoir_bleu_un(line: str):
            """ Quelle salle bloquer ? (0-9) """
            return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        @staticmethod
        def pouvoir_bleu_deux(line: str):
            """ Quelle sortie ? Chosir parmi : {0, 2} """
            q = line
            return [int(x) for x in q[q.index('{') + 1:q.index('}')].split(',')]

        @staticmethod
        def pouvoir_violet(line: str, lst: list):
            """ Avec quelle couleur échanger (pas violet!) ?  """
            return [x for x in lst if x.color is not Tuile.Color.violet]

        @staticmethod
        def pouvoir_blanc(line: str):
            """ rose-6-suspect, positions disponibles : {5, 7}, choisir la valeur """
            q = line
            [int(x) for x in q[q.index('{') + 1:q.index('}')].split(',')]
            return [int(x) for x in q[q.index('{') + 1:q.index('}')].split(',')]

    def __init__(self, jid: int):
        self._jid = jid
        self._tour = None
        self._score = None
        self._ombre = None
        self._bloque = None
        self._current_tuile = None
        self._list_question = deque([])
        self._hist_tuiles = {
            Tuile.Color.rose: deque([Tuile(Tuile.Color.rose)]),
            Tuile.Color.gris: deque([Tuile(Tuile.Color.gris)]),
            Tuile.Color.rouge: deque([Tuile(Tuile.Color.rouge)]),
            Tuile.Color.marron: deque([Tuile(Tuile.Color.marron)]),
            Tuile.Color.bleu: deque([Tuile(Tuile.Color.bleu)]),
            Tuile.Color.violet: deque([Tuile(Tuile.Color.violet)]),
            Tuile.Color.blanc: deque([Tuile(Tuile.Color.blanc)]),
            Tuile.Color.noir: deque([Tuile(Tuile.Color.noir)]),
        }

    def __repr__(self):
        return '<{c!s}: {str!s}>'.format(c=self.__class__.__name__, str=self)

    def __str__(self):
        return 'Tour={_tour!s}, {_score!s}, Ombre={_ombre!s}, Bloque={_bloque!s}'.format(**self.__dict__)

    def get_all_tuiles(self):
        return {k: self._hist_tuiles[k][0] for k in self._hist_tuiles}

    def get_tuile(self, color):
        if isinstance(color, str):
            return self._hist_tuiles[Tuile.Color[color]][0]
        return self._hist_tuiles[color][0]

    def init_file(self):
        for file in [self.file_info, self.file_response, self.file_question]:
            path = './{jid}/{file}'.format(jid=self._jid, file=file)
            with open(path, 'w+') as f:
                f.write("")

    def pull_question(self, file: str=file_question):
        path = './{jid}/{file}'.format(jid=self._jid, file=file)
        with open(path, 'r') as f:
            return f.read().strip()

    def push_response(self, text, file: str=file_response):
        path = './{jid}/{file}'.format(jid=self._jid, file=file)
        with open(path, 'w') as f:
            return f.write(str(text))

    def is_end(self, file: str=file_info):
        path = './{jid}/{file}'.format(jid=self._jid, file=file)
        with open(path, 'r') as f:
            x = list(f)
            if len(x) > 0:
                return "Score final" in (x[-1])
            return False

    def parse_word_state(self, line: str):
        """
        Tour:3, Score:10/22, Ombre:7, Bloque:{8, 9}
        """

        self._line = line
        r = re.search(r'^Tour:(?P<tour>[0-9]*),'
                      '.*Score:(?P<score-v>[0-9]*)/(?P<score-m>[0-9]*),'
                      '.*Ombre:(?P<ombre>[0-9]*),'
                      '.*Bloque:{(?P<bloque>.*)}$', line)
        self._tour = int(r.group('tour'))
        self._score = self.Score(value=r.group('score-v'),
                                 max=r.group('score-m'))
        self._ombre = int(r.group('ombre'))
        self._bloque = [int(x) for x in r.group('bloque').split(',')]

    def parse_question(self, line: str):
        q = None
        if 'Tuiles disponibles :' in line:
            self._current_tuile = None
            t = self._Parse.tuile_dispo(line)
            self._append_to_hist(t)
            q = Question(self._current_tuile, line, Question.Type.tuile_dispo, t)

        elif 'positions disponibles :' in line:
            q = Question(self._current_tuile, line, Question.Type.position_dispo,
                         self._Parse.position_dispo(line))

        elif 'Voulez-vous activer le pouvoir' in line:
            q = Question(self._current_tuile, line, Question.Type.activer_pouvoir,
                         self._Parse.activer_pouvoir(line))

        # pouvoir gris
        elif 'Quelle salle obscurcir ? (0-9)' in line:
            q = Question(self._current_tuile, line, Question.Type.pouvoir.gris,
                         self._Parse.pouvoir_gris(line))

        # pouvoir bleu 1
        elif 'Quelle salle bloquer ? (0-9)' in line:
            q = Question(self._current_tuile, line, Question.Type.pouvoir.bleu.un,
                         self._Parse.pouvoir_bleu_un(line))

        # pouvoir bleu 2
        elif 'Quelle sortie ? Chosir parmi :' in line:
            q = Question(self._current_tuile, line, Question.Type.pouvoir.bleu.deux,
                         self._Parse.pouvoir_bleu_deux(line))

        # pouvoir violet
        elif 'Avec quelle couleur échanger (pas violet!) ?' in line:
            q = Question(self._current_tuile, line, Question.Type.pouvoir.violet,
                         self._Parse.pouvoir_violet(line, copy.deepcopy(self.get_all_tuiles()).values()))

        # pouvoir blanc
        elif ', positions disponibles :' in line:
            q = Question(self._current_tuile, line, Question.Type.pouvoir.blanc,
                         self._Parse.pouvoir_blanc(line))

        if q is not None:
            self._list_question.appendleft(q)
        return q

    def _append_to_hist(self, lst: list):
        for k, v in self._hist_tuiles.items():
            if k in lst and k != lst[k]:
                self._hist_tuiles[k].appendleft(lst[k])

    @property
    def jid(self):
        return self._jid

    @property
    def tour(self):
        return self._tour

    @property
    def score(self):
        return self._score

    @property
    def ombre(self):
        return self._ombre

    @ombre.setter
    def ombre(self, ombre):
        self._ombre = ombre

    @property
    def bloque(self):
        return self._bloque

    @bloque.setter
    def bloque(self, bloque):
        self._bloque = bloque

    @property
    def current_tuile(self):
        return self._current_tuile

    @current_tuile.setter
    def current_tuile(self, current_tuile: Tuile):
        self._current_tuile = current_tuile

    @property
    def list_question(self):
        return self._list_question

    @property
    def hist_tuiles(self):
        return self._hist_tuiles


class skip(object):
    """
    Protects item from becaming an Enum member during class creation.
    """
    def __init__(self, value):
        self.value = value

    def __get__(self, instance, ownerclass=None):
        return self.value


class Question(list):

    class Type(Enum):
        unknown = 0
        tuile_dispo = 1
        position_dispo = 2
        activer_pouvoir = 3

        @skip
        class pouvoir(Enum):
            gris = 4
            violet = 6
            blanc = 7

            @skip
            class bleu(Enum):
                un = 5.1
                deux = 5.2

                def __repr__(self):
                    return '<{!s}>'.format(self)

                def __str__(self):
                    return 'Type.pouvoir.{!s}.{!s}'.format(type(self).__name__, self.name)

            def __repr__(self):
                return '<{!s}>'.format(self)

            def __str__(self):
                return 'Type.{!s}.{!s}'.format(type(self).__name__, self.name)

        def __repr__(self):
            return '<{!s}>'.format(self)

        def __str__(self):
            return '{!s}.{!s}'.format(type(self).__name__, self.name)
            # return self.name

    def __init__(self, tuile: Tuile, line: str, type: Type, *args):
        self._tuile = tuile
        self._line = line
        self._type = type
        list.__init__(self, *args)

    def __getitem__(self, key):
        return list.__getitem__(self, key)

    def __repr__(self):
        return '<{c!s}:{on!r} {t!r} {s!r}>'.format(c=self.__class__.__name__, on=self._tuile,
                                                   t=self.type, s=list.__repr__(self))

    def __str__(self):
        return '{t!s} {s!s}'.format(t=self.type, s=list.__str__(self))

    @property
    def tuile(self):
        return self._tuile

    @property
    def line(self):
        return self._line

    @property
    def type(self):
        return self._type
