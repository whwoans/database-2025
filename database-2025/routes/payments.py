from flask import Blueprint, request, jsonify, render_template
from models import db, Payment, Store
from utils.auth import owner_required, get_current_owner, verify_store_ownership

bp = Blueprint('payments', __name__)

@bp.route('/store/<int:store_id>', methods=['POST'])
@owner_required
def add_payment(store_id):
    """결제 수단 추가 (사장 인증 + 소유권 확인)"""
    owner = get_current_owner()
    if not owner:
        return jsonify({'error': '사장 인증이 필요합니다.'}), 401
    
    # 가게 소유권 확인
    if not verify_store_ownership(store_id, owner.id):
        return jsonify({'error': '가게 소유권이 없습니다.'}), 403
    
    data = request.get_json()
    if 'payment' not in data:
        return jsonify({'error': '결제 수단을 입력해주세요.'}), 400
    
    payment = Payment(
        store_id=store_id,
        payment=data['payment']
    )
    
    try:
        db.session.add(payment)
        db.session.commit()
        return jsonify({'message': '결제 수단이 추가되었습니다.', 'payment_id': payment.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/store/<int:store_id>/<int:payment_id>', methods=['DELETE'])
@owner_required
def remove_payment(store_id, payment_id):
    """결제 수단 제거 (사장 인증 + 소유권 확인)"""
    owner = get_current_owner()
    if not owner:
        return jsonify({'error': '사장 인증이 필요합니다.'}), 401
    
    # 가게 소유권 확인
    if not verify_store_ownership(store_id, owner.id):
        return jsonify({'error': '가게 소유권이 없습니다.'}), 403
    
    payment = Payment.query.filter_by(id=payment_id, store_id=store_id).first()
    if not payment:
        return jsonify({'error': '결제 수단을 찾을 수 없습니다.'}), 404
    
    try:
        db.session.delete(payment)
        db.session.commit()
        return jsonify({'message': '결제 수단이 제거되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/store/<int:store_id>', methods=['GET'])
def get_store_payments(store_id):
    """가게 결제 수단 목록"""
    payments = Payment.query.filter_by(store_id=store_id).all()
    return jsonify([{
        'id': payment.id,
        'payment': payment.payment
    } for payment in payments]), 200

# 템플릿 라우트
@bp.route('/page')
def payment_page():
    """결제 페이지"""
    return render_template('payment.html')

