# -*- coding: utf-8 -*-

import re
import parse
import game

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

	importantTarget = gameBoard.nodes[3]

	orderStack = []

	while isRunning :

		try:
			state2 = state_on_update()
			print(state2)
			data = parse.analyzeState(state2,gameBoard.matchUid)
			if(state2 == None):
				pass
			elif(data['type'] == 'STATE' and not isFinished):
				global globalState
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

						if(importantTarget.owner != gameBoard.playerId):
							tmp_target = importantTarget

							while(gameBoard.router.redirections[tmp_target.id] != None and gameBoard.router.redirections[tmp_target.id].owner != gameBoard.playerId):
								tmp_target = gameBoard.router.redirections[tmp_target.id]
							tmp_source = gameBoard.router.redirections[tmp_target.id] # Selectionne le noeud prédécesseur comme source du prochain noeud à capturer

							print("=========== NEXT CAPTURE IS ",tmp_target.id)

							if(tmp_source.unitAtq > tmp_target.unitAtq + tmp_target.unitDef):
								orderStack.append((parse.createMoveOrder(tmp_source,tmp_target.id,tmp_source.unitAtq,playerId),20)) # Order for capture

							roadList = []
							# Orders for helpers in the chain
							while(gameBoard.router.redirections[tmp_source.id] != None):
								tmp_target = tmp_source
								tmp_source = gameBoard.router.redirections[tmp_source.id]

								roadList.append(tmp_target)
								print("ASSISSTING ORDER : ",tmp_source.id," -> ",tmp_target.id)
								if(tmp_source.unitAtq > 0):
									orderStack.append((parse.createMoveOrder(tmp_source,tmp_target.id,tmp_source.unitAtq,playerId),10))

							for myNode in gameBoard.myPlayer.myNodes:
								if(myNode not in roadList and len(myNode.neighboors) == 1 and myNode.unitAtq > 0):
									orderStack.append((parse.createMoveOrder(myNode,myNode.neighboors[0].id,myNode.unitAtq,playerId),9))

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
													if(ally.owner == myNode.id):
														orderStack.append((parse.createMoveOrder(ally,target.id,ally.unitAtq,playerId),19))
											else:
												orderStack.append((parse.createMoveOrder(myNode,target.id,myNode.unitAtq,playerId),19))
										else:
											orderStack.append((parse.createMoveOrder(myNode,target.id,myNode.unitAtq,playerId),19))

									elif(len(myNode.neighboors) == 1):
										orderStack.append((parse.createMoveOrder(myNode,myNode.neighboors[0].id,myNode.unitAtq,playerId),9))
										#order(parse.createMoveOrder(myNode,myNode.neighboors[0].id,myNode.unitAtq,playerId))

									elif(numberOfEnnemy == 0):
										if(gameBoard.myPlayer.startingNode.id == 0 and myNode.id == 0):
											orderStack.append((parse.createMoveOrder(myNode,2,myNode.unitAtq,playerId),-1))
										elif(gameBoard.myPlayer.startingNode.id == 6 and myNode.id == 6):
											orderStack.append((parse.createMoveOrder(myNode,4,myNode.unitAtq,playerId),-1))
										else:
											for i in range(len(gameBoard.router.redirections)):
												if(gameBoard.router.redirections[i] == myNode):
													orderStack.append((parse.createMoveOrder(myNode,i,myNode.unitAtq,playerId),-1))
													break

									elif(len(myNode.neighboors) == 2 and (myNode.neighboorsType(myNode.id)['ally']) == 1):
										if(myNode.neighboors[0].owner == myNode.owner):
											orderStack.append((parse.createMoveOrder(myNode,myNode.neighboors[1].id,myNode.unitAtq,playerId),9))
											#order(parse.createMoveOrder(myNode,myNode.neighboors[1].id,myNode.unitAtq,playerId))
										else:
											orderStack.append((parse.createMoveOrder(myNode,myNode.neighboors[0].id,myNode.unitAtq,playerId),9))
											#order(parse.createMoveOrder(myNode,myNode.neighboors[0].id,myNode.unitAtq,playerId))

									elif(target != None and (myNode.unitAtq >= target.unitAtq + target.unitDef + 1)):
										orderStack.append((parse.createMoveOrder(myNode,target.id,target.unitAtq + target.unitDef + 1,playerId),9))
										#order(parse.createMoveOrder(myNode,target.id,target.unitAtq + target.unitDef + 1,playerId))

									elif(target != None and (target.unitAtq == target.maxAtq) and (myNode.unitAtq == target.unitAtq)):
										orderStack.append((parse.createMoveOrder(myNode,target.id,myNode.unitAtq,playerId),8))
										#order(parse.createMoveOrder(myNode,target.id,myNode.unitAtq,playerId))

										for neighboor in myNode.neighboors:
											if (neighboor.owner == myNode.owner and neighboor.unitAtq >= 5):
												orderStack.append((parse.createMoveOrder(neighboor,myNode.id,neighboor.unitAtq,playerId),7))
												#order(parse.createMoveOrder(neighboor,myNode.id,neighboor.unitAtq,playerId))
												break
















						needSorting = True

			elif(data['type'] == 'GAMEOVER'):
				if(data['data'] == gameBoard.playerId):
					print("we won !!!")
			elif(data['type'] == 'ENDOFGAME'):
				print("end of process")
				isRunning = False
		except KeyboardInterrupt:
			isRunning = False
			print("STOPPING THE CLIENT BECAUSE OF CTRL + C")
