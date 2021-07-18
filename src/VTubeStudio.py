from websocket import create_connection
import json
import os

class vtubeClient:
    def __init__(self):
        self.clientInstance = create_connection("ws://127.0.0.1:8001")
        self.token = self.checkToken()
        self.authenticateInstance()

    def checkToken(self):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "AuthenticationTokenRequest",
            "data": {
                    "pluginName": "pythonClient",
                    "pluginDeveloper": "Ashe Muller"
            }
        }
        
        if os.path.exists('token') != True:
            self.clientInstance.send(json.dumps(payload))
            token = json.loads(self.clientInstance.recv())['data']['authenticationToken']
            with open('token', 'w+') as f:
                f.write(token)
        else:
            with open('token', 'r') as f:
                return f.readline()
                
    def authenticateInstance(self):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "AuthenticationRequest",
            "data": {
                    "pluginName": "pythonClient",
                    "pluginDeveloper": "Ashe Muller",
                    "authenticationToken": self.token
            }
        }    
        self.clientInstance.send(json.dumps(payload))
        recieve = json.loads(self.clientInstance.recv())
        if recieve["data"]["authenticated"] == True:
            print("Authenticated User Successfully.")
        else:
            print("Failed to authenticate user {recieve['data']['reason'}")

    def statsRequest(self):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "StatisticsRequest"
        }

        self.clientInstance.send(json.dumps(payload))
        print("sending statRequest")
        recieve = json.loads(self.clientInstance.recv())
        print(f"Recieved stats {recieve}")

    def getFolders(self):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeID",
            "messageType": "VTSFolderInfoRequest"
        }

        self.clientInstance.send(json.dumps(payload))
        print("sending folders")
        recieve = json.loads(self.clientInstance.recv())
        print(f"Recieved folders {recieve}")

    def getCurrentModel(self):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeID",
            "messageType": "CurrentModelRequest"
        }

        self.clientInstance.send(json.dumps(payload))
        print("sending getModel")
        recieve = json.loads(self.clientInstance.recv())
        print(f"Recieved getModel {recieve}")

    def getAllModels(self):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "SomeID",
            "messageType": "AvailableModelsRequest"
        }
        
        self.clientInstance.send(json.dumps(payload))
        print("sending getAllModels")
        return json.loads(self.clientInstance.recv())

    def getIdByName(self, name):
        modelCache = self.getAllModels()
        found = False
        for item in modelCache['data']['availableModels']:
            if item['modelName'] == name:
                print(f"Found model with specified name {name} and returning ID {item['modelID']}")
                found = True
                return item['modelID']
        if found == False:
            print(f"Failed to find model with name {name}")
            
    def loadModel(self, name=None, modelId=None):
        if name != None:
            modelId = self.getIdByName(name)
        if modelId != None:
            payload = {
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": "SomeID",
                "messageType": "ModelLoadRequest",
                "data": {
                        "modelID": modelId
                }
            }
            self.clientInstance.send(json.dumps(payload))
            print("sending loadModel message")
            recieve = json.dumps(json.loads(self.clientInstance.recv()), indent=4, sort_keys=True)
            if recieve != None:
                print(f"Model loaded successfully")

    def getArtMeshNames(self):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "messageType": "ArtMeshListRequest"
        }
        self.clientInstance.send(json.dumps(payload))
        print(f"List of art meshes (by name): {', '.join(json.loads(self.clientInstance.recv())['data']['artMeshNames'])}")
        
    def tintArtMesh(self, color, meshNames):
        colors = list(tuple(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)))
        print(str(colors))
        if meshNames != None and type(meshNames) == list:
            payload = {
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": "SomeID",
                "messageType": "ColorTintRequest",
                "data": {
                        "colorTint": {
                                "colorR": colors[0],
                                "colorG": colors[1],
                                "colorB": colors[2],
                                "colorA": 255
                        },
                        "artMeshMatcher": {
                                "tintAll": False,
                                "nameExact": meshNames,
                        },
                }
            }
            print(str(payload))
            self.clientInstance.send(json.dumps(payload))
            print("sending tintArtMesh message")
            recieve = json.loads(self.clientInstance.recv())
            print(f"recieved data {recieve}")
            if recieve['data']['matchedArtMeshes'] != 0:
                print(f"Successfully altered the colors of {recieve['data']['matchedArtMeshes']} meshes.")
            else:
                print("Failed to alter the colors of any meshes. Please try again.")
        else:
            print("Err: Please provide mesh names exactly as they appear in getArtMeshNames return in list format.")
