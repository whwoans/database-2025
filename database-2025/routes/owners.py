from flask import Blueprint, request, jsonify, session, render_template
from models import db, Owner
from utils.auth import owner_required, get_current_owner

bp = Blueprint('owners', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """사장 회원가입"""
    data = request.get_json()
    
    if not all(k in data for k in ['owner_id', 'owner_passwd', 'email']):
        return jsonify({'error': '필수 필드가 누락되었습니다.'}), 400
    
    # 아이디 중복 확인
    if Owner.query.filter_by(owner_id=data['owner_id']).first():
        return jsonify({'error': '이미 존재하는 아이디입니다.'}), 400
    
    owner = Owner(
        owner_id=data['owner_id'],
        email=data['email']
    )
    owner.set_password(data['owner_passwd'])
    
    try:
        db.session.add(owner)
        db.session.commit()
        return jsonify({'message': '사장 회원가입이 완료되었습니다.', 'owner_id': owner.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """사장 로그인"""
    data = request.get_json()
    
    if not all(k in data for k in ['owner_id', 'owner_passwd']):
        return jsonify({'error': '아이디와 비밀번호를 입력해주세요.'}), 400
    
    owner = Owner.query.filter_by(owner_id=data['owner_id']).first()
    
    if not owner or not owner.check_password(data['owner_passwd']):
        return jsonify({'error': '아이디 또는 비밀번호가 잘못되었습니다.'}), 401
    
    session['owner_id'] = owner.id
    return jsonify({'message': '로그인 성공', 'owner_id': owner.id}), 200

@bp.route('/logout', methods=['POST'])
def logout():
    """로그아웃"""
    session.pop('owner_id', None)
    return jsonify({'message': '로그아웃되었습니다.'}), 200

@bp.route('/me', methods=['GET'])
@owner_required
def get_current_owner_info():
    """현재 로그인한 사장 정보 조회"""
    owner = get_current_owner()
    if not owner:
        return jsonify({'error': '사장을 찾을 수 없습니다.'}), 404
    return jsonify({
        'id': owner.id,
        'owner_id': owner.owner_id,
        'email': owner.email
    }), 200

@bp.route('/<int:owner_id>', methods=['GET'])
def get_owner(owner_id):
    """사장 정보 조회"""
    owner = Owner.query.get_or_404(owner_id)
    return jsonify({
        'id': owner.id,
        'owner_id': owner.owner_id,
        'email': owner.email
    }), 200

# 템플릿 라우트
@bp.route('/page')
def owner_page():
    """사장 페이지"""
    return render_template('owner.html')

