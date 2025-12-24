from flask import Blueprint, request, jsonify, render_template
from models import db, Category, Store, Menu, Payment, Coupon, Order, Rider, Owner, StorePayment
from utils.auth import login_required, get_current_user

bp = Blueprint('customer', __name__)

@bp.route('/categories', methods=['GET'])
def get_categories():
    """모든 카테고리 조회"""
    categories = Category.query.all()
    return jsonify([{
        'id': cat.id,
        'category': cat.category
    } for cat in categories]), 200

@bp.route('/payment-methods', methods=['GET'])
def get_payment_methods():
    """모든 지불방식 조회"""
    payments = Payment.query.all()
    return jsonify([{
        'id': p.id,
        'method_name': p.payment
    } for p in payments]), 200

@bp.route('/categories/<int:category_id>/stores', methods=['GET'])
def get_stores_by_category(category_id):
    """카테고리별 가게 목록 (주문 수, 평균 별점 포함, 정렬 옵션 지원)"""
    from sqlalchemy import func
    from models import Review
    
    # 정렬 옵션 파라미터 받기 (기본값: name - 가나다 순)
    sort_by = request.args.get('sort', 'name')
    
    # 카테고리별 가게 조회 (category_id로만 필터링)
    stores_query = Store.query.filter_by(category_id=category_id)
    
    # 정렬 적용
    if sort_by == 'review':
        # 리뷰 많은 순 (reviewCount 내림차순)
        stores_query = stores_query.order_by(Store.reviewCount.desc())
    elif sort_by == 'rating':
        # 별점 높은 순은 평균 별점을 계산해야 하므로 일단 reviewCount로 정렬 후 프론트에서 처리
        stores_query = stores_query.order_by(Store.store_name.asc())  # 임시로 이름순
    elif sort_by == 'order':
        # 주문 많은 순은 주문 수를 계산해야 하므로 일단 이름순 후 프론트에서 처리
        stores_query = stores_query.order_by(Store.store_name.asc())  # 임시로 이름순
    else:
        # 기본: 가나다 순 (store_name 오름차순)
        stores_query = stores_query.order_by(Store.store_name.asc())
    
    stores = stores_query.all()
    result = []
    
    for store in stores:
        # 주문 수 계산
        order_count = Order.query.filter_by(store_id=store.id).count()
        
        # 평균 별점 계산
        avg_rating_result = db.session.query(func.avg(Review.rating)).filter_by(store_id=store.id).scalar()
        avg_rating = round(avg_rating_result, 1) if avg_rating_result else 0.0
        
        # 리뷰 수 계산 (실제 Review 테이블에서)
        review_count = Review.query.filter_by(store_id=store.id).count()
        
        result.append({
            'id': store.id,
            'store_name': store.store_name,
            'category': store.category,
            'phone': store.phone,
            'minprice': store.minprice,
            'reviewCount': review_count,  # 실제 리뷰 수
            'orderCount': order_count,
            'avgRating': avg_rating,
            'operationTime': store.operationTime,
            'closedDay': store.closedDay
        })
    
    # 별점이나 주문 수로 정렬해야 하는 경우 프론트에서 정렬하도록 데이터만 제공
    # (DB에서 JOIN으로 정렬하는 것이 더 효율적이지만, 현재 구조상 이렇게 처리)
    
    return jsonify(result), 200

@bp.route('/stores/<int:store_id>/menus', methods=['GET'])
def get_store_menus(store_id):
    """가게 메뉴 목록"""
    menus = Menu.query.filter_by(store_id=store_id).all()
    return jsonify([{
        'id': menu.id,
        'menu': menu.menu,
        'price': menu.price
    } for menu in menus]), 200

