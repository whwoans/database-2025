from flask import Blueprint, request, jsonify
from models import db, Review, Store
from utils.auth import login_required, get_current_user, owner_required, get_current_owner, verify_store_ownership

bp = Blueprint('reviews', __name__)

@bp.route('', methods=['POST'])
@login_required
def create_review():
    """리뷰 작성 (사용자 인증 필요)"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
    
    data = request.get_json()
    
    if not all(k in data for k in ['store_id', 'rating']):
        return jsonify({'error': '가게 ID와 평점이 필요합니다.'}), 400
    
    store_id = data['store_id']
    order_id = data.get('order_id')  # 주문 ID (선택사항)
    
    # 가게 존재 확인
    store = Store.query.get(store_id)
    if not store:
        return jsonify({'error': '존재하지 않는 가게입니다.'}), 404
    
    # 주문 ID가 제공된 경우 주문 존재 확인 및 중복 리뷰 확인
    if order_id:
        from models import Order
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': '존재하지 않는 주문입니다.'}), 404
        
        # 해당 주문에 대한 리뷰가 이미 있는지 확인
        existing_review = Review.query.filter_by(
            user_id=user.id,
            order_id=order_id
        ).first()
        
        if existing_review:
            return jsonify({'error': '이미 해당 주문에 대한 리뷰를 작성하셨습니다.'}), 400
    
    # 평점 유효성 검사
    rating = data['rating']
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'error': '평점은 1~5 사이의 정수여야 합니다.'}), 400
    
    review = Review(
        user_id=user.id,
        store_id=store_id,
        order_id=order_id,  # 주문 ID 추가
        rating=rating,
        content=data.get('content', '')
    )
    
    try:
        db.session.add(review)
        # 가게의 리뷰 개수 업데이트
        store.reviewCount = Review.query.filter_by(store_id=store_id).count() + 1
        db.session.commit()
        return jsonify({'message': '리뷰가 작성되었습니다.', 'review_id': review.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/store/<int:store_id>', methods=['GET'])
def get_store_reviews(store_id):
    """가게 리뷰 목록"""
    reviews = Review.query.filter_by(store_id=store_id).order_by(Review.created_at.desc()).all()
    return jsonify([{
        'id': review.id,
        'user_id': review.user_id,
        'user_name': review.user.name if review.user else None,
        'rating': review.rating,
        'content': review.content,
        'created_at': review.created_at.isoformat()
    } for review in reviews]), 200

@bp.route('/<int:review_id>', methods=['DELETE'])
@login_required
def delete_review(review_id):
    """리뷰 삭제 (사장 인증 + 가게 소유권 확인)"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    
    # 리뷰 조회
    review = db.session.get(Review, review_id)
    if not review:
        return jsonify({'error': '리뷰를 찾을 수 없습니다.'}), 404
    
    # 가게 조회
    store = db.session.get(Store, review.store_id)
    if not store:
        return jsonify({'error': '가게를 찾을 수 없습니다.'}), 404
    
    # Owner 찾기
    from models import Owner
    owner = Owner.query.filter_by(owner_id=user.user_id).first()
    if not owner:
        return jsonify({'error': '사장님 정보를 찾을 수 없습니다.'}), 404
    
    # 가게 소유권 확인
    if store.owner_id != owner.id:
        return jsonify({'error': '리뷰 삭제 권한이 없습니다.'}), 403
    
    try:
        # 리뷰 삭제
        db.session.delete(review)
        db.session.flush()  # 삭제를 먼저 반영
        
        # 가게의 리뷰 개수 업데이트 (삭제 후 개수 재계산)
        store.reviewCount = Review.query.filter_by(store_id=store.id).count()
        db.session.commit()
        return jsonify({'message': '리뷰가 삭제되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

