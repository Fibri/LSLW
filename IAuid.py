# -*- coding: utf-8 -*-

import re
import parse
import game as game
import hud
import random

"""Robot-joueur de Pooo
	
	Le module fournit les fonctions suivantes :
		register_pooo(uid)
		init_pooo(init_string)
		play_pooo()
		
"""

__version__='0.1'
 
## chargement de l'interface de communication avec le serveur
from poooc import order, state, state_on_update, etime

# mieux que des print partout
import logging
# pour faire de l'introspection
import inspect

global playerId
playerId = ""
global gameBoard
gameBoard = None
global globalState
globalState = None

def register_pooo(uid):
	global playerId
	playerId = uid
	
	#REG<uid>
	#REG0947e717-02a1-4d83-9470-a941b6e8ed07
	order("REG"+uid)
	"""Inscrit un joueur et initialise le robot pour la compétition
		:param uid: identifiant utilisateur
		:type uid:  chaîne de caractères str(UUID) 
		
		:Example:
		"0947e717-02a1-4d83-9470-a941b6e8ed07"
	"""
	pass


def init_pooo(init_string):
	
	p = re.compile('INIT([A-z0-9-]*)TO(.*)\[(.*)\];(.);(\d+)CELLS:(.*);(\d+)LINES:(.*)')
 
	res = re.search(p, init_string)
	groups = res.groups()
	
	"""
	Groups :
	0 : matchid
	1 : #players
	2 : my player number
	3 : speed
	4 : #cells
	5 : cell data
	6 : #lines
	7 : line data
	"""
	gameData = {
		'matchid':groups[0],
		'playerNb':int(groups[1]),
		'myId':int(groups[2]),
		'speed':int(groups[3]),
		'cellNb':int(groups[4]),
		'cellData':parse.parseCellsInit(groups[5]),
		'lineNb':int(groups[6]),
		'lineData':parse.parseLinesInit(groups[7])
	}
	
	global gameBoard
	gameBoard = game.Game(gameData['matchid'],playerId,gameData['myId'],gameData['speed'],gameData['cellNb'],gameData['lineNb'])
	gameBoard.generateCells(gameData['cellData'])
	gameBoard.generateLines(gameData['lineData'])
	gameBoard.generateNeighboors()
		
	
	"""Initialise le robot pour un match
		:param init_string: instruction du protocole de communication de Pooo (voire ci-dessous)
		:type init_string: chaîne de caractères (utf-8 string)
	   
	   INIT<matchid>TO<#players>[<me>];<speed>;\
	   <#cells>CELLS:<cellid>(<x>,<y>)'<radius>'<offsize>'<defsize>'<prod>,...;\
	   <#lines>LINES:<cellid>@<dist>OF<cellid>,...

	   <me> et <owner> désignent des numéros de 'couleur' attribués aux joueurs. La couleur 0 est le neutre.
	   le neutre n'est pas compté dans l'effectif de joueurs (<#players>).
	   '...' signifie que l'on répète la séquence précédente autant de fois qu'il y a de cellules (ou d'arêtes).
	   0CELLS ou 0LINES sont des cas particuliers sans suffixe.
	   <dist> est la distance qui sépare 2 cellules, exprimée en... millisecondes !
	   /!\ attention: un match à vitesse x2 réduit de moitié le temps effectif de trajet d'une cellule à l'autre par rapport à l'indication <dist>.
	   De manière générale temps_de_trajet=<dist>/vitesse (division entière).
		
		:Example:
		"INIT20ac18ab-6d18-450e-94af-bee53fdc8fcaTO6[2];1;3CELLS:1(23,9)'2'30'8'I,2(41,55)'1'30'8'II,3(23,103)'1'20'5'I;2LINES:1@3433OF2,1@6502OF3"
	"""
	pass

	
def play_pooo():
	"""Active le robot-joueur
	"""
	logging.info('Entering play_pooo fonction from {} module...'.format(inspect.currentframe().f_back.f_code.co_filename))
	### Début stratégie joueur ### 
	# séquence type :
	# (1) récupère l'état initial 
	init_state = state()

	parse.analyzeState(init_state,gameBoard.matchUid)

	global window
	
	window = hud.HUD(gameBoard,Analyzer())

	print("WILL INIT MAP")
	window.initMap()
	'''
	# (2) TODO: traitement de init_state
	print("Bot started !!!")
	isRunning = True
	while isRunning :

		try:

			state2 = state_on_update()
			print(state2)
			data = parse.analyzeState(state2,gameBoard.matchUid)
			if(data['type'] == 'STATE'):
				globalState = data['data']

				gameBoard.clearFleets()
				gameBoard.updateCells(globalState['cellData'])
				gameBoard.updateMoves(globalState['moveData'])

				# PUT THE STRATEGY HERE
				# HERE !!!!
				# Current State => globalState
				# (Voir dans parse.py -> analyseState() pour plus de détails)
				# Classes du jeu dans gameBoard
				# (Voir game.py -> Game() pour plus d'infos)

				window.draw()


				# IA IDLE 
				# NE RIEN AJOUTER !!!




			elif(data['type'] == 'GAMEOVER'):
				if(data['data'] == 1):
					print("we won !!! [" , playerId,"]")
			elif(data['type'] == 'ENDOFGAME'):
				print("end of process")
				isRunning = False
		except KeyboardInterrupt:
			isRunning = False
			print("STOPPING THE CLIENT BECAUSE OF CTRL + C")

	# (5)     TODO: traitement de state et transmission d'ordres order(msg)
	
	#order(parse.createMoveOrder(cellFrom,cellTo,cellNb,playerId))
	
	
	
#init_pooo("INIT20ac18ab-6d18-450e-94af-bee53fdc8fcaTO6[2];1;3CELLS:1(23,9)'2'30'8'I,2(41,55)'1'30'8'II,3(23,103)'1'20'5'I;2LINES:1@3433OF2,1@6502OF3")
#print(parse.analyzeState("STATE20ac18ab-6d18-450e-94af-bee53fdc8fcaIS2;3CELLS:1[2]12'4,2[2]15'2,3[1]33'6;4MOVES:1<5[2]@232'>6[2]@488'>3[1]@4330'2,1<10[1]@2241'3"))
	'''
