from collections import deque

class Game : #Terrain de la partie
	def __init__(self,matchUid,playerUid,playerId,speed,cellNb,lineNb):
		self.matchUid = matchUid
		self.playerUid = playerUid
		self.speed = speed
		self.playerId = playerId
		self.cellNb = cellNb
		self.lineNb = lineNb
		self.nodes = [] #liste des cellules
		self.myPlayer = Player(playerId,self)
		self.router = Router(self)
		self.edgeCounter = 0
		self.fleetCounter = 0
		self.occupation = {
			"ally":1,
			"ennemy":1,
			"neutral":cellNb-2
		}
		self.lastRefreshTimestamp = 0
		for i in range(cellNb):
			self.nodes.append(0)
		self.edges = [] #liste des aretes
		for i in range(cellNb):
			self.edges.append([])
	
	def generateCells(self,cellDic):
		for cell in cellDic:
			self.nodes[cell['id']] = Node(cell['x'],cell['y'],cell['id'],cell['offsize'],cell['defsize'],cell['prod'],self)
			print("CREATE NODE WITH ID = ",cell['id'])

	def generateLines(self,lineDic):
		for line in lineDic:
			self.edges[line['source']].append(Edge(self.nodes[line['source']],self.nodes[line['target']],line['dist'],self,self.edgeCounter))
			self.edges[line['target']].append(Edge(self.nodes[line['target']],self.nodes[line['source']],line['dist'],self,self.edgeCounter))
			print("CREATE EDGE WITH SOURCE = ",line['source'], " AND TARGET ", line['target'])
	
	def updateCells(self,cellDic):
		for updatedCell in cellDic:
			self.nodes[updatedCell['id']].update(updatedCell['owner'],updatedCell['offunits'],updatedCell['defunits'])

		self.occupation = {
			"ally":0,
			"ennemy":0,
			"neutral":0
		}

		self.myPlayer.clearNodes()
		for node in self.nodes:
			if(node == 0):
				pass
			else:
				if(node.owner == self.playerId):
					self.myPlayer.addNode(node)
					self.occupation['ally'] += 1
				elif(node.owner == -1):
					self.occupation['neutral'] += 1
				else:
					self.occupation['ennemy'] += 1

	def updateMoves(self,movDic):
		for move in movDic:
			for edge in self.edges[move['sourceId']]:
				if(edge.source.id == move['sourceId'] and edge.target.id == move['targetId']):
					edge.addFleet(Fleet(move['owner'],move['sourceId'],move['targetId'],move['unitNb'],edge,move['timestamp'],self.fleetCounter))
					break

	def clearFleets(self):
		for lineGrp in self.edges:
			for line in lineGrp:
				line.clearFleets()

	def generateNeighboors(self):
		for sourceId in self.edges:
			for edge in sourceId:		
				edge.source.neighboors.append(edge.target)
				edge.source.neighboorsEdgesOut.append(edge)
				edge.target.neighboorsEdgesIn.append(edge)

				print("ADDING NEIGHBOOR WITH SOURCE = ", edge.source.id, " AND TARGET ", edge.target.id)
		
		


		#print("NUMBER OF NEIGHBOORS FOR ",node.id, " = ", len(node.neighboors))

	


class Player :
	def __init__(self,id,gameBoard):
		self.myGame = gameBoard
		self.id = id
		self.myNodes = []
		self.startingNode = None
		self.frontNodes = []
		self.importantNodes = []

	def clearNodes(self):
		self.myNodes = []
		self.frontNodes = []

	def addNode(self,node):
		if(self.startingNode == None):
			self.startingNode = node
			print("MY FIRST NODE IS ",node.id)
			self.myGame.router.generateRoutes(self.startingNode)
		if((node.neighboorsType(self.id)['ennemy']) >= 1 or (node.neighboorsType(self.id)['neutral']) >= 1):
			self.frontNodes.append(node)
		self.myNodes.append(node)

	def generateImportantTargets(self):
		maxNeighboors = 2 
		maxProduction = 1
		articulationNodes = []
		productionNodes = []


		for node in self.myGame.nodes:
			if(node.prodSpeedAtq > maxProduction):
				maxProduction = node.prodSpeedAtq
				productionNodes = []
				productionNodes.append(node)

			elif(node.prodSpeedAtq > 1 and node.prodSpeedAtq == maxProduction):
				productionNodes.append(node)

			elif(len(node.neighboors) > 2): # Minimum de 2 voisins pour être considéré comme noeud d'articulation
				if(len(node.neighboors) > maxNeighboors):
					articulationNodes = []
					maxNeighboors = len(node.neighboors)
					articulationNodes.append(node)

				elif(len(node.neighboors) == maxNeighboors):
					articulationNodes.append(node)

		self.importantNodes = productionNodes + articulationNodes
		
		
