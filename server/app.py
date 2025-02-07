#!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        image_url = data.get('image_url')
        bio = data.get('bio')

        user = User(username=username, password_hash=password, image_url=image_url, bio=bio)
        try:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return jsonify(id=user.id, username=user.username, image_url=user.image_url, bio=user.bio), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify(error='Username already exists'), 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify(error='Unauthorized'), 401
        
        user = User.query.get(user_id)
        return jsonify(id=user.id, username=user.username, image_url=user.image_url, bio=user.bio), 200

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            session['user_id'] = user.id
            return jsonify(id=user.id, username=user.username, image_url=user.image_url, bio=user.bio)
        return jsonify(error='Invalid credentials'), 401

class Logout(Resource):
    def delete(self):
        if 'user_id' in session:
            session.pop('user_id')
            return '', 204
        return jsonify(error='Unauthorized'), 401

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify(error='Unauthorized'), 401
        
        recipes = Recipe.query.all()
        return jsonify([recipe.to_dict() for recipe in recipes]), 200

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify(error='Unauthorized'), 401
        
        data = request.get_json()
        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')

        recipe = Recipe(
            title=title, 
            instructions=instructions, 
            minutes_to_complete=minutes_to_complete, 
            user_id=user_id
        )
        try:
            db.session.add(recipe)
            db.session.commit()
            return jsonify(recipe.to_dict()), 201
        except IntegrityError as e:
            db.session.rollback()
            return jsonify(error=str(e)), 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)