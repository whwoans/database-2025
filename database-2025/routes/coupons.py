from flask import Blueprint, request, jsonify
from models import db, Coupon, Store, Owner
from utils.auth import login_required, get_current_user

bp = Blueprint('coupons', __name__)

@bp.route('/store/<int:store_id>', methods=['POST'])
@login_required
def create_coupon(store_id):
    """쿠폰 생성 (User 로그인 필요 - User가 Owner 역할)"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    
    # 가게 존재 확인
    store = Store.query.get(store_id)
    if not store:
        return jsonify({'error': '가게를 찾을 수 없습니다.'}), 404
    
    # User의 user_id로 Owner 찾기
    owner = Owner.query.filter_by(owner_id=user.user_id).first()
    if not owner:
        return jsonify({'error': '사장님 정보를 찾을 수 없습니다.'}), 404
    
    # 가게 소유권 확인
    if store.owner_id != owner.id:
        return jsonify({'error': '가게 소유권이 없습니다.'}), 403
    
    data = request.get_json()
    
    # 필수 필드 검증
    if 'discount' not in data or data.get('discount') is None:
        return jsonify({'error': '할인 금액 또는 할인율을 입력해주세요.'}), 400
    
    coupon = Coupon(
        store_id=store_id,
        period=data.get('period'),
        discount=data.get('discount'),
        is_deleted=False
    )
    
    try:
        db.session.add(coupon)
        db.session.commit()
        return jsonify({'message': '쿠폰이 생성되었습니다.', 'coupon_id': coupon.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/store/<int:store_id>', methods=['GET'])
def get_store_coupons(store_id):
    """가게 쿠폰 목록"""
    coupons = Coupon.query.filter_by(store_id=store_id, is_deleted=False).all()
    return jsonify([{
        'id': coupon.id,
        'period': coupon.period,
        'discount': coupon.discount
    } for coupon in coupons]), 200

@bp.route('/store/<int:store_id>/<int:coupon_id>', methods=['DELETE'])
@login_required
def delete_coupon(store_id, coupon_id):
    """쿠폰 삭제 (User 로그인 필요 - User가 Owner 역할)"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    
    # 가게 존재 확인
    store = Store.query.get(store_id)
    if not store:
        return jsonify({'error': '가게를 찾을 수 없습니다.'}), 404
    
    # User의 user_id로 Owner 찾기
    owner = Owner.query.filter_by(owner_id=user.user_id).first()
    if not owner:
        return jsonify({'error': '사장님 정보를 찾을 수 없습니다.'}), 404
    
    # 가게 소유권 확인
    if store.owner_id != owner.id:
        return jsonify({'error': '가게 소유권이 없습니다.'}), 403
    
    coupon = Coupon.query.filter_by(id=coupon_id, store_id=store_id).first()
    if not coupon:
        return jsonify({'error': '쿠폰을 찾을 수 없습니다.'}), 404
    
    coupon.is_deleted = True
    
    try:
        db.session.commit()
        return jsonify({'message': '쿠폰이 삭제되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

