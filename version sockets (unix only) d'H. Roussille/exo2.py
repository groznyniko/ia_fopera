from random import shuffle,randrange
from time import sleep
from threading import Thread
import dummy0_ex2, dummy1

latence = 0.001
permanents, deux, avant, apres = {'rose'}, {'rouge','gris','bleu'}, {'violet','marron'}, {'noir','blanc'}
couleurs = avant | permanents | apres | deux
passages = [{1,4},{0,2},{1,3},{2,7},{0,5,8},{4,6},{5,7},{3,6,9},{4,9},{7,8}]
pass_ext = [{1,4},{0,2,5,7},{1,3,6},{2,7},{0,5,8,9},{4,6,1,8},{5,7,2,9},{3,6,9,1},{4,9,5},{7,8,4,6}]

def message(texte,jos):
    for j in jos:
        f = open("./"+str(j.numero)+"/infos.txt","a")
        f.write(texte + "\n")
        f.close()

def informer(texte):
    message(texte,joueurs)

def demander(q,j):
    informer("QUESTION : "+q)
    f = open("./"+str(j.numero)+"/questions"+".txt","w")
    f.write(q)
    f.close()
    sleep(latence)
    f = open("./"+str(j.numero)+"/reponses"+".txt","r")
    r = f.read()
    f.close()
    informer("REPONSE DONNEE : "+r)
    return r

class personnage:
    def __init__(self,couleur):
        self.couleur, self.suspect, self.position, self.pouvoir = couleur, True, 0, True
    def __repr__(self):
        susp = "-suspect" if self.suspect else "-clean"
        return self.couleur + "-" + str(self.position) + susp
            
class joueur:
    def __init__(self,n):
        self.numero = n
        self.role = "l'inspecteur" if n == 0 else "le fantome"
    def jouer(self,party):
        informer("****\n  Tour de "+self.role)
        p = self.selectionner(party.tuiles_actives)
        avec = self.activer_pouvoir(p,party,avant|deux)
        self.bouger(p,avec,party.bloque)
        self.activer_pouvoir(p,party,apres|deux)
    def selectionner(self,t):
        w = demander("Tuiles disponibles : " + str(t) + " choisir entre 0 et " + str(len(t)-1),self)
        i = int(w) if w.isnumeric() and int(w) in range(len(t)) else 0
        p = t[i]
        informer("REPONSE INTERPRETEE : "+str(p))
        informer(self.role + " joue " + p.couleur)
        del t[i]
        return p
    def activer_pouvoir(self,p,party,activables):
        if p.pouvoir and p.couleur in activables:
            a = demander("Voulez-vous activer le pouvoir (0/1) ?",self) == "1"
            informer("REPONSE INTERPRETEE : "+str(a==1))
            if a :
                informer("Pouvoir de " + p.couleur + " activé")
                p.pouvoir = False
                if p.couleur == "rouge":
                    draw = party.cartes[0]
                    informer(str(draw) + " a été tiré")
                    if draw == "fantome":
                        party.start += -1 if self.numero == 0 else 1
                    elif self.numero == 0:
                        draw.suspect = False
                    del party.cartes[0]
                if p.couleur == "noir":
                    for q in party.personnages:
                        if q.position in {x for x in passages[p.position] if x not in party.bloque or q.position not in party.bloque} :
                            q.position = p.position
                            informer("NOUVEAU PLACEMENT : "+str(q))
                if p.couleur == "blanc":
                    for q in party.personnages:
                        if q.position == p.position and p != q:
                            dispo = {x for x in passages[p.position] if x not in party.bloque or q.position not in party.bloque}
                            w = demander(str(q) + ", positions disponibles : " + str(dispo) + ", choisir la valeur",self)
                            x = int(w) if w.isnumeric() and int(w) in dispo else dispo.pop()
                            informer("REPONSE INTERPRETEE : "+str(x))
                            q.position = x
                            informer("NOUVEAU PLACEMENT : "+str(q))
                if p.couleur == "violet":
                    informer("Rappel des positions :\n" + str(party))
                    co = demander("Avec quelle couleur échanger (pas violet!) ?",self)
                    if co not in couleurs:
                        co = "rose"
                    informer("REPONSE INTERPRETEE : "+co)
                    q = [x for x in party.personnages if x.couleur == co][0]
                    p.position, q.position = q.position, p.position
                    informer("NOUVEAU PLACEMENT : "+str(p))
                    informer("NOUVEAU PLACEMENT : "+str(q))
                if p.couleur == "marron":
                    return [q for q in party.personnages if p.position == q.position]
                if p.couleur == "gris":
                    w = demander("Quelle salle obscurcir ? (0-9)",self)
                    party.shadow = int(w) if w.isnumeric() and int(w) in range(10) else (party.shadow+1)%10
                    informer("REPONSE INTERPRETEE : "+str(party.shadow))
                if p.couleur == "bleu":
                    w = demander("Quelle salle bloquer ? (0-9)",self)
                    x = int(w) if w.isnumeric() and int(w) in range(10) else 0
                    w = demander("Quelle sortie ? Chosir parmi : "+str(passages[x]),self)
                    y = int(w) if w.isnumeric() and int(w) in passages[x] else passages[x].copy().pop()
                    informer("REPONSE INTERPRETEE : "+str({x,y}))       
                    party.bloque = {x,y}
        return [p]
                    
    def bouger(self,p,avec,bloque):
        pass_act = pass_ext if p.couleur == 'rose' else passages
        if p.couleur != 'violet' or p.pouvoir:
            disp = {x for x in pass_act[p.position] if p.position not in bloque or x not in bloque}
            w = demander("positions disponibles : " + str(disp) + ", choisir la valeur",self)
            x = int(w) if w.isnumeric() and int(w) in disp else disp.pop()
            informer("REPONSE INTERPRETEE : "+str(x))
            for q in avec:
                q.position = x
                informer("NOUVEAU PLACEMENT : "+str(q))

