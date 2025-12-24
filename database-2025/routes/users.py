from flask import Blueprint, request, jsonify, session, render_template
from models import db, User
from utils.auth import login_required, get_current_user

bp = Blueprint('users', __name__)

@bp.route('/check-id', methods=['POST'])
def check_user_id():
    """아이디 중복 확인"""
    data = request.get_json()
    
    if not data or 'user_id' not in data:
        return jsonify({'error': '아이디를 입력해주세요.'}), 400
    
    user_id = data['user_id'].strip()
    if not user_id:
        return jsonify({'error': '아이디를 입력해주세요.'}), 400
    
    # 아이디 중복 확인
    existing_user = User.query.filter_by(user_id=user_id).first()
    if existing_user:
        return jsonify({'available': False, 'message': '이미 존재하는 아이디입니다.'}), 200
    else:
        return jsonify({'available': True, 'message': '사용 가능한 아이디입니다.'}), 200

@bp.route('/register', methods=['POST'])
def register():
    """회원가입"""
    data = request.get_json()
    
    if not all(k in data for k in ['user_id', 'passwd', 'email', 'name', 'address']):
        return jsonify({'error': '필수 필드가 누락되었습니다.'}), 400
    
    # 아이디 중복 확인
    if User.query.filter_by(user_id=data['user_id']).first():
        return jsonify({'error': '이미 존재하는 아이디입니다.'}), 400
    
    user = User(
        user_id=data['user_id'],
        email=data['email'],
        name=data['name'],
        address=data['address']
    )
    user.set_password(data['passwd'])
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': '회원가입이 완료되었습니다.', 'user_id': user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """로그인"""
    data = request.get_json()
    
    if not all(k in data for k in ['user_id', 'passwd']):
        return jsonify({'error': '아이디와 비밀번호를 입력해주세요.'}), 400
    
    user = User.query.filter_by(user_id=data['user_id']).first()
    
    if not user or not user.check_password(data['passwd']):
        return jsonify({'error': '아이디 또는 비밀번호가 잘못되었습니다.'}), 401
    
    session['user_id'] = user.id
    return jsonify({'message': '로그인 성공', 'user_id': user.id}), 200

@bp.route('/logout', methods=['POST'])
def logout():
    """로그아웃"""
    session.pop('user_id', None)
    return jsonify({'message': '로그아웃되었습니다.'}), 200

@bp.route('/me', methods=['GET'])
@login_required
def get_current_user_info():
    """현재 로그인한 사용자 정보 조회"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
    return jsonify({
        'id': user.id,
        'user_id': user.user_id,
        'email': user.email,
        'name': user.name,
        'address': user.address,
        'created_at': user.created_at.isoformat()
    }), 200

@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """사용자 정보 조회"""
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'user_id': user.user_id,
        'email': user.email,
        'name': user.name,
        'address': user.address,
        'created_at': user.created_at.isoformat()
    }), 200

@bp.route('/modify/address', methods=['POST'])
@login_required
def modify_address():
    """주소 수정"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
    
    data = request.get_json()
    if 'address' not in data:
        return jsonify({'error': '주소를 입력해주세요.'}), 400
    
    user.address = data['address']
    
    try:
        db.session.commit()
        return jsonify({'message': '주소가 수정되었습니다.', 'address': user.address}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 템플릿 라우트
@bp.route('/firstpage')
def firstpage():
    """로그인/회원가입 첫 페이지"""
    return render_template('firstpage.html')

@bp.route('/signup')
def signup():
    """회원가입 페이지"""
    return render_template('signup.html')

@bp.route('/setting')
def setting():
    """설정 페이지"""
    return render_template('setting.html')

