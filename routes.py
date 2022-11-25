import os

from app import app, db
from flask import request, Response, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    current_user,
)
from controllers.user import (
    serialize_user,
    add_user,
    validate_password,
    delete_user,
    get_all_users,
    get_user_by_email,
    get_user_by_id,
)
from controllers.room import (
    serialize_room,
    add_room,
    delete_room,
    get_room_by_id,
    get_rooms,
)
from controllers.room_membership import (
    serialize_membership,
    create_membership,
    get_room_memberships,
)
from controllers.retro import (
    get_all_retros,
    add_retro,
    serialize_retro,
    get_retro_by_id,
    get_room_retros,
    delete_retro,
)
from controllers.column import (
    get_all_columns,
    add_column,
    serialize_column,
    get_column_by_id,
    get_retro_columns,
    delete_column,
)
from controllers.card import get_all_cards

# ===== AUTH ===== #


@app.route("/api/login", methods=["POST"])
def login():
    re = request.get_json()
    user = get_user_by_email(re["email"])
    if validate_password(re["password"], user.password):
        access_token = create_access_token(identity=user.id)

        return jsonify(access_token=access_token)
    return jsonify("Login failed"), 401


@app.route("/api/whoami")
@jwt_required()
def get_current_user():
    return serialize_user(current_user)


# ===== USER ===== #


@app.route("/api/user", methods=["POST"])
def create_user():
    re = request.get_json()
    return serialize_user(add_user(re["name"], re["email"], re["password"]))


@app.route("/api/user/<id>", methods=["GET", "DELETE"])
@jwt_required()
def get_user_id(id):
    if request.method == "DELETE":
        delete_user(id)
        return "", 204

    return serialize_user(get_user_by_id(id))


# ===== ROOM ===== #


@app.route("/api/room", methods=["POST"])
@jwt_required()
def create_room():
    re = request.get_json()
    room = add_room(re["name"])

    create_membership(room_id=room.id, user_id=current_user.id, is_admin=True)

    return serialize_room(room)


@app.route("/api/rooms")
@jwt_required()
def room_list():
    room_memberships = get_room_memberships(current_user.id)
    ids = []
    for membership in room_memberships:
        ids.append(membership.room_id)
    return serialize_room(get_rooms(ids), many=True)


@app.route("/api/room/<id>", methods=["GET", "DELETE"])
@jwt_required()
def get_room_id(id):
    if request.method == "DELETE":
        delete_room(id)
        return "", 204

    return serialize_room(get_room_by_id(id))


# ===== RETRO ===== #


@app.route("/api/room/<room_id>/retro", methods=["POST"])
@jwt_required()
def create_retro(room_id):
    return serialize_retro(add_retro(room_id))


@app.route("/api/room/<room_id>/retros")
@jwt_required()
def room_retros_list(room_id):
    return serialize_retro(get_room_retros(room_id), many=True)


@app.route("/api/retro/<id>", methods=["GET", "DELETE"])
@jwt_required()
def get_retro_id(id):
    if request.method == "DELETE":
        delete_retro(id)
        return "", 204

    return serialize_retro(get_retro_by_id(id))


# ===== COLUMN ===== #


@app.route("/api/retro/<retro_id>/column", methods=["POST"])
@jwt_required()
def create_column(retro_id):
    re = request.get_json()
    return serialize_column(add_column(retro_id, re["name"], re["color"]))


@app.route("/api/retro/<retro_id>/columns")
@jwt_required()
def retro_columns_list(retro_id):
    return serialize_column(get_retro_columns(retro_id), many=True)


@app.route("/api/column/<id>", methods=["GET", "DELETE"])
@jwt_required()
def get_column_id(id):
    if request.method == "DELETE":
        delete_column(id)
        return "", 204

    return serialize_column(get_column_by_id(id))


# ===== OTHER ===== #


@app.route("/api/users")  # delete
def user_list():
    return serialize_user(get_all_users(), many=True)


@app.route("/api/retros")  # delete
def retro_list():
    return get_all_retros()


@app.route("/api/columns")  # delete
def columns_list():
    return get_all_columns()


@app.route("/api/cards")  # delete
def cards_list():
    return get_all_cards()


@app.route("/api/reset")  # delete
def reset_db():
    try:
        os.remove("instance/project.db")
    except:
        pass

    with app.app_context():
        db.create_all()

    return Response("OK", 200)