class partie:
    def __init__(self,joueurs):
        for i in [0,1]:
            f = open("./"+str(i)+"/infos"+".txt","w")
            f.write("")
            f.close()
        self.joueurs = joueurs
        self.start, self.end, self.num_tour, self.shadow, x = 4, 22, 1, randrange(10), randrange(10)
        self.bloque = {x,passages[x].copy().pop()}
        self.personnages = {personnage(c) for c in couleurs}
        self.tuiles = [p for p in self.personnages]
        self.cartes = self.tuiles[:]
        self.fantome = self.cartes[randrange(8)]
        message("!!! Le fantôme est : "+self.fantome.couleur,[self.joueurs[0]])
        self.cartes.remove(self.fantome)
        self.cartes += ['fantome']*3
        
        shuffle(self.tuiles)
        shuffle(self.cartes)
        for i,p in enumerate(self.tuiles):
            p.position = i
    def actions(self):
        joueur_actif = self.num_tour % 2
        if joueur_actif == 1:
            shuffle(self.tuiles)
            self.tuiles_actives = self.tuiles[:4]
        else:
            self.tuiles_actives = self.tuiles[4:]
        for i in [joueur_actif,1-joueur_actif,1-joueur_actif,joueur_actif]:
            self.joueurs[i].jouer(self)
    def lumiere(self):
        partition = [{p for p in self.personnages if p.position == i} for i in range(10)]
        if len(partition[self.fantome.position]) == 1 or self.fantome.position == self.shadow:
            informer("le fantome frappe")
            self.start += 1
            for piece,gens in enumerate(partition):
                if len(gens) > 1 and piece != self.shadow:
                    for p in gens:
                        p.suspect = False
        else:
            informer("pas de cri")
            for piece,gens in enumerate(partition):
                if len(gens) == 1 or piece == self.shadow:
                    for p in gens:
                        p.suspect = False
        self.start += len([p for p in self.personnages if p.suspect])
            
    def tour(self):
        informer("**************************\n" + str(self))
        self.actions()
        self.lumiere()
        for p in self.personnages:
            p.pouvoir = True
        self.num_tour += 1
    def lancer(self):
        while self.start < self.end and len([p for p in self.personnages if p.suspect]) > 1:
            self.tour()
        informer("L'enquêteur a trouvé - c'était " + str(self.fantome) if self.start < self.end else "Le fantôme a gagné")
        informer("Score final : "+str(self.end-self.start))
        return self.end-self.start
    def __repr__(self):
        return "Tour:" + str(self.num_tour) + ", Score:"+str(self.start)+"/"+str(self.end) + ", Ombre:" + str(self.shadow) + ", Bloque:" + str(self.bloque) +"\n" + "  ".join([str(p) for p in self.personnages])

score = []
joueurs = [joueur(0),joueur(1)]
nbparties = 100
for i in range(nbparties):
    t1,t2 = Thread(target=dummy0_ex2.lancer), Thread(target=dummy1.lancer)
    t1.start()
    t2.start()
    score.append(partie(joueurs).lancer())
    t1.join()
    t2.join()
victoires = [x for x in score if x<=0]
print("Efficacité : "+str(len(victoires)/nbparties*100)+"%")