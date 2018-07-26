import sys
import logging
import helper as _
from random import randrange

jid = '1'
role = "l'inspecteur" if jid == '0' else 'le fantome'
space_begin = '      '
formatter = logging.Formatter(
    fmt='%(asctime)s.%(msecs)03d - %(levelname)-8s:{role:12} - %(message)s'.format(role=role),
    datefmt='%H:%M:%S'
)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

log = logging.getLogger(__name__)
log.setLevel(logging.NOTSET)
log.addHandler(handler)

# passage
#
# 8--------9
# |        |
# |        |
# 4--5--6--7
# |        |
# 0--1--2--3
#

# passage secret
#
#   ________
#  /        \
# | 8--------9
# | |\      /|
#  \| \    / |
#   4--5--6--7
#   |  |  |  |\
#   0--1--2--3 |
#       \______/
#


class Process():

    passages = [{1, 4},
                {0, 2},
                {1, 3},
                {2, 7},
                {0, 5, 8},
                {4, 6},
                {5, 7},
                {3, 6, 9},
                {4, 9},
                {7, 8}]
    passages_rose = [{1, 4},
                     {0, 2, 5, 7},
                     {1, 3, 6},
                     {2, 7},
                     {0, 5, 8, 9},
                     {4, 6, 1, 8},
                     {5, 7, 2, 9},
                     {3, 6, 9, 1},
                     {4, 9, 5},
                     {7, 8, 4, 6}]

    def __init__(self, world: _.World):
        self.world = world

    def tuile_dispo(self):
        """
        question: Tuiles disponibles : [rose-3-clean, gris-4-clean] choisir entre 0 et 2
        response: id of the element in the list
        """
        lst = list(self.q)
        if _.Tuile.Color.rouge in lst:
            ret = lst.index(_.Tuile.Color.rouge)
        else:
            ret = randrange(len(lst))
        # for keeping track of the current played 'tuile'
        self.world.current_tuile = self.world.get_tuile(lst[ret])
        return ret

    def position_dispo(self):
        """
        question: positions disponibles : {1, 3}, choisir la valeur
        response: an element of the list
        """
        lst = list(self.q)
        dct = {}
        for v in self.world.get_all_tuiles().values():
            if v.position is None or v.position not in list(self.q):
                continue
            if v.position not in dct:
                dct[v.position] = []
            dct[v.position].append(v)

        for k, v in dct.items():
            log.info(space_begin + '{!s}: {!s}'.format(k, v))

        dct = {k: len(v) for k, v in dct.items()}
        dct = sorted(dct, key=dct.get, reverse=True)

        if len(dct) is not 0:
            ret = dct[0]
        else:
            ret = lst[randrange(len(lst))]
        return ret

    def activer_pouvoir(self):
        """
        question: Voulez-vous activer le pouvoir (0/1) ?
        response: 0 or 1
        """
        use = [_.Tuile.Color.noir, _.Tuile.Color.gris]
        not_use = [_.Tuile.Color.blanc]

        if self.world.current_tuile is None:
            return 0
        if self.world.current_tuile.Color in use:
            return 1
        elif self.world.current_tuile.Color in not_use:
            return 0
        return 1

    def pouvoir_gris(self):
        """
        question: Quelle salle obscurcir ? (0-9)
        response: number between 0 and 9
        """
        lst = list(self.q)
        dct = {}
        for v in self.world.get_all_tuiles().values():
            if v.position is None:
                continue
            if v.position not in dct:
                dct[v.position] = {}
            if v.status not in dct[v.position]:
                dct[v.position][v.status] = []
            dct[v.position][v.status].append(v)

        for k, v in dct.items():
            log.info(space_begin + '{!s}: {!s}'.format(k, v))

        dct = {k: len(v) for k, v in dct.items()}
        dct = sorted(dct, key=dct.get)

        if len(dct) is not 0:
            ret = dct[0]
        else:
            ret = lst[randrange(len(lst))]

        return ret

    def pouvoir_bleu_un(self):
        """
        question: Quelle salle bloquer ? (0-9)
        response: number between 0 and 9
        """
        lst = list(self.q)
        res = randrange(len(lst))
        return res

    def pouvoir_bleu_deux(self):
        """
        question: Quelle sortie ? Chosir parmi : {0, 2}
        response: an element of the list
        """
        lst = list(self.q)
        res = randrange(len(lst))
        return lst[res]

    def pouvoir_violet(self):
        """
        question: Avec quelle couleur échanger (pas violet!) ?
        response: color of an element in the list
        """
        lst = list(self.q)
        res = randrange(len(lst))
        return lst[res].color

    def pouvoir_blanc(self):
        """
        question: rose-6-suspect, positions disponibles : {5, 7}, choisir la valeur
        response: an element of the list
        """
        lst = list(self.q)
        res = randrange(len(lst))
        return lst[res]

    def process_question(self, q: _.Question):
        if q is None:
            return -1

        self.q = q
        log.info('{} {}'.format(space_begin, str(self.q)))
        res = {
            _.Question.Type.unknown: lambda x: log.info(x),
            _.Question.Type.tuile_dispo: self.tuile_dispo,
            _.Question.Type.position_dispo: self.position_dispo,
            _.Question.Type.activer_pouvoir: self.activer_pouvoir,
            _.Question.Type.pouvoir.gris: self.pouvoir_gris,
            _.Question.Type.pouvoir.bleu.un: self.pouvoir_bleu_un,
            _.Question.Type.pouvoir.bleu.deux: self.pouvoir_bleu_deux,
            _.Question.Type.pouvoir.violet: self.pouvoir_violet,
            _.Question.Type.pouvoir.blanc: self.pouvoir_blanc,
        }[self.q.type]()

        return res


def lancer():
    old_question = None

    world = _.World(jid)
    process = Process(world)
    world.init_file()

    while not world.is_end():
        question = world.pull_question()
        if question != old_question and question != "":
            log.info('QUESITON: {}'.format(question))
            res = process.process_question(world.parse_question(question))
            log.info('REPONSE: {}'.format(res))
            world.push_response(res)
            log.info('')
            old_question = question
    log.info('=== END')
