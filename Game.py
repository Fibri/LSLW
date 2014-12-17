import Math

class Game : #Terrain de la partie
    def __init__(self):
        self.nodes = [] #liste des cellules
        self.edges = [] #liste des aretes

class Node : #Cellule
    def __init__(self,x,y,id):
    	self.x = x #Coordonnées
    	self.y = y #Coordonnées
        self.id = id
        self.owner = None #Propriétaire
        self.unitAtq = 0 #Nb d'unités en attaque
        self.unitDef = 0 #Nb d'unités en défense
        self.prodSpeedAtq = 1
        self.prodSpeedDef = 1
        self.maxUnit = 1 #Capacité de la case

class Edge : #Arête
    def __init__(self,id,s1,s2): #Arête de s1 vers s2
        self.id = id
        self.sommet1 = s1
        self.sommet2 = s2
        self.length = Math.sqrt((s1.x-s2.x)**2+(s1.y-s2.y)**2) #Longueur (temps ?)
        self.fleets = [] #liste des Fleet qui la parcourent

class Fleet : #Flotte en mouvement
    def __init__(self,id,edge,to,size):
        self.id = id
        self.owner = None #Qui possède ces unités
        self.size = 1 #Taille
        self.edge = 1 #sur quel arete elle se trouve
        self.to = 0 #sa destination
        self.progress = 0 #%age de son voyage accompli
