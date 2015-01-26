import tkinter as tk
import math

class HUD:
	def __init__(self,gameBoard,analyzer):
		self.myGame = gameBoard
		self.myAnalyzer = analyzer
		self.window = tk.Tk()
		self.canvas = tk.Canvas(self.window, width=800, height=800, borderwidth=0, highlightthickness=0, bg="black")
		self.nodes = []
		self.fleets = []
		self.nodeRedirections = [x for x in range(gameBoard.cellNb)]
		self.edgeRedirections = [x for x in range(gameBoard.lineNb*2)]
		self.canvas.pack()
		self.repartitionMultiplier = 30
		self.nodeRadius = 30
		self.startX = self.nodeRadius + 10
		self.startY = self.nodeRadius + 10
		self.activateFleets = False

	def initMap(self):

		print("CREATING ", self.myGame.lineNb, " EDGES !")
		for sourceId in self.myGame.edges:
			for edge in sourceId:
				sourceNode = edge.source
				targetNode = edge.target
				id = self.canvas.create_line(self.startX+sourceNode.x*self.repartitionMultiplier, self.startY+sourceNode.y*self.repartitionMultiplier, self.startX+targetNode.x*self.repartitionMultiplier, self.startY+targetNode.y*self.repartitionMultiplier, fill="blue")
				if(sourceNode.id < targetNode.id):
					if(sourceNode.owner == self.myGame.myPlayer.id or targetNode.owner == self.myGame.myPlayer.id):
						id2 = self.canvas.create_text(self.startX+(sourceNode.x + targetNode.x)/2 *self.repartitionMultiplier,self.startY+(sourceNode.y + targetNode.y)/2 *self.repartitionMultiplier-5, fill="cyan", text=(str(edge.trafficPower())))
					elif(sourceNode == -1 and targetNode == -1):
						id2 = self.canvas.create_text(self.startX+(sourceNode.x + targetNode.x)/2 *self.repartitionMultiplier,self.startY+(sourceNode.y + targetNode.y)/2 *self.repartitionMultiplier-5, fill="grey", text=(str(edge.trafficPower())))
					else:
						id2 = self.canvas.create_text(self.startX+(sourceNode.x + targetNode.x)/2 *self.repartitionMultiplier,self.startY+(sourceNode.y + targetNode.y)/2 *self.repartitionMultiplier-5, fill="magenta", text=(str(edge.trafficPower())))
				else:
					if(sourceNode.owner == self.myGame.myPlayer.id or targetNode.owner == self.myGame.myPlayer.id):
						id2 = self.canvas.create_text(self.startX+(sourceNode.x + targetNode.x)/2 *self.repartitionMultiplier,self.startY+(sourceNode.y + targetNode.y)/2 *self.repartitionMultiplier+5, fill="cyan", text=(str(edge.trafficPower())))
					elif(sourceNode == -1 and targetNode == -1):
						id2 = self.canvas.create_text(self.startX+(sourceNode.x + targetNode.x)/2 *self.repartitionMultiplier,self.startY+(sourceNode.y + targetNode.y)/2 *self.repartitionMultiplier+5, fill="grey", text=(str(edge.trafficPower())))
					else:
						id2 = self.canvas.create_text(self.startX+(sourceNode.x + targetNode.x)/2 *self.repartitionMultiplier,self.startY+(sourceNode.y + targetNode.y)/2 *self.repartitionMultiplier+5, fill="magenta", text=(str(edge.trafficPower())))
				self.edgeRedirections[edge.id] = (id,id2)

		print("CREATING ", self.myGame.cellNb, " NODES !")
		for node in self.myGame.nodes:
			print("NODE (",node.x," : ",node.y,")")
			id = self.create_circle(self.startX+node.x*self.repartitionMultiplier,self.startY+node.y*self.repartitionMultiplier, "grey", "#DDD", 2)
			id2 = self.canvas.create_text(self.startX+node.x*self.repartitionMultiplier,self.startY+5+node.y*self.repartitionMultiplier, fill="white", text=(str(node.unitAtq)+" : "+str(node.unitDef)))
			self.canvas.create_text(self.startX+node.x*self.repartitionMultiplier,self.startY-5+node.y*self.repartitionMultiplier, fill="white", text=("["+str(node.id)+" | "+str(node.prodSpeedAtq)+"]"))
			self.nodeRedirections[node.id] = (id,id2)

		self.window.after(1000,self.task)
		self.window.mainloop()

	def create_circle(self, x, y, color2="grey", outline2="#DDD", width2=5, r=30):
		return self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=color2, outline=outline2, width=width2)

	def task(self):
		self.myAnalyzer.analyzeIAlittle()
		if(self.activateFleets):
			self.clearFleets()
		self.draw()
		
		if(self.myAnalyzer.isRunning):
			self.window.after(100,self.task)

	def clearFleets(self):
		for fleet in self.fleets:
			self.canvas.delete(fleet[0])
			self.canvas.delete(fleet[1])

	def draw(self):
		for node in self.myGame.nodes:
			id = self.nodeRedirections[node.id][0]
			id2 = self.nodeRedirections[node.id][1]
			if(node.owner == self.myGame.myPlayer.id):
				self.canvas.itemconfigure(id, fill="blue")
				self.canvas.itemconfigure(id2, text=(str(node.unitAtq)+" : "+str(node.unitDef)))
			elif(node.owner == -1):
				self.canvas.itemconfigure(id, fill="grey")
				self.canvas.itemconfigure(id2, text=(str(node.unitAtq)+" : "+str(node.unitDef)))
			else:
				self.canvas.itemconfigure(id, fill="red")
				self.canvas.itemconfigure(id2, text=(str(node.unitAtq)+" : "+str(node.unitDef)))

		for sourceId in self.myGame.edges:
			for edge in sourceId:
				id = self.edgeRedirections[edge.id][0]
				id2 = self.edgeRedirections[edge.id][1]

				if(edge.source.owner == self.myGame.myPlayer.id or edge.target.owner == self.myGame.myPlayer.id):
					self.canvas.itemconfigure(id, fill="blue")
					self.canvas.itemconfigure(id2, fill="cyan", text=(str(edge.trafficPower())))
				elif(edge.source.owner == -1 and edge.target.owner == -1):
					self.canvas.itemconfigure(id, fill="grey")
					self.canvas.itemconfigure(id2, fill="grey", text='0')
				else:
					self.canvas.itemconfigure(id, fill="red")
					self.canvas.itemconfigure(id2, fill="magenta", text=(str(edge.trafficPower())))

				if(self.activateFleets):
					for fleet in edge.fleets:
						if(fleet.progress < 0):
							print("ERROR NEGATIVE PROGRESS")

						if(edge.source.x == edge.target.x):
							posX = edge.source.x
						else:
							posX = edge.source.x + (edge.target.x - edge.source.x)*fleet.progress

						if(edge.source.y == edge.target.y):
							posY = edge.source.y
						else:
							posY = edge.source.y + (edge.target.y - edge.source.y)*fleet.progress
							posY = edge.source.y + (edge.target.y - edge.source.y)*fleet.progress

						posX *= self.repartitionMultiplier
						posY *= self.repartitionMultiplier
						posX += self.startX
						posY += self.startY

						if(fleet.owner == self.myGame.myPlayer.id):
							idf = self.create_circle(posX, posY, "blue", "#DDD", 1, 10)
							idf2 = self.canvas.create_text(posX, posY, fill="cyan", text=(str(fleet.size)))
						else:
							idf = self.create_circle(posX, posY, "red", "#DDD", 1, 10)
							idf2 = self.canvas.create_text(posX, posY, fill="magenta", text=(str(fleet.size)))

						self.fleets.append((idf,idf2))