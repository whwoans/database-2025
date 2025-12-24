from flask import Blueprint, request, jsonify, render_template
from models import db, Rider

bp = Blueprint('riders', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """라이더 등록"""
    data = request.get_json()
    
    if not all(k in data for k in ['rider_id', 'phone', 'vehicle']):
        return jsonify({'error': '필수 필드가 누락되었습니다.'}), 400
    
    # 아이디 중복 확인
    if Rider.query.filter_by(rider_id=data['rider_id']).first():
        return jsonify({'error': '이미 존재하는 라이더 ID입니다.'}), 400
    
    rider = Rider(
        rider_id=data['rider_id'],
        phone=data['phone'],
        vehicle=data['vehicle']
    )
    
    try:
        db.session.add(rider)
        db.session.commit()
        return jsonify({'message': '라이더 등록이 완료되었습니다.', 'rider_id': rider.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:rider_id>', methods=['GET'])
def get_rider(rider_id):
    """라이더 정보 조회"""
    rider = Rider.query.get_or_404(rider_id)
    return jsonify({
        'id': rider.id,
        'rider_id': rider.rider_id,
        'phone': rider.phone,
        'vehicle': rider.vehicle
    }), 200

@bp.route('/by-user-id/<string:user_id>', methods=['GET'])
def get_rider_by_user_id(user_id):
    """User ID로 라이더 정보 조회"""
    rider = Rider.query.filter_by(rider_id=user_id).first()
    if not rider:
        return jsonify({'error': '라이더가 등록되어 있지 않습니다.'}), 404
    
    return jsonify({
        'id': rider.id,
        'rider_id': rider.rider_id,
        'phone': rider.phone,
        'vehicle': rider.vehicle
    }), 200

# 템플릿 라우트
@bp.route('/page')
def rider_page():
    """라이더 페이지"""
    return render_template('rider.html')

