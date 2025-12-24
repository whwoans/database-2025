from flask import Blueprint, request, jsonify, render_template
from models import db, FavoriteStore, Store
from utils.auth import login_required, get_current_user

bp = Blueprint('favorites', __name__)

@bp.route('', methods=['POST'])
@login_required
def add_favorite():
    """찜하기 추가 (사용자 인증 필요)"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
    
    data = request.get_json()
    if 'store_id' not in data:
        return jsonify({'error': '가게 ID가 필요합니다.'}), 400
    
    store_id = data['store_id']
    
    # 가게 존재 확인
    store = Store.query.get(store_id)
    if not store:
        return jsonify({'error': '존재하지 않는 가게입니다.'}), 404
    
    # 이미 찜한 가게인지 확인
    existing = FavoriteStore.query.filter_by(
        user_id=user.id, 
        store_id=store_id,
        is_deleted=False
    ).first()
    
    if existing:
        return jsonify({'error': '이미 찜한 가게입니다.'}), 400
    
    favorite = FavoriteStore(
        user_id=user.id,
        store_id=store_id,
        is_deleted=False
    )
    
    try:
        db.session.add(favorite)
        db.session.commit()
        return jsonify({'message': '찜하기가 추가되었습니다.', 'favorite_id': favorite.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:store_id>', methods=['DELETE'])
@login_required
def remove_favorite(store_id):
    """찜하기 제거 (사용자 인증 필요)"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
    
    favorite = FavoriteStore.query.filter_by(
        user_id=user.id,
        store_id=store_id,
        is_deleted=False
    ).first()
    
    if not favorite:
        return jsonify({'error': '찜한 가게가 아닙니다.'}), 404
    
    favorite.is_deleted = True
    
    try:
        db.session.commit()
        return jsonify({'message': '찜하기가 제거되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('', methods=['GET'])
@login_required
def get_favorites():
    """찜한 가게 목록 (사용자 인증 필요)"""
    from models import Review
    
    user = get_current_user()
    if not user:
        return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
    
    favorites = FavoriteStore.query.filter_by(
        user_id=user.id,
        is_deleted=False
    ).all()
    
    stores = []
    for fav in favorites:
        store = Store.query.get(fav.store_id)
        if store:
            # 실제 Review 테이블에서 리뷰 개수 계산
            review_count = Review.query.filter_by(store_id=store.id).count()
            
            stores.append({
                'id': store.id,
                'store_name': store.store_name,
                'category': store.category,
                'phone': store.phone,
                'minprice': store.minprice,
                'reviewCount': review_count  # 실제 리뷰 개수 사용
            })
    
    return jsonify(stores), 200

# 템플릿 라우트
@bp.route('/page')
def favorites_page():
    """찜한 가게 목록 페이지"""
    return render_template('like.html')

