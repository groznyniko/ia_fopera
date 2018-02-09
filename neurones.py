from math import exp,sqrt
from random import randrange

class neurone:
    def __init__(self,a,b):
        self.a=a
        self.b=b
    def proceed(self,z):
        t = z[0]*self.a + z[1]*self.b
        return 1/(1+exp(-t))

n = 100
X_app = [(randrange(-500,501)/1000,randrange(-500,501)/1000) for i in range(n)]
Y_app = [1 if ((x[0]-0.3)+(x[1]-0.3))<0.2 else 0 for x in X_app]

a=1
Y_pred,Y_score = [None for i in range(1001)], [None for i in range(1001)] 
for i in range(1001):
    b=i/1000*4-1
    ne = neurone(a,b)
    Y_pred[i] = [ne.proceed(z) for z in X_app]
    Y_score[i] = sum([abs(Y_pred[i][j]-Y_app[j]) for j in range(n)])
opt = min(Y_score)
print(Y_score)