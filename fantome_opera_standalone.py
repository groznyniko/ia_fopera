from random import shuffle,randrange

permanents = {'rose'}
deux = {'rouge','gris','bleu'}
avant = {'violet','marron'}
apres = {'noir','blanc'}
couleurs = avant | permanents | apres | deux
passages = [{1,4},{0,2},{1,3},{2,7},{0,5,8},{4,6},{5,7},{3,6,9},{4,9},{7,8}]
pass_ext = [{1,4},{0,2,5,7},{1,3,6},{2,7},{0,5,8,9},{4,6,1,8},{5,7,2,9},{3,6,9,1},{4,9,5},{7,8,4,6}] 

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
        print("****\n Tour de "+self.role)
        p = self.selectionner(party.tuiles_actives)
        avec = self.activer_pouvoir(p,party,avant|deux)
        self.bouger(p,avec,party.bloque)
        self.activer_pouvoir(p,party,apres|deux)
    def selectionner(self,t):
        w = input("Tuiles disponibles : " + str(t) + " choisir entre 0 et " + str(len(t)-1))
        i = int(w) if w.isnumeric() and int(w) in range(len(t)) else 0
        p = t[i]
        print(self.role + " joue " + p.couleur)
        del t[i]
        return p
    def activer_pouvoir(self,p,party,activables):
        if p.pouvoir and p.couleur in activables:
            a = input("Voulez-vous activer le pouvoir (0/1) ?") == "1"
            if a :
                print("Pouvoir de " + p.couleur + " activé")
                p.pouvoir = False
                if p.couleur == "rouge":
                    draw = party.cartes[0]
                    print(str(draw) + " a été tiré")
                    if draw == "fantome":
                        party.start += self.numero
                    elif self.numero == 0:
                        draw.suspect = False
                    del party.cartes[0]
                if p.couleur == "noir":
                    for q in party.personnages:
                        if q.position in {x for x in passages[p.position] if x not in party.bloque or q.position not in party.bloque} :
                            q.position = p.position
                if p.couleur == "blanc":
                    for q in party.personnages:
                        if q.position == p.position and p != q:
                            x = int(input(str(q) + ", positions disponibles : " + str({x for x in passages[p.position] if x not in party.bloque or q.position not in party.bloque}) + ", choisir la valeur"))
                            q.position = x
                if p.couleur == "violet":
                    print("Rappel des positions :\n" + str(party))
                    co = input("Avec quelle couleur échanger (pas violet!) ?")
                    if co not in couleurs:
                        co = "rose"
                    q = [x for x in party.personnages if x.couleur == co][0]
                    p.position, q.position = q.position, p.position
                if p.couleur == "marron":
                    return [q for q in party.personnages if p.position == q.position]
                if p.couleur == "gris":
                    w = input("Quelle salle obscurcir ? (0-9)")
                    party.shadow = int(w) if w.isnumeric() and int(w) in range(10) else (party.shadow+1)%10
                if p.couleur == "bleu":
                    w = input(input("Quelle salle bloquer ? (0-9)"))
                    x = int(w) if w.isnumeric() and int(w) in range(10) else (party.bloque[0]+1)%10
                    w = input("Quelle sortie ? Chosir parmi : "+str(passages[x]))
                    y = int(w) if w.isnumeric() and int(w) in passages[x] else passages[x].copy().pop()
                    party.bloque = {x,y}
        return [p]
                    
    def bouger(self,p,avec,bloque):
        pass_act = pass_ext if p.couleur == 'rose' else passages
        if p.couleur != 'violet' or p.pouvoir:
            disp = {x for x in pass_act[p.position] if p.position not in bloque or x not in bloque}
            w = input("positions disponibles : " + str(disp) + ", choisir la valeur")
            x = int(w) if w.isnumeric() and int(w) in disp else disp.pop()
            for q in avec:
                q.position = x

class partie:
    def __init__(self):
        self.start, self.end, self.num_tour, self.shadow, x = 4, 22, 1, randrange(10), randrange(10)
        self.bloque = {x,passages[x].copy().pop()}
        self.personnages = {personnage(c) for c in couleurs}
        self.tuiles = [p for p in self.personnages]
        self.cartes = self.tuiles[:]
        self.fantome = self.cartes[randrange(8)]
        self.cartes.remove(self.fantome)
        self.cartes += ['fantome']*3
        self.joueurs = [joueur(0),joueur(1)]
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
            print("le fantome frappe")
            self.start += 1
            for piece,gens in enumerate(partition):
                if len(gens) > 1 and piece != self.shadow:
                    for p in gens:
                        p.suspect = False
        else:
            print("pas de cri")
            for piece,gens in enumerate(partition):
                if len(gens) == 1 or piece == self.shadow:
                    for p in gens:
                        p.suspect = False
        self.start += len([p for p in self.personnages if p.suspect])
            
    def tour(self):
        print("**************************\n" + str(self))
        self.actions()
        self.lumiere()
        for p in self.personnages:
            p.pouvoir = True
        self.num_tour += 1
    def lancer(self):
        while self.start < self.end and len([p for p in self.personnages if p.suspect]) > 1:
            self.tour()
        print("L'enquêteur a trouvé - c'était " + str(self.fantome) if self.start < self.end else "Le fantôme a gagné")
    def __repr__(self):
        return "Tour:" + str(self.num_tour) + ", Score:"+str(self.start)+"/"+str(self.end) + ", Ombre:" + str(self.shadow) + ", Bloque:" + str(self.bloque) +"\n" + "  ".join([str(p) for p in self.personnages])

pa = partie()
pa.lancer()