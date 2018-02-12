from random import randrange

def lancer():
    fini = False
    old_question = ""
    while not fini:
        qf = open('./0/questions.txt','r')
        question = qf.read()
        qf.close()
        if question != old_question :
            rf = open('./0/reponses.txt','w')
            if "activer le pouvoir" in question:
                rf.write(str(1))
            else:
                rf.write(str(0))
            rf.close()
            old_question = question
        infof = open('./0/infos.txt','r')
        fini = "Score" in infof.read()
        infof.close()
    print("partie finie")