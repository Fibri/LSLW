# -*- coding: utf-8 -*-

import re
import parse
import game
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
	# (2) TODO: traitement de init_state
	print("Bot started !!!")
	isRunning = True
	while isRunning :

		try:

			state2 = state_on_update()
			print(state2)
			data = parse.analyzeState(state2,gameBoard.matchUid)
			if(data['type'] == 'STATE'):
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

				# IA RANDOM
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
