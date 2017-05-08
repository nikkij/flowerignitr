from flask import Flask
from flask import jsonify
from flask import request
from geopy.distance import great_circle
import uuid

# TODO leader election
# TODO all nodes keep a look up table of the complete list of nodes and calculate
#      their own distance from all other nodes so that calculation doesn't have to
#      happen in realtime on motion detection
# TODO rewrite the nodes list so they're keyed by uuid for faster look ups


app = Flask(__name__)

# nodes = [{'id':uuid.uuid1(), 'name':'flower 1', 'address':'localhost:5051', 'lat':43.079657, 'long':-105.179252, 'distance':0},
#          {'id':uuid.uuid1(), 'name':'flower 2', 'address':'localhost:5052', 'lat':45.0, 'long':-105.179252, 'distance':0},
# 				 {'id':uuid.uuid1(), 'name':'flower 3', 'address':'localhost:5052', 'lat':40.0, 'long':-105.179252, 'distance':0}]
mode = 'gps'
nodes = []

@app.route("/")
def hello():
    return jsonify(nodes)

@app.route("/register", methods=['POST'])
def register():
		global nodes
		print("Registering node ...")
		requestData = request.json
		node = requestData['node']
		nodeId = node['id']
		nodeToRegisterExists = getNodeByUuid(nodeId)

		if nodeToRegisterExists:
			response = {"failed":[{"message":"Node already registered"}]}
			return jsonify(response)
		else:
			nodes.append(node)

		response = {"success":[{"node-id":node['id']}]}
		return jsonify(response)

@app.route("/motion", methods=['POST'])
def motion():
		global nodes
		print("Motion detected ....")
		requestData = request.json
		nodeId = requestData['node-id']
		nodeMotionDetectedAt = getNodeByUuid(nodeId)
		print(nodeMotionDetectedAt)

		# run algorithm to calculate distance for each node
		for node in nodes:
			print(node)
			distance = calcDistance(nodeMotionDetectedAt['x'], nodeMotionDetectedAt['y'], node['x'], node['y'])
			print("Distance between nodes is")
			print(distance)
			node['distance'] = distance

		# run algorithm to sort list from closest to furthest to the node where motion was detected
		sortedNodes = sorted(nodes, key=lambda k: k["distance"])

		# send flare message to that nodes /flare endpoint (with delay?)
		sendFlareMessage(sortedNodes)

		nodes = sortedNodes
		response = {"success":sortedNodes}
		return jsonify(response)

def calcDistance(x1, y1, x2, y2):
		print(x1)
		point1 = (x1, y1)
		point2 = (x2, y2)
		print("Calculating distance")
		return great_circle(point1, point2).feet

def getNodeByUuid(uuid):
		for node in nodes:
			if node['id'] == uuid:
				return node

def sendFlareMessage(listOfNodesToFlare):
		for node in listOfNodesToFlare:
			print("flare")
			# TODO get all nodes that are within 1ft
			#      send flare message
			# 		 get all nodes that are within 2ft
			#      send flare message
			#      until nodes are exhausted
			print(listOfNodesToFlare)

if __name__ == "__main__":
    app.run(port='5050')