class Node : #Cellule
	def __init__(self,x,y,id,offSize,defSize,prodSpeed,gameBoard):
		self.myGame = gameBoard
		self.x = x #Coordonnées
		self.y = y #Coordonnées
		self.id = id
		self.owner = -1 #Propriétaire
		self.unitAtq = 0 #Nb d'unités en attaque
		self.unitDef = 0 #Nb d'unités en défense
		self.maxAtq = offSize
		self.maxDef = defSize
		self.prodSpeedAtq = prodSpeed
		self.prodSpeedDef = 1
		self.neighboors = []
		self.neighboorsEdgesOut = []
		self.neighboorsEdgesIn = []
		
	def update(self,owner,offunits,defunits):
		self.owner = owner
		self.unitAtq = offunits
		self.unitDef = defunits

	def powerIn(self):
		power = {}
		for edgesIn in self.neighboorsEdgesIn:
			for fleet in edgesIn.fleets:
				if(power[fleet.owner] == None):
					power[fleet.owner] = fleet.size
				else:
					power[fleet.owner] += fleet.size
		return power

	def neighboorsType(self,myId):
		types = {
			"ally":0,
			"ennemy":0,
			"neutral":0
		}
		for neighboor in self.neighboors:
			if(neighboor.owner == myId):
				types['ally'] += 1
			elif(neighboor.owner == -1):
				types['neutral'] += 1
			else:
				types['ennemy'] += 1
		return types

	def possibleEnnemyIncome(self,myId):
		income = 0
		if(self.owner != -1 and self.owner != myId):
			income += self.unitAtq + self.unitDef
		elif(self.owner == -1):
			income -= self.unitAtq + self.unitDef
		for neighboor in self.neighboors:
			if(neighboor.owner != -1 and neighboor.owner != myId):
				income += neighboor.unitAtq
		for edge in self.neighboorsEdgesIn:
			if(edge.source.id != -1 and edge.source.id != myId):
				income += edge.trafficPower()
		if(income < 0):
			income = 0
		return income

	def possibleAllyIncome(self,myId):
		income = 0
		if(self.owner == myId):
			income += self.unitAtq + self.unitDef
		elif(self.owner == -1):
			income -= self.unitAtq + self.unitDef
		for neighboor in self.neighboors:
			if(neighboor.owner == myId):
				income += neighboor.unitAtq
		for edge in self.neighboorsEdgesIn:
			if(edge.source.id == myId):
				for fleet in edge.fleets:
					income += fleet.size
		return income

	def sortNeighboors(self):
		self.neighboorsEdgesOut = sorted(self.neighboorsEdgesOut, key = lambda edge: (edge.length,edge.target.nodeValue()))
		self.neighboors = []
		for edge in self.neighboorsEdgesOut:
			self.neighboors.append(edge.target)

	def nodeValue(self):
		nbNeighboors = len(self.neighboors)
		prod = self.prodSpeedAtq

		return prod*nbNeighboors

class Edge : #Arête
	def __init__(self,s1,s2,time,gameBoard,id): #Arête de s1 vers s2
		self.myGame = gameBoard
		self.myGame.edgeCounter += 1
		self.source = s1
		self.target = s2
		self.length = time #Longueur (temps en ms)
		self.fleets = [] #liste des Fleet qui la parcourent
		self.id = id

	def clearFleets(self):
		self.fleets = []

	def addFleet(self,fleet):
		self.fleets.append(fleet)

	def trafficPower(self):
		power = 0
		for fleet in self.fleets:
			power += fleet.size
		return power


class Fleet : #Flotte en mouvement
	def __init__(self,owner,src,dst,size,edge,timestamp,id):
		self.myEdge = edge
		self.myEdge.myGame.fleetCounter += 1
		self.owner = owner #Qui possède ces unités
		self.size = size #Taille
		self.source = src #sa source
		self.target = dst #sa destination
		self.timestamp = timestamp # etime au lancement
		self.progress = ((self.myEdge.myGame.lastRefreshTimestamp - self.timestamp) / self.myEdge.length) * self.myEdge.myGame.speed
		self.id = id

