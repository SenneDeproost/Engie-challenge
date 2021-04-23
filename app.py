from flask import Flask, request, jsonify
from CommitmentController import CommitmentController

app = Flask(__name__)


@app.route('/productionplan', methods=['POST'])
def productionplan():
    data = request.get_json()
    controller = CommitmentController(data)
    response = controller.calculate_commitment()
    return jsonify(response)


app.run(port=8888, debug=True)
