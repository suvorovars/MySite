import flask
from flask import jsonify, request

from . import db_session
from .application import Application

blueprint = flask.Blueprint(
    'application_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/application')
def get_news():
    db_sess = db_session.create_session()
    applic = db_sess.query(Application).all()
    return jsonify(
        {
            'application':
                [item.to_dict(only=('title', 'content', 'text', 'feedback', 'user.name', 'created_date'))
                 for item in applic]
        }
    )


@blueprint.route('/api/application/<int:applic_id>', methods=['GET'])
def get_one_news(applic_id):
    db_sess = db_session.create_session()
    applic = db_sess.query(Application).get(applic_id)
    if not applic:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'application': applic.to_dict(only=(
                'title', 'content', 'text', 'feedback', 'user.name', 'created_date'))
        }
    )


@blueprint.route('/api/application', methods=['POST'])
def create_news():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['title', 'content', 'text', 'feedback', 'user_id', 'created_date']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    applic = Application(
        title=request.json['title'],
        content=request.json['content'],
        text=request.json['text'],
        feedback=request.json['feedback'],
        user_id=request.json['user_id'],
        created_date=request.json['created_date']

    )
    db_sess.add(applic)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/application/<int:applic_id>', methods=['DELETE'])
def delete_news(applic_id):
    db_sess = db_session.create_session()
    applic = db_sess.query(Application).get(applic_id)
    if not applic:
        return jsonify({'error': 'Not found'})
    db_sess.delete(applic)
    db_sess.commit()
    return jsonify({'success': 'OK'})