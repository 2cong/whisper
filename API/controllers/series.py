import os, sys

BASE_DIR = os.path.dirname(os.path.abspath("API"))
sys.path.extend([BASE_DIR])

import pymysql
from flask import Blueprint, request, jsonify

from connections import db_connector
from models import ModelDao

series_app = Blueprint("series_app", __name__)
model_dao = ModelDao()

@series_app.route('', methods=['POST'])
def new_series():
    """새로운 시리즈 생성 API.

    Headers:
        Token

    Args:
        user_id: 사용자 id
        name: 생성될 시리즈 이름

    Return:
        None

    Exceptions:
        InternalError: DATABASE가 존재하지 않을 때 발생
        OperationalError: DATABASE 접속이 인가되지 않았을 때 발생
        ProgramingError: SQL syntax가 잘못되었을 때 발생
        IntegrityError: Key의 무결성을 해쳤을 때 발생
        DataError: 컬럼 타입과 매칭되지 않는 값이 DB에 전달되었을 때 발생
        KeyError: 엔드포인트에서 요구하는 키값이 전달되지 않았을 때 발생
    """
    db = None
    try:
        # user_id = 토큰에서 받아온 user_id
        user_id = 1
        name = request.json['name']

        db = db_connector()
        # db 에러처리
        if db is None:
            return jsonify(message="DATABASE_INIT_ERROR"), 500

        # 시리즈 중복 확인
        series_id = model_dao.search_series(db, user_id, name)
        # 시리즈가 존재하면 Error
        if series_id:
            return jsonify(message="EXIST_SERIES"), 400

        # db에 값 추가
        db.begin()
        model_dao.insert_series(db, user_id, name)
        db.commit()

        return (''), 200

    except pymysql.err.InternalError:
        db.rollback()
        return jsonify(message="DATABASE_DOES_NOT_EXIST"), 500
    except pymysql.err.OperationalError:
        db.rollback()
        return jsonify(message="DATABASE_AUTHORIZATION_DENIED"), 500
    except pymysql.err.ProgrammingError:
        db.rollback()
        return jsonify(message="DATABASE_SYNTAX_ERROR"), 500
    except pymysql.err.IntegrityError:
        db.rollback()
        return jsonify(message="FOREIGN_KEY_CONSTRAINT_ERROR"), 500
    except pymysql.err.DataError:
        db.rollback()
        return jsonify(message="DATA_ERROR"), 400
    except KeyError:
        db.rollback()
        return jsonify(message="KEY_ERROR"), 400
    except Exception as e:
        db.rollback()
        return jsonify(message=f"{e}"), 500
    finally:
        if db:
            db.close()

@series_app.route('', methods=['GET'])
def find_user_series():
    """user별 시리즈 조회.

    Headers:
        token

    Args:

    """
    db = None
    try:
        user_id = 1

        db = db_connector()
        if db is None:
            return jsonify(message="DATABASE_INIT_ERROR"), 500

        series_data = model_dao.my_series(db, user_id)
        data = [
            {
                "id": series['id'],
                "name": series['name'],
                "count": model_dao.count_series_diary(db, user_id, series['id'])
            }for series in series_data ]

        return jsonify(data), 200

    except pymysql.err.InternalError:
        return jsonify(message="DATABASE_DOES_NOT_EXIST"), 500
    except pymysql.err.OperationalError:
        return jsonify(message="DATABASE_AUTHORIZATION_DENIED"), 500
    except pymysql.err.ProgrammingError:
        return jsonify(message="DATABASE_SYNTAX_ERROR"), 500
    except pymysql.err.IntegrityError:
        return jsonify(message="FOREIGN_KEY_CONSTRAINT_ERROR"), 500
    except pymysql.err.DataError:
        return jsonify(message="DATA_ERROR"), 400
    except KeyError:
        return jsonify(message="KEY_ERROR"), 400
    except Exception as e:
        return jsonify(message=f"{e}"), 500
    finally:
        if db:
            db.close()

