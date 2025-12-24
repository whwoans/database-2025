from functools import wraps
from flask import session, jsonify, request
from models import db, User, Owner

def login_required(f):
    """사용자 인증 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '로그인이 필요합니다.'}), 401
        return f(*args, **kwargs)
    return decorated_function

def owner_required(f):
    """사장 인증 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        owner_id = session.get('owner_id')
        if not owner_id:
            return jsonify({'error': '사장 인증이 필요합니다.'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """현재 로그인한 사용자 반환"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

def get_current_owner():
    """현재 로그인한 사장 반환"""
    owner_id = session.get('owner_id')
    if owner_id:
        return Owner.query.get(owner_id)
    return None

def verify_store_ownership(store_id, owner_id):
    """가게 소유권 확인"""
    from models import Store
    store = db.session.get(Store, store_id)
    if not store or store.owner_id != owner_id:
        return False
    return True

