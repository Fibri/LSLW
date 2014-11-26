import Math

class Game :
    def __init__(self):
        self.nodes = []
        self.edges = []

class Node :
    def __init__(self,x,y,id):
    	self.x = x
    	self.y = y
        self.id = id
        self.owner = None
        self.population = 0
        self.production = 1
        self.defense = 0

class Edge :
    def __init__(self,id,s1,s2): #Arrête de s1 vers s2
        self.id = id
        self.sommet1 = s1
        self.sommet2 = s2
        self.length = Math.sqrt((s1.x-s2.x)**2+(s1.y-s2.y)**2)
        self.pop = 0 #Combien d'unités parcourent cette arrête
        self.owner = None #Qui possède ces unités

class Fleet :
    def __init__(self,id,edge,to,nb):
        self.id = id
        self.edge = edge
        self.to = to
        self.nb = nb
        self.progress = 0