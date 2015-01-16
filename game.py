class Game : #Terrain de la partie
	def __init__(self,matchUid,playerUid,playerId,speed,cellNb,lineNb):
		self.matchUid = matchUid
		self.playerUid = playerUid
		self.speed = speed
		self.playerId = playerId
		self.cellNb = cellNb
		self.lineNb = lineNb
		self.nodes = [] #liste des cellules
		self.myPlayer = Player(playerId)
		for i in range(cellNb+1):
			self.nodes.append(0)
		self.edges = [] #liste des aretes
		for i in range(cellNb+1):
			self.edges.append([])
	
	def generateCells(self,cellDic):
		for cell in cellDic:
			self.nodes[cell['id']] = Node(cell['id'],cell['offsize'],cell['defsize'],cell['prod'])
			print("CREATE NODE WITH ID = ",cell['id'])

	def generateLines(self,lineDic):
		for line in lineDic:
			self.edges[line['source']].append(Edge(self.nodes[line['source']],self.nodes[line['target']],line['dist']))
			self.edges[line['target']].append(Edge(self.nodes[line['target']],self.nodes[line['source']],line['dist']))
			print("CREATE EDGE WITH SOURCE = ",line['source'], " AND TARGET ", line['target'])
	
	def updateCells(self,cellDic):
		for updatedCell in cellDic:
			self.nodes[updatedCell['id']].update(updatedCell['owner'],updatedCell['offunits'],updatedCell['defunits'])

		self.myPlayer.clearNodes()
		for node in self.nodes:
			if(node == 0):
				pass
			else:
				if(node.owner == self.playerId):
					self.myPlayer.addNode(node)

	def updateMoves(self,movDic):
		for move in movDic:
			for edge in self.edges[move['sourceId']]:
				print("DEBUGGING 'EDGE ERROR': ",edge)
				if(edge.source.id == move['sourceId'] and edge.target.id == move['targetId']):
					edge.addFleet(Fleet(move['owner'],move['sourceId'],move['targetId'],move['unitNb']))
					break

	def clearFleets(self):
		for lineGrp in self.edges:
			for line in lineGrp:
				line.clearFleets()

	def generateNeighboors(self):
		for node in self.nodes:
			if(node == 0):
				pass
			else:
				for edge in self.edges[node.id]:
					node.neighboors.append(edge.target)
					node.neighboorsEdges.append(edge)
					print("ADDING NEIGHBOOR WITH SOURCE = ", edge.source.id, " AND TARGET ", edge.target.id)
				print("NUMBER OF NEIGHBOORS FOR ",node.id, " = ", len(node.neighboors))

class Player :
	def __init__(self,id):
		self.id = id
		self.myNodes = []

	def clearNodes(self):
		self.myNodes = []

	def addNode(self,node):
		self.myNodes.append(node)

class Node : #Cellule
	def __init__(self,id,offSize,defSize,prodSpeed):
		self.x = 0 #Coordonnées
		self.y = 0 #Coordonnées
		self.id = id
		self.owner = -1 #Propriétaire
		self.unitAtq = 0 #Nb d'unités en attaque
		self.unitDef = 0 #Nb d'unités en défense
		self.maxAtq = offSize
		self.maxDef = defSize
		self.prodSpeedAtq = 1
		self.prodSpeedDef = prodSpeed
		self.neighboors = []
		self.neighboorsEdges = []
		
	def update(self,owner,offunits,defunits):
		self.owner = owner
		self.unitAtq = offunits
		self.unitDef = defunits

	def powerIn(self):
		power = {}
		for edgesIn in self.neighboorsEdges:
			for fleet in edgesIn.fleets:
				if(power[fleet.owner] == None):
					power[fleet.owner] = fleet.size
				else:
					power[fleet.owner] += fleet.size
		return power

class Edge : #Arête
	def __init__(self,s1,s2,time): #Arête de s1 vers s2
		self.source = s1
		self.target = s2
		self.length = time #Longueur (temps en ms)
		self.fleets = [] #liste des Fleet qui la parcourent

	def clearFleets(self):
		self.fleets = []

	def addFleet(self,fleet):
		self.fleets.append(fleet)

class Fleet : #Flotte en mouvement
	def __init__(self,owner,src,dst,size):
		self.owner = owner #Qui possède ces unités
		self.size = size #Taille
		self.source = src #sur quelle arete elle se trouve
		self.target = dst #sa destination
