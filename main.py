import random
from flask import Flask, jsonify, render_template, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from pandas import DataFrame

app = Flask(__name__)
# api = Api(app)

# class CafeWork(Resource):
#     def get(self,location, test):
#         return {"location": location, "test": test}
#
# api.add_resource(CafeWork, "/search/<string:location/<int:test>")


##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
            print(getattr(self, column.name))
        return dictionary

    # def to_search(self,loc):
    #     dictionary = {}
    #     for column in self.__table__.columns:
    #         # Create a new dictionary entry;
    #         # where the key is the name of the column
    #         # and the value is the value of the column
    #         dictionary[column.location] = getattr(self, column.name)
    #         if dictionary[column.location] == loc:
    #             # id = getattr(self, column.location)
    #             for c
    #             # return id
    #     return "sorry"


@app.route("/")
def home():
    return render_template("index.html")


# @app.route("/random", methods=['GET'])
# def get_random_cafe():
#     pass
## But GET is allowed by default on all routes.
# So this is much simpler:


## HTTP GET - Read Record

@app.route("/all")
def all_cafe():
    cafes = db.session.query(Cafe).all()
    # brings all cafe results in db.
    latestu = []
    for cafe in cafes:
        testu = cafe.to_dict()
        latestu.append(testu)
    return jsonify(cafe=latestu)
    # list comprehension
    # return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc").title()
    # This one brings all result where entered location info.
    # cafes = db.session.query(Cafe).filter_by(location=query_location).all()
    # if cafes:
    #     all_cafe_info = []
    #     for cafe in cafes:
    #         cafe_infos_in_dic = cafe.to_dict()
    #         all_cafe_info.append(cafe_infos_in_dic)
    #     return jsonify(cafe=all_cafe_info)
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})
    # return jsonify(cafe=random_cafe.to_dict())


## HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.form.get("new_price")
    # cafe = db.session.query(Cafe).filter_by(id=cafe_id).first()
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        db.session.close()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
        # abort(400)


## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api_key")
    if api_key == "TopSecretAPIKey":
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
