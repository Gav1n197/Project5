from panda3d.core import PandaNode, Loader, NodePath, CollisionNode, CollisionSphere, CollisionInvSphere, CollisionCapsule, Vec3

class PlacedObject(PandaNode):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str):
        self.modelNode: NodePath = loader.loadModel(modelPath)

        if not isinstance(self.modelNode, NodePath):
            raise AssertionError("PlacedObject loader.loadModel(" + modelPath + ") did not return a proper PandaNode!")
        
        self.modelNode.reparentTo(parentNode)
        self.modelNode.setName(nodeName)

class CollidableObject(PlacedObject): # Makes PlacedObject into the parent of the child class CollidableObject
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str):
        super(CollidableObject, self).__init__(loader, modelPath, parentNode, nodeName) # Applies the 

        self.collisionNode = self.modelNode.attachNewNode(CollisionNode(nodeName + '_cNode')) #_cNode signifies that it is a collidable object

class InverseSphereCollideObject(CollidableObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, colPositionVec: Vec3, colRadius: float):
        super(InverseSphereCollideObject, self).__init__(loader, modelPath, parentNode, nodeName)
        self.collisionNode.node().addSolid(CollisionInvSphere(colPositionVec, colRadius))
        
        #self.collisionNode.show()

class CapsuleCollidableObject(CollidableObject):
    # a and b represent the furthest points away on each side of the capsule
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, ax: float, ay: float, az: float, bx: float, by: float, bz: float, r: float):
        super(CapsuleCollidableObject, self).__init__(loader, modelPath, parentNode, nodeName)
        self.collisionNode.node().addSolid(CollisionCapsule(ax, ay, az, bx, by, bz, r))
        
        self.collisionNode.show()

class SphereCollidableObject(CollidableObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, x: float, y: float, z: float, r: float):
        super(SphereCollidableObject, self).__init__(loader, modelPath, parentNode, nodeName)
        self.collisionNode.node().addSolid(CollisionSphere(x, y, z, r))

        self.collisionNode.show()