@series_app.route('/<int:series_id>', methods=['PUT'])
def change_series_name(series_id):
    """시리즈 이름 변경 API

    """
    try:
        db = None

        user_id = 1
        name = request.json['name']

        db = db_connector()
        if db is None:
            return jsonify(message="DATABASE_INIT_ERROR"), 500

        db.begin()
        model_dao.update_series_name(db, name, series_id)
        db.commit()
        return (''), 200

    except pymysql.err.InternalError:
        db.rollback()
        return jsonify(message="DATABASE_DOES_NOT_EXIST"), 500
    except pymysql.err.OperationalError:
        db.rollback()
        return jsonify(message="DATABASE_AUTHORIZATION_DENIED"), 500
    except pymysql.err.ProgrammingError:
        db.rollback()
        return jsonify(message="DATABASE_SYNTAX_ERROR"), 500
    except pymysql.err.IntegrityError:
        db.rollback()
        return jsonify(message="FOREIGN_KEY_CONSTRAINT_ERROR"), 500
    except pymysql.err.DataError:
        db.rollback()
        return jsonify(message="DATA_ERROR"), 400
    except KeyError:
        db.rollback()
        return jsonify(message="KEY_ERROR"), 400
    except Exception as e:
        db.rollback()
        return jsonify(message=f"{e}"), 500
    finally:
        if db:
            db.close()

@series_app.route('/<int:series_id>', methods=['DELETE'])
def delete_series(series_id):
    """시리즈 삭제하는 API.

    Header:

    """
    try:
        db = None

        user_id = 1

        db = db_connector()
        if db is None:
            return jsonify(message="DATABASE_INIT_ERROR"), 500

        db.begin()
        # 시리즈 삭제
        model_dao.delete_series_from_db(db, series_id, user_id)
        # 다이어리에서 해당 시리즈 삭제
        model_dao.delete_series_from_diaries(db, series_id, user_id)
        db.commit()
        return (''), 200

    except pymysql.err.InternalError:
        db.rollback()
        return jsonify(message="DATABASE_DOES_NOT_EXIST"), 500
    except pymysql.err.OperationalError:
        db.rollback()
        return jsonify(message="DATABASE_AUTHORIZATION_DENIED"), 500
    except pymysql.err.ProgrammingError:
        db.rollback()
        return jsonify(message="DATABASE_SYNTAX_ERROR"), 500
    except pymysql.err.IntegrityError:
        db.rollback()
        return jsonify(message="FOREIGN_KEY_CONSTRAINT_ERROR"), 500
    except pymysql.err.DataError:
        db.rollback()
        return jsonify(message="DATA_ERROR"), 400
    except KeyError:
        db.rollback()
        return jsonify(message="KEY_ERROR"), 400
    except Exception as e:
        db.rollback()
        return jsonify(message=f"{e}"), 500
    finally:
        if db:
            db.close()

@series_app.route('diary/<int:series_id>', methods=['GET'])
def diaries_series(series_id):
    """시리즈별 다이어리 보여주는 API

    """
    try:
        db = None

        user_id = 1

        db = db_connector()
        if db is None:
            return jsonify(message="DATABASE_INIT_ERROR"), 500

        diaries = model_dao.search_diaries_in_series(db, series_id, user_id)

        diary=[
            {
                "diary_id": data['id'],
                "emotion_id": data['emotion_id'],
                "image_url":data['image_url'],
                "color":data['color'],
                "summary":data['summary'],
                "like": True if data['is_deleted'] == 0 else False,
                "is_public": True if data['public'] == 1 else False,
                "count":model_dao.count_likes(db, data['id'])
            }for data in diaries]

        return jsonify(diary), 200

    except pymysql.err.InternalError:
        return jsonify(message="DATABASE_DOES_NOT_EXIST"), 500
    except pymysql.err.OperationalError:
        return jsonify(message="DATABASE_AUTHORIZATION_DENIED"), 500
    except pymysql.err.ProgrammingError:
        return jsonify(message="DATABASE_SYNTAX_ERROR"), 500
    except pymysql.err.IntegrityError:
        return jsonify(message="FOREIGN_KEY_CONSTRAINT_ERROR"), 500
    except pymysql.err.DataError:
        return jsonify(message="DATA_ERROR"), 400
    except KeyError:
        return jsonify(message="KEY_ERROR"), 400
    except Exception as e:
        return jsonify(message=f"{e}"), 500
    finally:
        if db:
            db.close()