class Analyzer:
	def __init__(self):
		self.isRunning = True
		self.isFinished = False
		self.importantTarget = gameBoard.nodes[3]
		self.orderStack = []
		self.needSorting = False

	def analyzeIAidle(self):
		global gameBoard
		global globalState
		global window

		state2 = state_on_update()
		print(state2)
		data = parse.analyzeState(state2,gameBoard.matchUid)
		if(data['type'] == 'STATE'):
			globalState = data['data']

			gameBoard.clearFleets()
			gameBoard.updateCells(globalState['cellData'])
			gameBoard.updateMoves(globalState['moveData'])
			gameBoard.lastRefreshTimestamp = etime()

			# PUT THE STRATEGY HERE
			# HERE !!!!
			# Current State => globalState
			# (Voir dans parse.py -> analyseState() pour plus de détails)
			# Classes du jeu dans gameBoard
			# (Voir game.py -> Game() pour plus d'infos)


			# IA IDLE 
			# NE RIEN AJOUTER !!!

		elif(data['type'] == 'GAMEOVER'):
			if(data['data'] == 1):
				print("we won !!! [" , playerId,"]")
		elif(data['type'] == 'ENDOFGAME'):
			print("end of process")
			self.isRunning = False

	def analyzeIArandom(self):
		global gameBoard
		global globalState
		global window

		state2 = state_on_update()
		print(state2)
		data = parse.analyzeState(state2,gameBoard.matchUid)
		if(data['type'] == 'STATE'):
			globalState = data['data']

			gameBoard.clearFleets()
			gameBoard.updateCells(globalState['cellData'])
			gameBoard.updateMoves(globalState['moveData'])
			gameBoard.lastRefreshTimestamp = etime()

			# PUT THE STRATEGY HERE
			# HERE !!!!
			# Current State => globalState
			# (Voir dans parse.py -> analyseState() pour plus de détails)
			# Classes du jeu dans gameBoard
			# (Voir game.py -> Game() pour plus d'infos)

			if(gameBoard.cellNb == len(gameBoard.myPlayer.myNodes)):
				pass
			else:
				if(len(gameBoard.myPlayer.myNodes) > 0):
					
					print("==========[",len(gameBoard.myPlayer.myNodes),"/",gameBoard.cellNb,"]==========")

					tmp_rdm = random.randint(0,len(gameBoard.myPlayer.myNodes)-1)
					node_rdm = gameBoard.myPlayer.myNodes[tmp_rdm]

					tmp_rdm = random.randint(0,len(node_rdm.neighboors)-1)
					target_rdm = node_rdm.neighboors[tmp_rdm]

					if(node_rdm.unitAtq > 0):
						order(parse.createMoveOrder(node_rdm,target_rdm.id,node_rdm.unitAtq,playerId))

		elif(data['type'] == 'GAMEOVER'):
			if(data['data'] == 1):
				print("we won !!! [" , playerId,"]")
		elif(data['type'] == 'ENDOFGAME'):
			print("end of process")
			self.isRunning = False

	def analyzeIAlittle(self):
		global gameBoard
		global globalState
		global window

		state2 = state_on_update()
		print(state2)
		data = parse.analyzeState(state2,gameBoard.matchUid)
		if(data['type'] == 'STATE'):
			globalState = data['data']

			gameBoard.clearFleets()
			gameBoard.updateCells(globalState['cellData'])
			gameBoard.updateMoves(globalState['moveData'])
			gameBoard.lastRefreshTimestamp = etime()

			# PUT THE STRATEGY HERE
			# HERE !!!!
			# Current State => globalState
			# (Voir dans parse.py -> analyseState() pour plus de détails)
			# Classes du jeu dans gameBoard
			# (Voir game.py -> Game() pour plus d'infos)


			if(gameBoard.cellNb == len(gameBoard.myPlayer.myNodes)):
				print("WE CAPTURED EVERY NODE !!! ~yay")
				self.isFinished = True
			elif(len(gameBoard.myPlayer.myNodes) == 0):
				print("WE LOST D=")
				self.isFinished = True
			else:
				print("==========[",len(gameBoard.myPlayer.myNodes),"/",gameBoard.cellNb,"]==========")
				if(len(self.orderStack) > 0):
					print("=====THROWING ORDERS !!! ",len(self.orderStack), " REMAINING")
					if(self.needSorting):
						orderStack = sorted(self.orderStack, key=lambda order: order[1])
						print(self.orderStack)
					order(self.orderStack.pop()[0])
					self.needSorting = False
				else:
					print("=====ANALYZING THE MAP")

					if(self.importantTarget.owner != gameBoard.playerId):
						tmp_target = self.importantTarget

						while(gameBoard.router.redirections[tmp_target.id] != None and gameBoard.router.redirections[tmp_target.id].owner != gameBoard.playerId):
							tmp_target = gameBoard.router.redirections[tmp_target.id]
						tmp_source = gameBoard.router.redirections[tmp_target.id] # Selectionne le noeud prédécesseur comme source du prochain noeud à capturer

						print("=========== NEXT CAPTURE IS ",tmp_target.id)

						if(tmp_source != None and tmp_target != None and tmp_source.unitAtq > tmp_target.unitAtq + tmp_target.unitDef):
							self.orderStack.append((parse.createMoveOrder(tmp_source,tmp_target.id,tmp_source.unitAtq,playerId),20)) # Order for capture

						roadList = []
						# Orders for helpers in the chain
						while(tmp_source != None and gameBoard.router.redirections[tmp_source.id] != None):
							tmp_target = tmp_source
							tmp_source = gameBoard.router.redirections[tmp_source.id]

							roadList.append(tmp_target)
							print("ASSISSTING ORDER : ",tmp_source.id," -> ",tmp_target.id)
							if(tmp_source.unitAtq > 0):
								self.orderStack.append((parse.createMoveOrder(tmp_source,tmp_target.id,tmp_source.unitAtq,playerId),10))

						for myNode in gameBoard.myPlayer.myNodes:
							if(myNode not in roadList and len(myNode.neighboors) == 1 and myNode.unitAtq > 0):
								self.orderStack.append((parse.createMoveOrder(myNode,myNode.neighboors[0].id,myNode.unitAtq,playerId),9))

					else:

						for myNode in gameBoard.myPlayer.myNodes:
							if(myNode.unitAtq >= 5):
								target = None
								numberOfEnnemy = 0

								for neighboor in myNode.neighboors:
									if(neighboor.owner != myNode.owner):
										numberOfEnnemy += 1
										if (target == None or (neighboor.unitAtq + neighboor.unitDef) < (target.unitAtq + target.unitDef) or (neighboor.prodSpeedAtq > target.prodSpeedAtq)):
											target = neighboor

								if(target != None and target.prodSpeedAtq > 1):
									targetNeighboorsType = target.neighboorsType(myNode.id)
									if(target.owner == -1 and targetNeighboorsType['ally'] >= targetNeighboorsType['ennemy']):
										if(targetNeighboorsType['ally'] > 1):
											for ally in target.neighboors:
												if(ally.owner == myNode.id and ally.unitAtq > 0):
													self.orderStack.append((parse.createMoveOrder(ally,target.id,ally.unitAtq,playerId),19))
										else:
											self.orderStack.append((parse.createMoveOrder(myNode,target.id,myNode.unitAtq,playerId),19))
									else:
										self.orderStack.append((parse.createMoveOrder(myNode,target.id,myNode.unitAtq,playerId),19))

								elif(len(myNode.neighboors) == 1):
									self.orderStack.append((parse.createMoveOrder(myNode,myNode.neighboors[0].id,myNode.unitAtq,playerId),9))
									#order(parse.createMoveOrder(myNode,myNode.neighboors[0].id,myNode.unitAtq,playerId))

								elif(numberOfEnnemy == 0):
									if(gameBoard.myPlayer.startingNode.id == 0 and myNode.id == 0):
										self.orderStack.append((parse.createMoveOrder(myNode,2,myNode.unitAtq,playerId),-1))
									elif(gameBoard.myPlayer.startingNode.id == 6 and myNode.id == 6):
										self.orderStack.append((parse.createMoveOrder(myNode,4,myNode.unitAtq,playerId),-1))
									else:
										for i in range(len(gameBoard.router.redirections)):
											if(gameBoard.router.redirections[i] == myNode):
												self.orderStack.append((parse.createMoveOrder(myNode,i,myNode.unitAtq,playerId),-1))
												break

								elif(len(myNode.neighboors) == 2 and (myNode.neighboorsType(myNode.id)['ally']) == 1):
									if(myNode.neighboors[0].owner == myNode.owner):
										self.orderStack.append((parse.createMoveOrder(myNode,myNode.neighboors[1].id,myNode.unitAtq,playerId),9))
										#order(parse.createMoveOrder(myNode,myNode.neighboors[1].id,myNode.unitAtq,playerId))
									else:
										self.orderStack.append((parse.createMoveOrder(myNode,myNode.neighboors[0].id,myNode.unitAtq,playerId),9))
										#order(parse.createMoveOrder(myNode,myNode.neighboors[0].id,myNode.unitAtq,playerId))

								elif(target != None and (myNode.unitAtq >= target.unitAtq + target.unitDef + 1)):
									self.orderStack.append((parse.createMoveOrder(myNode,target.id,target.unitAtq + target.unitDef + 1,playerId),9))
									#order(parse.createMoveOrder(myNode,target.id,target.unitAtq + target.unitDef + 1,playerId))

								elif(target != None and (target.unitAtq == target.maxAtq) and (myNode.unitAtq == target.unitAtq)):
									self.orderStack.append((parse.createMoveOrder(myNode,target.id,myNode.unitAtq,playerId),8))
									#order(parse.createMoveOrder(myNode,target.id,myNode.unitAtq,playerId))

									for neighboor in myNode.neighboors:
										if (neighboor.owner == myNode.owner and neighboor.unitAtq >= 5):
											self.orderStack.append((parse.createMoveOrder(neighboor,myNode.id,neighboor.unitAtq,playerId),7))
											#order(parse.createMoveOrder(neighboor,myNode.id,neighboor.unitAtq,playerId))
											break

					self.needSorting = True

		elif(data['type'] == 'GAMEOVER'):
			if(data['data'] == 1):
				print("we won !!! [" , playerId,"]")
		elif(data['type'] == 'ENDOFGAME'):
			print("end of process")
			self.isRunning = False

	def analyzeIArainbow(self):
		global gameBoard
		global globalState
		global window

		state2 = state_on_update()
		print(state2)
		data = parse.analyzeState(state2,gameBoard.matchUid)
		if(data['type'] == 'STATE'):
			globalState = data['data']

			gameBoard.clearFleets()
			gameBoard.updateCells(globalState['cellData'])
			gameBoard.updateMoves(globalState['moveData'])
			gameBoard.lastRefreshTimestamp = etime()

			# PUT THE STRATEGY HERE
			# HERE !!!!
			# Current State => globalState
			# (Voir dans parse.py -> analyseState() pour plus de détails)
			# Classes du jeu dans gameBoard
			# (Voir game.py -> Game() pour plus d'infos)


			if(gameBoard.cellNb == len(gameBoard.myPlayer.myNodes)):
				print("WE CAPTURED EVERY NODE !!! ~yay")
				self.isFinished = True
			elif(len(gameBoard.myPlayer.myNodes) == 0):
				print("WE LOST D=")
				self.isFinished = True
			else:
				print("==========[",len(gameBoard.myPlayer.myNodes),"/",gameBoard.cellNb,"]==========")
				if(len(self.orderStack) > 0):
					print("=====THROWING ORDERS !!! ",len(self.orderStack), " REMAINING")
					if(self.needSorting):
						self.orderStack = sorted(self.orderStack, key=lambda order: order[1])
						print(self.orderStack)
					order(self.orderStack.pop()[0])
					self.needSorting = False
				else:
					print("=====ANALYZING THE MAP")
					for node in gameBoard.myPlayer.importantNodes:
						print("TARGETS ::::::::::::::::: ",node.id)

					if(gameBoard.myPlayer.importantNodes != [] and gameBoard.myPlayer.importantNodes[0].owner != gameBoard.myPlayer.id):
						tmp_target = gameBoard.myPlayer.importantNodes[0]

						while(gameBoard.router.redirections[tmp_target.id] != None and gameBoard.router.redirections[tmp_target.id].owner != gameBoard.playerId):
							tmp_target = gameBoard.router.redirections[tmp_target.id]
						tmp_source = gameBoard.router.redirections[tmp_target.id] # Selectionne le noeud prédécesseur comme source du prochain noeud à capturer

						print("=========== NEXT CAPTURE IS ",tmp_target.id)

						if(tmp_source.unitAtq > tmp_target.unitAtq + tmp_target.unitDef):
							if(tmp_target == gameBoard.myPlayer.importantNodes[0]):
								ennemyNodes = []
								incomingEnnemyPower = tmp_target.possibleEnnemyIncome(gameBoard.myPlayer.id)
								incomingAllyPower = tmp_target.possibleAllyIncome(gameBoard.myPlayer.id)

								if((incomingAllyPower - tmp_target.unitDef - tmp_target.unitAtq) > incomingEnnemyPower):
									self.orderStack.append((parse.createMoveOrder(tmp_source,tmp_target.id,tmp_source.unitAtq,playerId),20)) # Order for capture
								elif(tmp_target.owner != -1 and tmp_source.unitAtq > tmp_target.unitAtq + tmp_target.unitDef):
									self.orderStack.append((parse.createMoveOrder(tmp_source,tmp_target.id,tmp_source.unitAtq,playerId),20)) # Order for capture
							else:
								self.orderStack.append((parse.createMoveOrder(tmp_source,tmp_target.id,tmp_source.unitAtq,playerId),20)) # Order for capture

						roadList = []
						# Orders for helpers in the chain
						while(gameBoard.router.redirections[tmp_source.id] != None):
							tmp_target = tmp_source
							tmp_source = gameBoard.router.redirections[tmp_source.id]

							roadList.append(tmp_target)
							print("ASSISSTING ORDER : ",tmp_source.id," -> ",tmp_target.id)
							if(tmp_source.unitAtq > 0):
								self.orderStack.append((parse.createMoveOrder(tmp_source,tmp_target.id,tmp_source.unitAtq,playerId),10))

						for myNode in gameBoard.myPlayer.myNodes:
							if(myNode not in roadList and len(myNode.neighboors) == 1 and myNode.unitAtq > 0):
								self.orderStack.append((parse.createMoveOrder(myNode,myNode.neighboors[0].id,myNode.unitAtq,playerId),9))

					else:
						
						nodeList = sorted(gameBoard.myPlayer.myNodes, key=lambda node: gameBoard.router.routes[node.id]['distance'])
						maxDist = gameBoard.router.routes[nodeList[len(nodeList)-1].id]['distance']

						nodeToExclude = []

						for node in nodeList:
							if(node not in nodeToExclude and node.unitAtq > 0):
								print("ANALYZE NODE ",node.id)
								if(node in gameBoard.myPlayer.frontNodes):
									print("FRONT NODE")
									neighboorsTypes = node.neighboorsType(gameBoard.myPlayer.id)
									nbNode = 0 # nb de noeuds à la profondeur inférieure aux noeuds de bord
									for i in range(maxDist):
										nbNode += len(gameBoard.router.nodeDisposition[i])

									if(gameBoard.router.routes[node.id]['distance'] == maxDist):
										print("FRONT MAX DIST")
										if(len(gameBoard.myPlayer.myNodes) > nbNode): # Frontal attack !!! si tout les noeuds de prof inférieure sont capturés
											print("FRONTAL ATTACK !!!")
											for neighboor in node.neighboors:
												if(gameBoard.router.redirections[neighboor.id] == node):

													tmp_target = neighboor
													capturable = -5 + tmp_target.possibleAllyIncome(gameBoard.myPlayer.id) - tmp_target.possibleEnnemyIncome(gameBoard.myPlayer.id)

													if(capturable > 0):
														self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq,playerId),20))
													else:
														helpers = []
														for helper in node.neighboors:
															if(helper.neighboorsType(gameBoard.myPlayer.id)['ally'] == len(helper.neighboors)):
																capturable += helper.unitAtq
																helpers.append(helper)

														if(capturable > 0):
															self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq,playerId),20))
															for helper in helpers:
																if(helper.unitAtq > 0):
																	self.orderStack.append((parse.createMoveOrder(helper,node.id,helper.unitAtq,playerId),19))

													break
									else:
										print("FRONT NEED HELP ")
										for neighboor in node.neighboors:
											tmp_target = neighboor
											if(gameBoard.router.redirections[neighboor.id] == node):
												print("FOLLOW ATTACK PATH")
												print("FROM ",node.id," TO ",tmp_target.id)
												if(neighboor.owner == gameBoard.myPlayer.id):
													pass
												else:
													allyAlreadyHelping = 0
													for edge in node.neighboorsEdgesOut:
														if(edge.target == tmp_target):
															allyAlreadyHelping = edge.trafficPower()
															break
													
													capturable = node.unitAtq + allyAlreadyHelping
													if(tmp_target.owner != -1):
														capturable -= 5 - tmp_target.possibleEnnemyIncome(gameBoard.myPlayer.id)
													else:
														capturable -= tmp_target.unitAtq + tmp_target.unitDef

													if(capturable > 0):
														print("CAN CAPTURE SOLO")
														self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq,playerId),20))
													else:
														neededToCapture = tmp_target.possibleAllyIncome(gameBoard.myPlayer.id) - tmp_target.possibleEnnemyIncome(gameBoard.myPlayer.id) - 5
														if(neededToCapture > 0):
															print("CAN CAPTURE IN GROUP")
															allies = tmp_target.neighboorsType(gameBoard.myPlayer.id)['ally']

															self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq,playerId),20))
															neededToCapture -= node.unitAtq

															for ally in tmp_target.neighboors:
																if(ally.owner == gameBoard.myPlayer.id and ally != node):
																	self.orderStack.append((parse.createMoveOrder(ally,tmp_target.id,int(neededToCapture/(allies-1))+1,playerId),19))
													break

								else:
									print("HELPING NODE")
									for neighboor in node.neighboors:
										if(gameBoard.router.redirectionsForHelpers[neighboor.id] == node):
											tmp_target = neighboor
											print("FROM ",node.id," TO ",tmp_target.id)

											allyAlreadyHelping = 0

											for edge in node.neighboorsEdgesOut:
												if(edge.source == neighboor):
													allyAlreadyHelping += edge.trafficPower()
													break

											place = tmp_target.maxAtq - tmp_target.unitAtq - 5 - allyAlreadyHelping
											if(place > 0):
												if(place > node.unitAtq):
													self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq,playerId),0))
												else:
													self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,place,playerId),0))
											break



					self.needSorting = True


		elif(data['type'] == 'GAMEOVER'):
			if(data['data'] == 1):
				print("we won !!! [" , playerId,"]")
		elif(data['type'] == 'ENDOFGAME'):
			print("end of process")
			self.isRunning = False

	def analyzeIAflutterbat(self):
		global gameBoard
		global globalState
		global window

		state2 = state_on_update()
		print(state2)
		data = parse.analyzeState(state2,gameBoard.matchUid)
		if(data['type'] == 'STATE'):
			globalState = data['data']

			gameBoard.clearFleets()
			gameBoard.updateCells(globalState['cellData'])
			gameBoard.updateMoves(globalState['moveData'])
			gameBoard.lastRefreshTimestamp = etime()

			# PUT THE STRATEGY HERE
			# HERE !!!!
			# Current State => globalState
			# (Voir dans parse.py -> analyseState() pour plus de détails)
			# Classes du jeu dans gameBoard
			# (Voir game.py -> Game() pour plus d'infos)

			if(gameBoard.cellNb == len(gameBoard.myPlayer.myNodes)):
				print("WE CAPTURED EVERY NODE !!! ~yay")
				self.isFinished = True
			elif(len(gameBoard.myPlayer.myNodes) == 0):
				print("WE LOST D=")
				self.isFinished = True
			else:
				print("==========[",len(gameBoard.myPlayer.myNodes),"/",gameBoard.cellNb,"]==========")
				if(len(self.orderStack) > 0):
					print("=====THROWING ORDERS !!! ",len(self.orderStack), " REMAINING")
					if(self.needSorting):
						self.orderStack = sorted(self.orderStack, key=lambda order: order[1])
						print(self.orderStack)
					order(self.orderStack.pop()[0])
					self.needSorting = False
				else:
					print("=====ANALYZING THE MAP")
						
					nodeList = sorted(gameBoard.myPlayer.myNodes, key=lambda node: gameBoard.router.routes[node.id]['distance'])
					maxDist = gameBoard.router.routes[nodeList[len(nodeList)-1].id]['distance']

					nodeToExclude = []

					for node in nodeList:
						keep = node.possibleEnnemyIncome(gameBoard.myPlayer.id) - node.unitDef + 1

						if(node not in nodeToExclude and node.unitAtq > 0):
							print("ANALYZE NODE ",node.id)
							if(node in gameBoard.myPlayer.frontNodes):
								print("FRONT NODE")
								neighboorsTypes = node.neighboorsType(gameBoard.myPlayer.id)
								nbNode = 0 # nb de noeuds à la profondeur inférieure aux noeuds de bord
								for i in range(maxDist):
									nbNode += len(gameBoard.router.nodeDisposition[i])

								if(gameBoard.router.routes[node.id]['distance'] == maxDist):
									print("FRONT MAX DIST")
									node.sortNeighboors()
										
									for neighboor in node.neighboors:
										if(neighboor.owner != gameBoard.myPlayer.id):
											print("POSSIBLE TARGET = ",neighboor.id)
											if((len(gameBoard.myPlayer.myNodes) > nbNode and node in gameBoard.router.redirections[neighboor.id]) or 
												gameBoard.router.routes[neighboor.id]['distance'] <= maxDist or
												len(neighboor.neighboors) == 1 or
												((neighboor.unitAtq + neighboor.unitDef + 5) < node.unitAtq and neighboor.owner == -1)):
												print("FRONTAL ATTACK !!!") # Frontal attack !!! si tout les noeuds de prof inférieure sont capturés
												print("TARGET = ",neighboor.id)
												print("NB neighboors = ",len(node.neighboors))

												tmp_target = neighboor
												capturable = tmp_target.possibleAllyIncome(gameBoard.myPlayer.id) - tmp_target.possibleEnnemyIncome(gameBoard.myPlayer.id)
												if(tmp_target.owner != -1):
													capturable -= 5

												print("CAPTURABLE ? ",capturable)

												if(capturable > 0):
													print("CAN CAPTURE SOLO")
													self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),20))
													break
												elif(node.unitAtq == node.maxAtq):
													print("CAPTURE BY FULL POP")
													self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),25))
													break
												else:
													helpers = []
													for helper in node.neighboors:
														if(helper.neighboorsType(gameBoard.myPlayer.id)['ally'] == len(helper.neighboors)):
															capturable += helper.unitAtq
															helpers.append(helper)

													if(capturable > 0):
														print("CAN CAPTURE IN GROUP")
														self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),20))
														for helper in helpers:
															helperKeep =  helper.possibleEnnemyIncome(gameBoard.myPlayer.id)
															if(helper.unitAtq - helperKeep > 0):
																self.orderStack.append((parse.createMoveOrder(helper,node.id,helper.unitAtq - helperKeep,playerId),19))
														break



												

								else:
									print("FRONT NEED HELP ")
									node.sortNeighboors()
									for neighboor in node.neighboors:
										if(neighboor.owner != gameBoard.myPlayer.id):
											print("POSSIBLE TARGET = ",neighboor.id)
											if(len(neighboor.neighboors) == 1 or
												(node in gameBoard.router.redirections[neighboor.id] and ((neighboor.owner == -1 and node.neighboorsType(gameBoard.myPlayer.id)['ennemy'] == 0) or neighboor.owner != -1)) or
												(neighboor in gameBoard.router.redirections[node.id] and ((neighboor.owner == -1 and node.neighboorsType(gameBoard.myPlayer.id)['ennemy'] == 0) or neighboor.owner != -1))):
												print("TARGET = ",neighboor.id)
												print("NB neighboors = ",len(node.neighboors))

												tmp_target = neighboor
												capturable = tmp_target.possibleAllyIncome(gameBoard.myPlayer.id) - node.possibleEnnemyIncome(gameBoard.myPlayer.id)
												if(tmp_target.owner != -1):
													capturable -= 3

												if(capturable > 0):
													print("CAN CAPTURE SOLO")
													self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),20))
													break
												elif(node.unitAtq == node.maxAtq):
													print("CAPTURE BY FULL POP")
													self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),25))
													break
												else:
													helpers = []
													for helper in node.neighboors:
														if(helper.neighboorsType(gameBoard.myPlayer.id)['ally'] == len(helper.neighboors)):
															capturable += helper.unitAtq
															helpers.append(helper)

													if(capturable > 0):
														print("CAN CAPTURE IN GROUP")
														self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),20))
														for helper in helpers:
															helperKeep =  helper.possibleEnnemyIncome(gameBoard.myPlayer.id)
															if(helper.unitAtq - helperKeep > 0):
																self.orderStack.append((parse.createMoveOrder(helper,node.id,helper.unitAtq - helperKeep,playerId),19))
														break

							else:
								print("HELPING NODE")
								if(len(node.neighboors) == 2):
									neighboorsTypes = node.neighboorsType(gameBoard.myPlayer.id)
									if(node.neighboors[0].owner == gameBoard.myPlayer.id and len(node.neighboors[0].neighboors) == 1):
										self.orderStack.append((parse.createMoveOrder(node,node.neighboors[1].id,node.unitAtq,playerId),0))
									elif(node.neighboors[1].owner == gameBoard.myPlayer.id and len(node.neighboors[1].neighboors) == 1):
										self.orderStack.append((parse.createMoveOrder(node,node.neighboors[0].id,node.unitAtq,playerId),0))
									else:
										for neighboor in node.neighboors:
											if(node in gameBoard.router.redirectionsForHelpers[neighboor.id] and node.unitAtq > 0):
												allyAlreadyHelping = 0

												for edge in node.neighboorsEdgesOut:
													if(edge.target == neighboor):
														allyAlreadyHelping += edge.trafficPower()
														break
												
												place = neighboor.maxAtq - neighboor.unitAtq - allyAlreadyHelping - 1

												if(place > 0):
													self.orderStack.append((parse.createMoveOrder(node,neighboor.id,place,playerId),0))

												node.unitAtq -= place

								else:
									for neighboor in node.neighboors:
										if(node in gameBoard.router.redirectionsForHelpers[neighboor.id] and node.unitAtq > 0):
											allyAlreadyHelping = 0

											for edge in node.neighboorsEdgesOut:
												if(edge.target == neighboor):
													allyAlreadyHelping += edge.trafficPower()
													break
											
											place = neighboor.maxAtq - neighboor.unitAtq - allyAlreadyHelping - 1

											if(place > 0):
												self.orderStack.append((parse.createMoveOrder(node,neighboor.id,place,playerId),0))

											node.unitAtq -= place


				if(len(self.orderStack) > 0):
					self.needSorting = True

		elif(data['type'] == 'GAMEOVER'):
			if(data['data'] == 1):
				print("we won !!! [" , playerId,"]")
		elif(data['type'] == 'ENDOFGAME'):
			print("end of process")
			self.isRunning = False

	def analyzeIAfriendship(self):
		global gameBoard
		global globalState
		global window

		state2 = state_on_update()
		print(state2)
		data = parse.analyzeState(state2,gameBoard.matchUid)
		if(data['type'] == 'STATE'):
			globalState = data['data']

			gameBoard.clearFleets()
			gameBoard.updateCells(globalState['cellData'])
			gameBoard.updateMoves(globalState['moveData'])
			gameBoard.lastRefreshTimestamp = etime()

			# PUT THE STRATEGY HERE
			# HERE !!!!
			# Current State => globalState
			# (Voir dans parse.py -> analyseState() pour plus de détails)
			# Classes du jeu dans gameBoard
			# (Voir game.py -> Game() pour plus d'infos)

			if(gameBoard.cellNb == len(gameBoard.myPlayer.myNodes)):
				print("WE CAPTURED EVERY NODE !!! ~yay")
				self.isFinished = True
			elif(len(gameBoard.myPlayer.myNodes) == 0):
				print("WE LOST D=")
				self.isFinished = True
			else:
				print("==========[",len(gameBoard.myPlayer.myNodes),"/",gameBoard.cellNb,"]==========")
				if(len(self.orderStack) > 0):
					print("=====THROWING ORDERS !!! ",len(self.orderStack), " REMAINING")
					if(self.needSorting):
						self.orderStack = sorted(self.orderStack, key=lambda order: order[1])
						print(self.orderStack)
					order(self.orderStack.pop()[0])
					self.needSorting = False
				else:
					print("=====ANALYZING THE MAP")
						
					nodeList = sorted(gameBoard.myPlayer.myNodes, key=lambda node: gameBoard.router.routes[node.id]['distance'])
					maxDist = gameBoard.router.routes[nodeList[len(nodeList)-1].id]['distance']

					nodeToExclude = []

					for node in nodeList:
						keep = 1 - node.unitDef
						for edge in node.neighboorsEdgesOut:
							if(edge.target.owner not in [-1,gameBoard.myPlayer.id]):
								keep += edge.target.unitAtq
								keep -= int(edge.length/1000)*((node.prodSpeedAtq-1)/2+1)
						if(keep < 0):
							keep = 0

						if(node not in nodeToExclude and node.unitAtq > 0):
							print("ANALYZE NODE ",node.id)
							if(node in gameBoard.myPlayer.frontNodes):
								print("FRONT NODE")
								neighboorsTypes = node.neighboorsType(gameBoard.myPlayer.id)
								nbNode = 0 # nb de noeuds à la profondeur inférieure aux noeuds de bord
								for i in range(maxDist):
									nbNode += len(gameBoard.router.nodeDisposition[i])

								if(gameBoard.router.routes[node.id]['distance'] == maxDist):
									print("FRONT MAX DIST")
									node.sortNeighboors()
										
									for neighboor in node.neighboors:
										if(neighboor.owner != gameBoard.myPlayer.id):
											print("POSSIBLE TARGET = ",neighboor.id)
											if((len(gameBoard.myPlayer.myNodes) > nbNode and node in gameBoard.router.redirections[neighboor.id]) or 
												gameBoard.router.routes[neighboor.id]['distance'] <= maxDist or
												len(neighboor.neighboors) == 1 or
												((neighboor.unitAtq + neighboor.unitDef + 5) < node.unitAtq and neighboor.owner == -1)):
												print("FRONTAL ATTACK !!!") # Frontal attack !!! si tout les noeuds de prof inférieure sont capturés
												print("TARGET = ",neighboor.id)
												print("NB neighboors = ",len(node.neighboors))

												tmp_target = neighboor

												edgeToTarget = None
												for edge in node.neighboorsEdgesOut:
													if(edge.target == tmp_target):
														edgeToTarget = edge
														break


												capturable = tmp_target.possibleAllyIncome(gameBoard.myPlayer.id) - tmp_target.possibleEnnemyIncome(gameBoard.myPlayer.id) - keep
												if(tmp_target.neighboorsType(gameBoard.myPlayer.id)['ennemy'] > 0):
													for edgeIn in neighboor.neighboorsEdgesIn:
														if(edgeIn.source.owner not in [gameBoard.myPlayer.id,-1] and edgeIn.source.unitAtq*((edgeIn.source.prodSpeedAtq-1)/2+1) > int(edgeIn.length)):
															capturable -= edgeIn.source.unitAtq - int(edgeIn.length/1000)
															print("ENNEMY SUPPORT BY ", edgeIn.source.unitAtq - int(edgeIn.length/1000))
													if(tmp_target.owner != -1 and tmp_target.unitDef < tmp_target.maxDef):
														capturable -= int(edgeToTarget.length/1000)

												print("CAPTURABLE ? ",capturable)

												if(capturable > 0):
													print("CAN CAPTURE SOLO")
													self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),20))
													break
												elif(node.unitAtq == node.maxAtq):
													print("CAPTURE BY FULL POP")
													self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),25))
													break
												else:
													helpers = []
													for helper in tmp_target.neighboors:
														if(helper.owner == gameBoard.myPlayer.id and helper.neighboorsType(gameBoard.myPlayer.id)['ally'] == len(helper.neighboors) and helper.unitAtq > 5):
															capturable += helper.unitAtq
															helpers.append(helper)

													if(capturable > 0):
														print("CAN CAPTURE IN GROUP")
														self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),20))
														for helper in helpers:
															helperKeep =  helper.possibleEnnemyIncome(gameBoard.myPlayer.id)
															if(helper.unitAtq - helperKeep > 0):
																self.orderStack.append((parse.createMoveOrder(helper,node.id,helper.unitAtq - helperKeep,playerId),19))
														break



												

								else:
									print("FRONT NEED HELP ")
									node.sortNeighboors()
									for neighboor in node.neighboors:
										if(neighboor.owner != gameBoard.myPlayer.id):
											print("POSSIBLE TARGET = ",neighboor.id)
											if(len(neighboor.neighboors) == 1 or
												(node in gameBoard.router.redirections[neighboor.id] and ((neighboor.owner == -1 and node.neighboorsType(gameBoard.myPlayer.id)['ennemy'] == 0) or neighboor.owner != -1)) or
												(neighboor in gameBoard.router.redirections[node.id] and ((neighboor.owner == -1 and node.neighboorsType(gameBoard.myPlayer.id)['ennemy'] == 0) or neighboor.owner != -1))):
												print("TARGET = ",neighboor.id)
												print("NB neighboors = ",len(node.neighboors))

												tmp_target = neighboor

												edgeToTarget = None
												for edge in node.neighboorsEdgesOut:
													if(edge.target == tmp_target):
														edgeToTarget = edge
														break

												capturable = tmp_target.possibleAllyIncome(gameBoard.myPlayer.id) - node.possibleEnnemyIncome(gameBoard.myPlayer.id) - keep
												if(tmp_target.neighboorsType(gameBoard.myPlayer.id)['ennemy'] > 0):
													for edgeIn in neighboor.neighboorsEdgesIn:
														if(edgeIn.source.owner not in [gameBoard.myPlayer.id,-1] and edgeIn.source.unitAtq*((edgeIn.source.prodSpeedAtq-1)/2+1) > int(edgeIn.length)):
															capturable -= edgeIn.source.unitAtq 
															capturable += int(edgeIn.length/1000)*((tmp_target.prodSpeedAtq-1)/2+1)
															print("ENNEMY SUPPORT BY ", edgeIn.source.unitAtq - int(edgeIn.length/1000))
													if(tmp_target.owner != -1 and tmp_target.unitDef < tmp_target.maxDef):
														capturable -= int(edgeToTarget.length/1000)

												print("CAPTURABLE ? ",capturable)

												if(capturable > 0):
													print("CAN CAPTURE SOLO")
													self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),20))
													break
												elif(node.unitAtq == node.maxAtq):
													print("CAPTURE BY FULL POP")
													self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),25))
													break
												else:
													helpers = []
													for helper in node.neighboors:
														if(helper.owner == gameBoard.myPlayer.id and helper.neighboorsType(gameBoard.myPlayer.id)['ally'] == len(helper.neighboors) and helper.unitAtq > 5):
															capturable += helper.unitAtq
															helpers.append(helper)

													if(capturable > 0):
														print("CAN CAPTURE IN GROUP")
														self.orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),20))
														for helper in helpers:
															helperKeep =  helper.possibleEnnemyIncome(gameBoard.myPlayer.id)
															if(helper.unitAtq - helperKeep > 0):
																self.orderStack.append((parse.createMoveOrder(helper,node.id,helper.unitAtq - helperKeep,playerId),19))
														break

							else:
								print("HELPING NODE")
								if(len(node.neighboors) == 2):
									neighboorsTypes = node.neighboorsType(gameBoard.myPlayer.id)
									if(node.neighboors[0].owner == gameBoard.myPlayer.id and len(node.neighboors[0].neighboors) == 1):
										self.orderStack.append((parse.createMoveOrder(node,node.neighboors[1].id,node.unitAtq,playerId),0))
									elif(node.neighboors[1].owner == gameBoard.myPlayer.id and len(node.neighboors[1].neighboors) == 1):
										self.orderStack.append((parse.createMoveOrder(node,node.neighboors[0].id,node.unitAtq,playerId),0))
									else:
										for neighboor in node.neighboors:

											edgeToTarget = None
											for edge in node.neighboorsEdgesOut:
												if(edge.target == neighboor):
													edgeToTarget = edge
													break

											if(node in gameBoard.router.redirectionsForHelpers[neighboor.id] and node.unitAtq > 0):
												allyAlreadyHelping = 0

												for edge in node.neighboorsEdgesOut:
													if(edge.target == neighboor):
														allyAlreadyHelping += edge.trafficPower()
														break
												
												place = neighboor.maxAtq - neighboor.unitAtq - allyAlreadyHelping - int(edgeToTarget.length/1000)

												if(place > 0):
													self.orderStack.append((parse.createMoveOrder(node,neighboor.id,place,playerId),0))

												node.unitAtq -= place

								else:
									for neighboor in node.neighboors:

										edgeToTarget = None
										for edge in node.neighboorsEdgesOut:
											if(edge.target == neighboor):
												edgeToTarget = edge
												break

										if(node in gameBoard.router.redirectionsForHelpers[neighboor.id] and node.unitAtq > 0):
											allyAlreadyHelping = 0

											for edge in node.neighboorsEdgesOut:
												if(edge.target == neighboor):
													allyAlreadyHelping += edge.trafficPower()
													break
											
											place = neighboor.maxAtq - neighboor.unitAtq - allyAlreadyHelping - int(edgeToTarget.length/1000)

											if(place > 0):
												self.orderStack.append((parse.createMoveOrder(node,neighboor.id,place,playerId),0))

											node.unitAtq -= place


				if(len(self.orderStack) > 0):
					self.needSorting = True

		elif(data['type'] == 'GAMEOVER'):
			if(data['data'] == 1):
				print("we won !!! [" , playerId,"]")
		elif(data['type'] == 'ENDOFGAME'):
			print("end of process")
			self.isRunning = False