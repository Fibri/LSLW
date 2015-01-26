# -*- coding: utf-8 -*-

import re
import parse
import gameO as game

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

	print("INIT STATE : ",init_string)
	
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
	# (2) TODO: traitement de init_state
	print("Bot started !!!")

	isRunning = True
	isFinished = False

	orderStack = []

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
				gameBoard.lastRefreshTimestamp = etime()

				# PUT THE STRATEGY HERE
				# HERE !!!!
				# Current State => globalState
				# (Voir dans parse.py -> analyseState() pour plus de détails)
				# Classes du jeu dans gameBoard
				# (Voir game.py -> Game() pour plus d'infos)

				if(gameBoard.cellNb == len(gameBoard.myPlayer.myNodes)):
					print("WE CAPTURED EVERY NODE !!! ~yay")
					isFinished = True
				elif(len(gameBoard.myPlayer.myNodes) == 0):
					print("WE LOST D=")
					isFinished = True
				else:
					print("==========[",len(gameBoard.myPlayer.myNodes),"/",gameBoard.cellNb,"]==========")
					if(len(orderStack) > 0):
						print("=====THROWING ORDERS !!! ",len(orderStack), " REMAINING")
						if(needSorting):
							orderStack = sorted(orderStack, key=lambda order: order[1])
							print(orderStack)
						order(orderStack.pop()[0])
						needSorting = False
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
														orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),20))
														break
													elif(node.unitAtq == node.maxAtq):
														print("CAPTURE BY FULL POP")
														orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),25))
														break
													else:
														helpers = []
														for helper in tmp_target.neighboors:
															if(helper.owner == gameBoard.myPlayer.id and helper.neighboorsType(gameBoard.myPlayer.id)['ally'] == len(helper.neighboors) and helper.unitAtq > 5):
																capturable += helper.unitAtq
																helpers.append(helper)

														if(capturable > 0):
															print("CAN CAPTURE IN GROUP")
															orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),20))
															for helper in helpers:
																helperKeep =  helper.possibleEnnemyIncome(gameBoard.myPlayer.id)
																if(helper.unitAtq - helperKeep > 0):
																	orderStack.append((parse.createMoveOrder(helper,node.id,helper.unitAtq - helperKeep,playerId),19))
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
														orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),20))
														break
													elif(node.unitAtq == node.maxAtq):
														print("CAPTURE BY FULL POP")
														orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),25))
														break
													else:
														helpers = []
														for helper in node.neighboors:
															if(helper.owner == gameBoard.myPlayer.id and helper.neighboorsType(gameBoard.myPlayer.id)['ally'] == len(helper.neighboors) and helper.unitAtq > 5):
																capturable += helper.unitAtq
																helpers.append(helper)

														if(capturable > 0):
															print("CAN CAPTURE IN GROUP")
															orderStack.append((parse.createMoveOrder(node,tmp_target.id,node.unitAtq - keep,playerId),20))
															for helper in helpers:
																helperKeep =  helper.possibleEnnemyIncome(gameBoard.myPlayer.id)
																if(helper.unitAtq - helperKeep > 0):
																	orderStack.append((parse.createMoveOrder(helper,node.id,helper.unitAtq - helperKeep,playerId),19))
															break

								else:
									print("HELPING NODE")
									if(len(node.neighboors) == 2):
										neighboorsTypes = node.neighboorsType(gameBoard.myPlayer.id)
										if(node.neighboors[0].owner == gameBoard.myPlayer.id and len(node.neighboors[0].neighboors) == 1):
											orderStack.append((parse.createMoveOrder(node,node.neighboors[1].id,node.unitAtq,playerId),0))
										elif(node.neighboors[1].owner == gameBoard.myPlayer.id and len(node.neighboors[1].neighboors) == 1):
											orderStack.append((parse.createMoveOrder(node,node.neighboors[0].id,node.unitAtq,playerId),0))
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
														orderStack.append((parse.createMoveOrder(node,neighboor.id,place,playerId),0))

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
													orderStack.append((parse.createMoveOrder(node,neighboor.id,place,playerId),0))

												node.unitAtq -= place


					if(len(orderStack) > 0):
						needSorting = True

			elif(data['type'] == 'GAMEOVER'):
				if(data['data'] == 1):
					print("we won !!! [" , playerId,"]")
			elif(data['type'] == 'ENDOFGAME'):
				print("end of process")
				isRunning = False
		except KeyboardInterrupt:
			isRunning = False
			print("STOPPING THE CLIENT BECAUSE OF CTRL + C")