@series_app.route('diary/<int:series_id>', methods=['POST'])
def insert_serise_diary(series_id):
    """시리즈에 다이어리 추가 API
    """
    try:
        db = None

        user_id = 1

        # requset body로 들어온 diary id를 tuple로 변경
        diaries = request.json['diary_id']
        diary_list = []
        for diary in diaries:
            diary_id = diary['id']
            diary_list.append(diary_id)
        diary_tuple = tuple(diary_list)

        db = db_connector()
        if db is None:
            return jsonify(message="DATABASE_INIT_ERROR"), 500

        db.begin()
        model_dao.update_series(db, series_id, diary_tuple, user_id)
        db.commit()
        return (''), 200

    except pymysql.err.InternalError:
        db.rollback()
        return jsonify(message="DATABASE_DOES_NOT_EXIST"), 500
    except pymysql.err.OperationalError:
        db.rollback()
        return jsonify(message="DATABASE_AUTHORIZATION_DENIED"), 500
    except pymysql.err.ProgrammingError:
        db.rollback()
        return jsonify(message="DATABASE_SYNTAX_ERROR"), 500
    except pymysql.err.IntegrityError:
        db.rollback()
        return jsonify(message="FOREIGN_KEY_CONSTRAINT_ERROR"), 500
    except pymysql.err.DataError:
        db.rollback()
        return jsonify(message="DATA_ERROR"), 400
    except KeyError:
        db.rollback()
        return jsonify(message="KEY_ERROR"), 400
    except Exception as e:
        db.rollback()
        return jsonify(message=f"{e}"), 500
    finally:
        if db:
            db.close()

@series_app.route('diary/<int:series_id>', methods=['DELETE'])
def delete_diary(series_id):
    """
    시리즈에서 다이어리 삭제하는 API
    """
    try:
        db = None

        user_id = 1

        diaries = request.json['diary_id']

        # requset body로 들어온 diary id를 tuple로 변경
        diary_list = []
        for diary in diaries:
            diary_id = diary['id']
            diary_list.append(diary_id)
        diary_tuple = tuple(diary_list)

        db = db_connector()
        if db is None:
            return jsonify(message="DATABASE_INIT_ERROR"), 500

        db.begin()
        model_dao.delete_diaries_from_series(db, diary_tuple, user_id, series_id)
        db.commit()
        return (''), 200

    except pymysql.err.InternalError:
        db.rollback()
        return jsonify(message="DATABASE_DOES_NOT_EXIST"), 500
    except pymysql.err.OperationalError:
        db.rollback()
        return jsonify(message="DATABASE_AUTHORIZATION_DENIED"), 500
    except pymysql.err.ProgrammingError:
        db.rollback()
        return jsonify(message="DATABASE_SYNTAX_ERROR"), 500
    except pymysql.err.IntegrityError:
        db.rollback()
        return jsonify(message="FOREIGN_KEY_CONSTRAINT_ERROR"), 500
    except pymysql.err.DataError:
        db.rollback()
        return jsonify(message="DATA_ERROR"), 400
    except KeyError:
        db.rollback()
        return jsonify(message="KEY_ERROR"), 400
    except Exception as e:
        db.rollback()
        return jsonify(message=f"{e}"), 500
    finally:
        if db:
            db.close()
