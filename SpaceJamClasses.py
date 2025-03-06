from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.task import Task
from direct.task.Task import TaskManager
from typing import Callable
from panda3d.core import Loader, NodePath, Vec3

from CollideObjectBase import InverseSphereCollideObject, CapsuleCollidableObject, SphereCollidableObject, SphereCollidableObjectVec3 # type: ignore

class Player(SphereCollidableObjectVec3):
    def __init__(self, loader: Loader, taskMgr: TaskManager, accept: Callable[[str, Callable], None], modelPath: str, parentNode: NodePath, nodeName: str, posVec: Vec3, scaleVec: float, Hpr: Vec3, render):
        super(Player, self).__init__(loader, modelPath, parentNode, nodeName, posVec, 10) ##Uses __init__ function from SphereCollideObject
        self.taskMgr = taskMgr
        self.accept = accept
        self.loader = loader
        self.render = render
        self.modelNode = loader.loadModel(modelPath)
        self.modelNode.reparentTo(parentNode)

        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.modelNode.setName(nodeName)
        self.modelNode.setHpr(Hpr)

        self.reloadTime = 0.25
        self.missileDistance = 4000       # Time until missile explodes
        self.missileBay = 1               # Only one missile at a time can be launched (originally)

        self.setKeyBindings()

        self.taskMgr.add(self.checkIntervals, 'checkMissiles', 34)
    
    def checkIntervals(self, task): #Object Polling in the dictionaries
        for i in Missile.Intervals:
            if not Missile.Intervals[i].isPlaying(): # isPlaying returns true or false to see if the missile has gotten to the end of its path
                Missile.cNodes[i].detachNode()
                Missile.fireModels[i].detachNode()
                del Missile.Intervals[i]
                del Missile.fireModels[i]
                del Missile.cNodes[i]
                del Missile.collisionSolids[i]
                print(i + " has reached the end of its fire solution")
                break # We break because when things are deleted from a dictionary, we have to refactor the dictionary so we can reuse it. 
                      # This is because when we delete things, there's a gap at that point
        return Task.cont

    def thrust(self, keyDown):
        if (keyDown):
            self.taskMgr.add(self.applyThrust, 'forward-thrust') # might be taskManager instead, taskMgr is whats on the website
        else:
            self.taskMgr.remove('forward-thrust')

    def applyThrust(self, task):
        rate = 5
        trajectory = self.render.getRelativeVector(self.modelNode, Vec3.forward())
        trajectory.normalize()
        self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)
        self.printPosHpr()
        return task.cont                                    # Continue moving the players ship when returning
    
    def setKeyBindings(self): ##Movement for the player, review Warmup3
        self.accept('space', self.thrust, [1])
        self.accept('space-up', self.thrust, [0])

        self.accept('q', self.leftRoll, [1])
        self.accept('q-up', self.leftRoll, [0])

        self.accept('e', self.rightRoll, [1])
        self.accept('e-up', self.rightRoll, [0])

        self.accept('a', self.LeftTurn, [1])
        self.accept('a-up', self.LeftTurn, [0])

        self.accept('d', self.rightTurn, [1])
        self.accept('d-up', self.rightTurn, [0])

        self.accept('w', self.Up, [1])
        self.accept('w-up', self.Up, [0])

        self.accept('s', self.Down, [1])
        self.accept('s-up', self.Down, [0])

        self.accept('f', self.fire)

    def leftRoll(self, keyDown):
        if (keyDown):
            self.taskMgr.add(self.applyLeftRoll, 'left-roll')
        else:
            self.taskMgr.remove('left-roll')

    def rightRoll(self, keyDown):
        if (keyDown):
            self.taskMgr.add(self.applyRightRoll, 'right-roll')
        else:
            self.taskMgr.remove('right-roll')


    def applyLeftRoll(self, task):
        rate = 1
        #print('leftroll')
        self.printPosHpr()
        self.modelNode.setR(self.modelNode.getR() - rate)
        return task.cont
        
    def applyRightRoll(self, task):
        rate = 1
        #print('rightroll')
        self.printPosHpr()
        self.modelNode.setR(self.modelNode.getR() + rate)
        return task.cont
    
#------------------------------------------------------------------------------------

    def LeftTurn(self, keyDown):
        if (keyDown):
            self.taskMgr.add(self.applyLeftTurn, 'left-turn')
        else:
            self.taskMgr.remove('left-turn')

    def rightTurn(self, keyDown):
        if (keyDown):
            self.taskMgr.add(self.applyRightTurn, 'right-turn')
        else:
            self.taskMgr.remove('right-turn')


    def applyLeftTurn(self, task):
        rate = 1
        #print('leftturn')
        self.printPosHpr()
        self.modelNode.setH(self.modelNode.getH() + rate)
        return task.cont

    def applyRightTurn(self, task):
        rate = 1
        #print('rightturn')
        self.printPosHpr()
        self.modelNode.setH(self.modelNode.getH() - rate)
        return task.cont
    