class Router :
	def __init__(self,gameBoard):
		self.myGame = gameBoard
		self.ready = False
		self.redirections = [] # Contient les sommets de passage (parent d'un noeud)
		self.redirectionsForHelpers = [] # Contient les sommets de passage (parent d'un noeud) pour les noeuds ne pouvant qu'en aider d'autres
		self.routes = [] # Contient les distances les plus courtes pour chaque noeud et la distance au noeud d'origine
		self.nodeDisposition = {}
		for i in range(self.myGame.cellNb):
			self.routes.append(None)
			self.redirections.append([])
			self.redirectionsForHelpers.append([])

	def generateRoutes(self,startingNode):
		print("GENERATING DEFAULT ROUTES")
		nodeVisited = []
		nextNodes = deque([])
		firstNode = startingNode
		nextNodes.append(startingNode)
		self.routes[firstNode.id]= {
			'length':0,
			'distance':0
		}

		'''
		while(len(nextNodes) > 0):
			myNode = nextNodes.popleft()
			for edge in myNode.neighboorsEdgesOut:
				if(edge.target not in nodeVisited):
					self.redirections[edge.target.id].append(myNode)
					print("DEFAULT REDIRECTION : ",myNode.id," -> ",edge.target.id)
					nextNodes.append(edge.target)
			nodeVisited.append(myNode)
		'''

		nodeVisited = []
		currentNode = firstNode
		nextNode = firstNode

		while(len(nextNodes) > 0):
			currentNode = nextNode
			nextNode = None

			print("NODE NUMBER ", currentNode.id)
			for edge in currentNode.neighboorsEdgesOut:
				if(edge.target not in nodeVisited):
					if(self.routes[edge.target.id] == None or self.routes[edge.target.id]['length'] > self.routes[currentNode.id]['length']+edge.length):
						self.routes[edge.target.id] = {
							'length':self.routes[currentNode.id]['length']+edge.length,
							'distance':self.routes[currentNode.id]['distance']+1
						}
						print("TARGET : ",edge.target.id," DISTANCE : ",self.routes[currentNode.id]['distance']+1)
						if(edge.target not in nodeVisited and edge.target not in nextNodes):
							nextNodes.append(edge.target)
			nodeVisited.append(currentNode.id)
			nextNode = nextNodes.popleft()

		for sourceId in self.myGame.edges:
			for edge in sourceId:
				if(self.routes[edge.target.id]['distance'] >= self.routes[edge.source.id]['distance']):
					self.redirections[edge.target.id].append(edge.source)
					print("DEFAULT REDIRECTION : ",edge.source.id," -> ",edge.target.id)
			

		print("DEFAULT ROUTING TABLE READY")
		self.ready = True
		for node in self.myGame.nodes:
			node.sortNeighboors()
		self.generateHelpingRoutes()
		self.generateNodeDisposition()
		self.myGame.myPlayer.generateImportantTargets()

	def generateHelpingRoutes(self):
		print("GENERATING HELPING ROUTES")
		
		for i in range(len(self.redirections)):
			self.redirectionsForHelpers[i] = self.redirections[i]

		maxDist = 0
		validNodes = []

		for node in self.myGame.nodes:
			found = False
			for successorList in self.redirections:
				if(node in successorList):
					found = True
			if( not found ):
				validNodes.append(node)

		for node in validNodes:
			timesChild = 0
			for neighboor in node.neighboors:
				if(node not in self.redirections[neighboor.id]):
					self.redirectionsForHelpers[neighboor.id].append(node)
					print("HELPING REDIRECTION : ",node.id," -> ",neighboor.id)
			if(timesChild == len(node.neighboors)):
				self.redirectionsForHelpers[node.id] = []
				for neighboor in node.neighboors:
					self.redirectionsForHelpers[neighboor.id].append(node)
					print("HELPING REDIRECTION : ",node.id," -> ",neighboor.id)

		print("HELPING ROUTING TABLE READY")

	def generateNodeDisposition(self):
		for node in self.myGame.nodes:
			dist = self.routes[node.id]['distance']

			if(dist not in self.nodeDisposition):
				self.nodeDisposition[dist] = []
			self.nodeDisposition[dist].append(node)

		for i in range(len(self.nodeDisposition)):
			print("NODES AT DISTANCE ",i," : ",len(self.nodeDisposition[i]))