@bp.route('/stores/<int:store_id>/menus', methods=['POST'])
@login_required
def add_store_menu(store_id):
    """가게 메뉴 추가 (User 로그인 필요 - User가 Owner 역할)"""
    from models import Owner
    
    user = get_current_user()
    if not user:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    
    # User의 Owner 찾기
    owner = Owner.query.filter_by(owner_id=user.user_id).first()
    if not owner:
        return jsonify({'error': '가게 소유권이 없습니다.'}), 403
    
    # 가게 소유권 확인
    store = Store.query.get_or_404(store_id)
    if store.owner_id != owner.id:
        return jsonify({'error': '가게 소유권이 없습니다.'}), 403
    
    data = request.get_json()
    if not all(k in data for k in ['menu', 'price']):
        return jsonify({'error': '메뉴 이름과 가격을 입력해주세요.'}), 400
    
    menu = Menu(
        store_id=store_id,
        menu=data['menu'],
        price=data['price']
    )
    
    try:
        db.session.add(menu)
        db.session.commit()
        return jsonify({
            'message': '메뉴가 추가되었습니다.',
            'id': menu.id,
            'menu': menu.menu,
            'price': menu.price
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/stores/<int:store_id>/menus/<int:menu_id>', methods=['DELETE'])
@login_required
def delete_store_menu(store_id, menu_id):
    """가게 메뉴 삭제 (User 로그인 필요 - User가 Owner 역할)"""
    from models import Owner
    
    user = get_current_user()
    if not user:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    
    # User의 Owner 찾기
    owner = Owner.query.filter_by(owner_id=user.user_id).first()
    if not owner:
        return jsonify({'error': '가게 소유권이 없습니다.'}), 403
    
    # 가게 소유권 확인
    store = Store.query.get_or_404(store_id)
    if store.owner_id != owner.id:
        return jsonify({'error': '가게 소유권이 없습니다.'}), 403
    
    menu = Menu.query.filter_by(id=menu_id, store_id=store_id).first_or_404()
    
    try:
        db.session.delete(menu)
        db.session.commit()
        return jsonify({'message': '메뉴가 삭제되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/stores/<int:store_id>/payments', methods=['GET'])
def get_store_payments(store_id):
    """가게 결제 수단 목록 (여러 개 반환)"""
    from models import Store
    store = db.session.get(Store, store_id)
    if not store:
        return jsonify({'error': '가게를 찾을 수 없습니다.'}), 404
    
    # StorePayment 테이블에서 가게의 모든 지불방식 조회
    store_payments = StorePayment.query.filter_by(store_id=store_id).all()
    
    if not store_payments:
        # 하위 호환: 기존 payment_id가 있으면 반환
        if store.payment:
            return jsonify([{
                'id': store.payment.id,
                'payment': store.payment.payment
            }]), 200
        return jsonify([]), 200
    
    return jsonify([{
        'id': sp.payment.id,
        'payment': sp.payment.payment
    } for sp in store_payments]), 200

@bp.route('/stores/<int:store_id>/coupons', methods=['GET'])
def get_store_coupons(store_id):
    """가게 쿠폰 목록"""
    coupons = Coupon.query.filter_by(store_id=store_id, is_deleted=False).all()
    return jsonify([{
        'id': coupon.id,
        'period': coupon.period,
        'discount': coupon.discount
    } for coupon in coupons]), 200

@bp.route('/orders', methods=['GET'])
@login_required
def get_orders():
    """주문 목록 조회 (사용자 인증 필요)"""
    from models import Review
    
    user = get_current_user()
    if not user:
        return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
    
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.order_time.desc()).all()
    
    result = []
    for order in orders:
        # 해당 주문에 대해 사용자가 이미 리뷰를 작성했는지 확인 (order_id 기준)
        existing_review = Review.query.filter_by(
            user_id=user.id,
            order_id=order.id
        ).first()
        
        result.append({
            'id': order.id,
            'store_id': order.store_id,
            'store_name': order.store.store_name if order.store else None,
            'rider_id': order.rider_id,
            'order': order.order,
            'total_price': order.total_price,
            'order_time': order.order_time.isoformat() if order.order_time else None,
            'created_at': order.order_time.isoformat() if order.order_time else None,
            'has_review': existing_review is not None  # 리뷰 작성 여부 (주문별)
        })
    
    return jsonify(result), 200

@bp.route('/orders/waiting', methods=['GET'])
def get_waiting_orders():
    """대기 중인 주문 목록 조회 (라이더가 수락할 수 있는 주문)"""
    # rider_id가 None인 주문만 조회 (라이더가 수락하지 않은 주문)
    orders = Order.query.filter(Order.rider_id == None).order_by(Order.order_time.desc()).all()
    
    return jsonify([{
        'id': order.id,
        'store_id': order.store_id,
        'store_name': order.store.store_name if order.store else None,
        'user_id': order.user_id,
        'user_name': order.user.name if order.user else None,
        'user_address': order.user.address if order.user else None,
        'order': order.order,
        'total_price': order.total_price,
        'order_time': order.order_time.isoformat() if order.order_time else None
    } for order in orders]), 200

@bp.route('/orders/<int:order_id>/accept', methods=['POST'])
@login_required
def accept_order(order_id):
    """라이더가 주문 수락 (User가 라이더 역할)"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    
    order = Order.query.get_or_404(order_id)
    
    # 이미 다른 라이더가 수락한 주문인지 확인
    if order.rider_id:
        return jsonify({'error': '이미 수락된 주문입니다.'}), 400
    
    # User ID를 rider_id로 사용 (User가 라이더 역할)
    # Rider 테이블에 레코드가 없으면 생성
    from models import Rider
    rider = Rider.query.filter_by(rider_id=user.user_id).first()
    if not rider:
        # Rider 레코드 생성
        rider = Rider(
            rider_id=user.user_id,
            phone='',  # 기본값
            vehicle='자전거'  # 기본값
        )
        db.session.add(rider)
        db.session.flush()
    
    # 주문의 rider_id 업데이트
    order.rider_id = rider.id
    
    try:
        db.session.commit()
        return jsonify({'message': '주문을 수락했습니다.', 'order_id': order.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    """주문 생성 (사용자 인증 필요)"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
    
    data = request.get_json()
    
    if not all(k in data for k in ['store_id', 'order', 'total_price']):
        return jsonify({'error': '필수 필드가 누락되었습니다.'}), 400
    
    # 가게 존재 확인
    store = Store.query.get(data['store_id'])
    if not store:
        return jsonify({'error': '존재하지 않는 가게입니다.'}), 404
    
    # 주문 생성 시 rider_id는 None으로 설정 (라이더가 수락할 때 업데이트)
    # 라이더는 주문 생성 시 선택하지 않음
    order = Order(
        user_id=user.id,
        store_id=data['store_id'],
        rider_id=None,  # 라이더가 수락할 때까지 None으로 설정
        order=data['order'],
        total_price=data['total_price']
    )
    
    try:
        db.session.add(order)
        db.session.commit()
        return jsonify({'message': '주문이 생성되었습니다.', 'order_id': order.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 템플릿 라우트
@bp.route('/main')
def main():
    """메인 페이지"""
    return render_template('main.html')

@bp.route('/storelist')
def storelist():
    """가게 목록 페이지"""
    return render_template('storelist2.html')

@bp.route('/cart')
def cart():
    """장바구니 페이지"""
    return render_template('cart.html')

@bp.route('/orderlist')
def orderlist():
    """주문 목록 페이지"""
    return render_template('orderlist2.html')

@bp.route('/order')
def order():
    """주문/결제 페이지"""
    return render_template('payment.html')