#------------------------------------------------------------------------------------

    def Up(self, keyDown):
        
        if (keyDown):
            self.taskMgr.add(self.applyUp, 'up')
        else:
            self.taskMgr.remove('up')

    def Down(self, keyDown):
        if (keyDown):
            self.taskMgr.add(self.applyDown, 'down')
        else:
            self.taskMgr.remove('down')


    def applyUp(self, task):
        rate = 1
        #print('applyUp')
        self.printPosHpr()
        self.modelNode.setP(self.modelNode.getP() + rate)
        return task.cont

    def applyDown(self, task):
        rate = 1
        #print('applyDown')
        self.printPosHpr()
        self.modelNode.setP(self.modelNode.getP() - rate)
        return task.cont

    def printPosHpr(self):
        print("renderPos: " + str(self.render.getPos()))
        print("renderHPR: " + str(self.render.getHpr()))
        print("modelPOS:  " + str(self.modelNode.getPos()))
        print("modelHPR:  " + str(self.modelNode.getHpr()))

    def fire(self):
        if self.missileBay:
            travRate = self.missileDistance
            aim = self.render.getRelativeVector(self.modelNode, Vec3.forward())  # The dirction the spaceship is facing (changed from self.render)
            aim.normalize()                                                         # Normalizing a vector makes it consistant all the time
            fireSolution = aim * travRate
            inFront = aim * 150                                                     # Stores where the missile starts its path in comparison to the spaceship
            travVec = fireSolution + self.modelNode.getPos()
            self.missileBay -= 1
            tag = 'Missile' + str(Missile.missileCount)                                # Creates a tag for each missile that details the number of the missile
            posVec = self.modelNode.getPos() + inFront

            #Create our missile
            currentmissile = Missile(self.loader, 'Assets/Phaser/phaser.egg', self.modelNode, tag, posVec, 4.0) #(modelNode changed from self.render)
            Missile.Intervals[tag] = currentmissile.modelNode.posInterval(2.0, travVec, startPos = posVec, fluid = 1)
            Missile.Intervals[tag].start()
            
        else: #Start reloading
            if not self.taskMgr.hasTaskNamed('reload'):
                print('Reloading')
                self.taskMgr.doMethodLater(0, self.reload, 'reload')
                return Task.cont
            
    def reload(self, task):
        if task.time > self.reloadTime:
            self.missileBay += 1
            print("reload complete")
            return Task.done
        elif task.time <= self.reloadTime:
            print("Still reloading!")
            return Task.cont
        if self.missileBay > 1: # if the missiles ever glitch out
            self.missileBay = 1
            return Task.done


class Universe(InverseSphereCollideObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Universe, self).__init__(loader, modelPath, parentNode, nodeName, posVec, 9600) ##Uses __init__ function from InverseSphereCollideObject
        self.modelNode = loader.loadModel(modelPath)
        self.modelNode.reparentTo(parentNode)

        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.modelNode.setName(nodeName)

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)

class SpaceStation(CapsuleCollidableObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(SpaceStation, self).__init__(loader, modelPath, parentNode, nodeName, 1, -1, 5, 1, -1, -5, 7)     ##Defines ax, ay, az, etc. for capsule
        self.modelNode = loader.loadModel(modelPath)
        self.modelNode.reparentTo(parentNode)

        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.modelNode.setName(nodeName)

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        print("spacestation " + nodeName + " created")

class Planet(SphereCollidableObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, x: float, y: float, z: float, scaleVec: float):
        super(Planet, self).__init__(loader, modelPath, parentNode, nodeName, x, y, z, scaleVec)
        self.modelNode = loader.loadModel(modelPath)
        self.modelNode.reparentTo(parentNode)

        self.modelNode.setX(x)
        self.modelNode.setY(y)
        self.modelNode.setZ(z)
        self.modelNode.setScale(scaleVec)

        self.modelNode.setName(nodeName)

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)

class Drone(SphereCollidableObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float): # type: ignore
        super(Drone, self).__init__(loader, modelPath, parentNode, nodeName, posVec.getX(), posVec.getY(), posVec.getZ(), scaleVec)
        self.modelNode = loader.loadModel(modelPath)
        self.modelNode.reparentTo(parentNode)

        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.modelNode.setName(nodeName)

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
    droneCount = 0

class Missile(SphereCollidableObject):
    fireModels = {}             # Dictionaries
    cNodes = {}
    collisionSolids = {}
    Intervals = {}
    missileCount = 0

    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, posVec: Vec3, scaleVec: float = 1.0): # type: ignore
        super(Missile, self).__init__(loader, modelPath, parentNode, nodeName, posVec.getX(), posVec.getY(), posVec.getZ(), 3.0)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setPos(posVec)
        Missile.missileCount += 1
        
        Missile.fireModels[nodeName] = self.modelNode
        Missile.cNodes[nodeName] = self.collisionNode
        Missile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
        Missile.cNodes[nodeName].show()
        print("Fire Missile #" + str(Missile.missileCount))
        
