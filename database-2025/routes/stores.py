from flask import Blueprint, request, jsonify, render_template
from models import db, Store, Category, Owner, Payment, StorePayment, Review, Order
from utils.auth import login_required, get_current_user, owner_required, get_current_owner, verify_store_ownership

bp = Blueprint('stores', __name__)

@bp.route('/register', methods=['POST'])
@login_required
def register():
    """가게 등록 (User 로그인 필요 - User가 Owner 역할)"""
    from utils.auth import get_current_user
    
    user = get_current_user()
    if not user:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    
    data = request.get_json()
    
    # 필수 필드 검증 (모든 필드가 있어야 함)
    required_fields = ['category_id', 'store_name', 'phone', 'minprice', 'operationTime', 'closedDay', 'payment_ids']
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        return jsonify({'error': f'필수 필드가 누락되었습니다: {", ".join(missing_fields)}'}), 400
    
    # 각 필드 값 검증 (빈 문자열도 안 됨)
    if not data['store_name'] or not data['store_name'].strip():
        return jsonify({'error': '가게 이름을 입력해주세요.'}), 400
    if not data['phone'] or not data['phone'].strip():
        return jsonify({'error': '전화번호를 입력해주세요.'}), 400
    if not data['minprice'] or not data['minprice'].strip():
        return jsonify({'error': '최소주문금액을 입력해주세요.'}), 400
    if not data['operationTime'] or not data['operationTime'].strip():
        return jsonify({'error': '운영시간을 입력해주세요.'}), 400
    if not data['closedDay'] or not data['closedDay'].strip():
        return jsonify({'error': '휴무일을 입력해주세요.'}), 400
    
    # 지불방식 검증
    payment_ids = data.get('payment_ids', [])
    if not payment_ids or not isinstance(payment_ids, list) or len(payment_ids) == 0:
        return jsonify({'error': '최소 1개 이상의 지불방식을 선택해주세요.'}), 400
    
    # 지불방식 ID들이 유효한지 확인
    for payment_id in payment_ids:
        payment = db.session.get(Payment, payment_id)
        if not payment:
            return jsonify({'error': f'존재하지 않는 지불방식 ID: {payment_id}'}), 400
    
    # category_id로 Category 테이블에서 확인
    category = db.session.get(Category, data['category_id'])
    if not category:
        return jsonify({'error': '존재하지 않는 카테고리입니다.'}), 404
    
    # User ID를 owner_id로 사용 (User가 Owner 역할)
    # 먼저 Owner 레코드가 있는지 확인하고, 없으면 생성
    from models import Owner
    owner = Owner.query.filter_by(owner_id=user.user_id).first()
    if not owner:
        # Owner 레코드 생성 (User 정보 기반)
        owner = Owner(
            owner_id=user.user_id,
            email=user.email,
            owner_passwd=user.passwd  # 같은 비밀번호 사용
        )
        db.session.add(owner)
        db.session.flush()  # owner.id를 얻기 위해
    
    # category_id로 Category 테이블에서 확인하고 category 필드에 자동으로 채우기
    store = Store(
        owner_id=owner.id,
        category_id=data['category_id'],
        payment_id=payment_ids[0] if payment_ids else None,  # 하위 호환을 위해 첫 번째 payment_id 저장
        store_name=data['store_name'],
        category=category.category,  # Category 테이블에서 가져온 카테고리 이름
        phone=data['phone'],
        minprice=data['minprice'],
        reviewCount=0,
        operationTime=data['operationTime'],
        closedDay=data['closedDay'],
        information=data.get('information', '')  # 가게 정보 추가
    )
    
    try:
        db.session.add(store)
        db.session.flush()  # store.id를 얻기 위해
        
        # StorePayment 테이블에 여러 지불방식 저장
        for payment_id in payment_ids:
            store_payment = StorePayment(
                store_id=store.id,
                payment_id=payment_id
            )
            db.session.add(store_payment)
        
        db.session.commit()
        return jsonify({'message': '가게 등록이 완료되었습니다.', 'store_id': store.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/category/<int:category_id>', methods=['GET'])
def get_stores_by_category(category_id):
    """카테고리별 가게 목록"""
    stores = Store.query.filter_by(category_id=category_id).all()
    return jsonify([{
        'id': store.id,
        'store_name': store.store_name,
        'category': store.category,
        'phone': store.phone,
        'minprice': store.minprice,
        'reviewCount': store.reviewCount,
        'operationTime': store.operationTime,
        'closedDay': store.closedDay
    } for store in stores]), 200

@bp.route('/<int:store_id>', methods=['GET'])
def get_store(store_id):
    """가게 상세 정보"""
    from sqlalchemy import func
    
    store = Store.query.get_or_404(store_id)
    
    # 평균 별점 계산
    avg_rating_result = db.session.query(func.avg(Review.rating)).filter_by(store_id=store_id).scalar()
    avg_rating = round(avg_rating_result, 1) if avg_rating_result else 0.0
    
    # 주문 수 계산
    order_count = Order.query.filter_by(store_id=store_id).count()
    
    # 리뷰 수 계산 (실제 Review 테이블에서)
    review_count = Review.query.filter_by(store_id=store_id).count()
    
    return jsonify({
        'id': store.id,
        'owner_id': store.owner_id,
        'category_id': store.category_id,
        'store_name': store.store_name,
        'category': store.category,
        'phone': store.phone,
        'minprice': store.minprice,
        'reviewCount': review_count,  # 실제 리뷰 수
        'avgRating': avg_rating,  # 평균 별점
        'orderCount': order_count,  # 주문 수
        'operationTime': store.operationTime,
        'closedDay': store.closedDay,
        'information': store.information or '',  # 가게 정보 추가
        'created_at': store.created_at.isoformat()
    }), 200

@bp.route('/<int:store_id>', methods=['PUT'])
@login_required
def update_store(store_id):
    """가게 정보 수정"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    
    # Owner 찾기
    owner = Owner.query.filter_by(owner_id=user.user_id).first()
    if not owner:
        return jsonify({'error': '사장님 정보를 찾을 수 없습니다.'}), 404
    
    # 가게 찾기 및 소유권 확인
    store = Store.query.get_or_404(store_id)
    if store.owner_id != owner.id:
        return jsonify({'error': '가게 수정 권한이 없습니다.'}), 403
    
    data = request.get_json()
    
    # 필수 필드 검증
    required_fields = ['category_id', 'store_name', 'phone', 'minprice', 'operationTime', 'closedDay', 'payment_ids']
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        return jsonify({'error': f'필수 필드가 누락되었습니다: {", ".join(missing_fields)}'}), 400
    
    # 각 필드 값 검증
    if not data['store_name'] or not data['store_name'].strip():
        return jsonify({'error': '가게 이름을 입력해주세요.'}), 400
    if not data['phone'] or not data['phone'].strip():
        return jsonify({'error': '전화번호를 입력해주세요.'}), 400
    if not data['minprice'] or not data['minprice'].strip():
        return jsonify({'error': '최소주문금액을 입력해주세요.'}), 400
    if not data['operationTime'] or not data['operationTime'].strip():
        return jsonify({'error': '운영시간을 입력해주세요.'}), 400
    if not data['closedDay'] or not data['closedDay'].strip():
        return jsonify({'error': '휴무일을 입력해주세요.'}), 400
    
    # 지불방식 검증
    payment_ids = data.get('payment_ids', [])
    if not payment_ids or not isinstance(payment_ids, list) or len(payment_ids) == 0:
        return jsonify({'error': '최소 1개 이상의 지불방식을 선택해주세요.'}), 400
    
    # 지불방식 ID들이 유효한지 확인
    for payment_id in payment_ids:
        payment = db.session.get(Payment, payment_id)
        if not payment:
            return jsonify({'error': f'존재하지 않는 지불방식 ID: {payment_id}'}), 400
    
    # category_id로 Category 테이블에서 확인
    category = db.session.get(Category, data['category_id'])
    if not category:
        return jsonify({'error': '존재하지 않는 카테고리입니다.'}), 404
    
    # 가게 정보 업데이트
    store.category_id = data['category_id']
    store.category = category.category  # Category 테이블에서 가져온 카테고리 이름
    store.payment_id = payment_ids[0] if payment_ids else None  # 하위 호환을 위해 첫 번째 payment_id 저장
    store.store_name = data['store_name']
    store.phone = data['phone']
    store.minprice = data['minprice']
    store.operationTime = data['operationTime']
    store.closedDay = data['closedDay']
    store.information = data.get('information', '')  # 가게 정보 업데이트
    
    try:
        # 기존 StorePayment 레코드 삭제
        StorePayment.query.filter_by(store_id=store.id).delete()
        
        # 새로운 StorePayment 레코드 추가
        for payment_id in payment_ids:
            store_payment = StorePayment(
                store_id=store.id,
                payment_id=payment_id
            )
            db.session.add(store_payment)
        
        db.session.commit()
        return jsonify({'message': '가게 정보가 수정되었습니다.', 'store_id': store.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/owner/<int:user_id>', methods=['GET'])
def get_stores_by_owner(user_id):
    """사장별 가게 목록 (User ID로 조회)"""
    from models import User
    
    # User ID로 User 찾기
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
    
    # User의 user_id로 Owner 찾기
    owner = Owner.query.filter_by(owner_id=user.user_id).first()
    if not owner:
        # Owner가 없으면 빈 배열 반환
        return jsonify([]), 200
    
    # Owner의 가게 목록 조회
    stores = Store.query.filter_by(owner_id=owner.id).all()
    return jsonify([{
        'id': store.id,
        'store_name': store.store_name,
        'category_id': store.category_id,  # category_id 추가
        'category': store.category,
        'phone': store.phone,
        'minprice': store.minprice,
        'operationTime': store.operationTime,  # 운영시간 추가
        'closedDay': store.closedDay,  # 휴무일 추가
        'information': store.information or '',  # 가게 정보 추가
        'reviewCount': store.reviewCount
    } for store in stores]), 200

# 템플릿 라우트
@bp.route('/<int:store_id>/detail')
def store_detail(store_id):
    """가게 상세 페이지"""
    return render_template('storedetail.html', store_id=store_id)

