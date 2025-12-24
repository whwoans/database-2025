from flask import Blueprint, request, jsonify, render_template
from models import db, Category, User, Store, Menu, Coupon, Owner, Rider, Order, Review, FavoriteStore, Payment
from datetime import datetime

bp = Blueprint('admin', __name__)

@bp.route('/page')
def admin_page():
    """관리자 페이지"""
    return render_template('admin.html')

@bp.route('/categories/seed', methods=['POST'])
def seed_categories():
    """카테고리 기본 데이터 추가"""
    try:
        categories = [
            '한식',
            '중식',
            '일식',
            '양식',
            '분식',
            '패스트푸드'
        ]
        
        added = 0
        for cat_name in categories:
            existing = Category.query.filter_by(category=cat_name).first()
            if not existing:
                category = Category(category=cat_name)
                db.session.add(category)
                added += 1
        
        db.session.commit()
        return jsonify({'message': f'{added}개의 카테고리가 추가되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/categories/clear', methods=['DELETE'])
def clear_categories():
    """카테고리 전체 삭제"""
    try:
        # Category를 참조하는 Store 먼저 삭제 (Store의 자식들도 함께)
        Menu.query.delete()
        Coupon.query.delete()
        Payment.query.delete()
        Review.query.delete()
        FavoriteStore.query.delete()
        Order.query.delete()
        Store.query.delete()
        # 이제 Category 삭제 가능
        Category.query.delete()
        db.session.commit()
        return jsonify({'message': '모든 카테고리가 삭제되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/users/seed', methods=['POST'])
def seed_users():
    """테스트 사용자 추가"""
    try:
        users_data = [
            {'user_id': 'testuser1', 'passwd': 'test123', 'email': 'test1@test.com', 'name': '테스트 사용자1', 'address': '서울시 강남구'},
            {'user_id': 'testuser2', 'passwd': 'test123', 'email': 'test2@test.com', 'name': '테스트 사용자2', 'address': '서울시 서초구'},
            {'user_id': 'testuser3', 'passwd': 'test123', 'email': 'test3@test.com', 'name': '테스트 사용자3', 'address': '서울시 송파구'},
        ]
        
        added = 0
        for user_data in users_data:
            existing = User.query.filter_by(user_id=user_data['user_id']).first()
            if not existing:
                user = User(**user_data)
                user.set_password(user_data['passwd'])
                db.session.add(user)
                added += 1
        
        db.session.commit()
        return jsonify({'message': f'{added}개의 테스트 사용자가 추가되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/users/clear', methods=['DELETE'])
def clear_users():
    """사용자 전체 삭제"""
    try:
        # User를 참조하는 테이블들 먼저 삭제
        Order.query.delete()
        Review.query.delete()
        FavoriteStore.query.delete()
        # 이제 User 삭제 가능
        User.query.delete()
        db.session.commit()
        return jsonify({'message': '모든 사용자가 삭제되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/stores/seed', methods=['POST'])
def seed_stores():
    """테스트 가게 추가 - 카테고리별로 3개씩"""
    try:
        # Owner가 있는지 확인하고 없으면 생성
        owner = Owner.query.first()
        if not owner:
            # 테스트 Owner 생성
            owner = Owner(
                owner_id='testowner',
                email='owner@test.com',
                owner_passwd='test123'
            )
            owner.set_password('test123')
            db.session.add(owner)
            db.session.flush()
        
        # 모든 카테고리 가져오기
        categories = Category.query.all()
        if not categories:
            return jsonify({'error': '먼저 카테고리를 추가해주세요.'}), 400
        
        # 카테고리별 가게 데이터 (각 카테고리당 3개씩)
        store_templates = {
            '한식': [
                {'store_name': '맛있는 한식당', 'phone': '02-1234-5678', 'minprice': '15000원', 'operationTime': '09:00 - 22:00', 'closedDay': '월요일'},
                {'store_name': '전통 한식당', 'phone': '02-2345-6789', 'minprice': '18000원', 'operationTime': '10:00 - 21:00', 'closedDay': '화요일'},
                {'store_name': '고향 한식', 'phone': '02-3456-7890', 'minprice': '12000원', 'operationTime': '11:00 - 23:00', 'closedDay': '수요일'}
            ],
            '중식': [
                {'store_name': '중화반점', 'phone': '02-1111-2222', 'minprice': '20000원', 'operationTime': '10:00 - 21:00', 'closedDay': '화요일'},
                {'store_name': '만리장성', 'phone': '02-2222-3333', 'minprice': '18000원', 'operationTime': '11:00 - 22:00', 'closedDay': '수요일'},
                {'store_name': '차이나팰리스', 'phone': '02-3333-4444', 'minprice': '25000원', 'operationTime': '12:00 - 23:00', 'closedDay': '목요일'}
            ],
            '일식': [
                {'store_name': '일본라면', 'phone': '02-4444-5555', 'minprice': '12000원', 'operationTime': '11:00 - 23:00', 'closedDay': '수요일'},
                {'store_name': '스시마스터', 'phone': '02-5555-6666', 'minprice': '30000원', 'operationTime': '17:00 - 24:00', 'closedDay': '월요일'},
                {'store_name': '우동하우스', 'phone': '02-6666-7777', 'minprice': '15000원', 'operationTime': '10:00 - 22:00', 'closedDay': '화요일'}
            ],
            '양식': [
                {'store_name': '파스타하우스', 'phone': '02-7777-8888', 'minprice': '20000원', 'operationTime': '11:00 - 22:00', 'closedDay': '월요일'},
                {'store_name': '스테이크킹', 'phone': '02-8888-9999', 'minprice': '35000원', 'operationTime': '17:00 - 23:00', 'closedDay': '화요일'},
                {'store_name': '피자파라다이스', 'phone': '02-9999-0000', 'minprice': '18000원', 'operationTime': '12:00 - 24:00', 'closedDay': '수요일'}
            ],
            '분식': [
                {'store_name': '떡볶이천국', 'phone': '02-1010-2020', 'minprice': '10000원', 'operationTime': '09:00 - 22:00', 'closedDay': '월요일'},
                {'store_name': '순대킹', 'phone': '02-2020-3030', 'minprice': '12000원', 'operationTime': '10:00 - 21:00', 'closedDay': '화요일'},
                {'store_name': '김밥나라', 'phone': '02-3030-4040', 'minprice': '8000원', 'operationTime': '08:00 - 20:00', 'closedDay': '수요일'}
            ],
            '패스트푸드': [
                {'store_name': '버거월드', 'phone': '02-4040-5050', 'minprice': '15000원', 'operationTime': '10:00 - 23:00', 'closedDay': '없음'},
                {'store_name': '치킨헤븐', 'phone': '02-5050-6060', 'minprice': '18000원', 'operationTime': '16:00 - 02:00', 'closedDay': '없음'},
                {'store_name': '타코벨', 'phone': '02-6060-7070', 'minprice': '12000원', 'operationTime': '11:00 - 22:00', 'closedDay': '월요일'}
            ]
        }
        
        added = 0
        for category in categories:
            category_name = category.category
            # 카테고리에 해당하는 가게 템플릿 가져오기
            templates = store_templates.get(category_name, [])
            
            # 각 카테고리당 3개씩 가게 생성
            for i, template in enumerate(templates[:3]):
                store_name = template['store_name']
                # 이미 존재하는 가게인지 확인 (같은 이름이 있으면 스킵)
                existing = Store.query.filter_by(store_name=store_name).first()
                if existing:
                    continue
                
                # category_id로 Category 테이블에서 확인하고 category 필드에 자동으로 채우기
                store = Store(
                    owner_id=owner.id,
                    category_id=category.id,
                    category=category.category,  # Category 테이블에서 가져온 카테고리 이름
                    store_name=store_name,
                    phone=template['phone'],
                    minprice=template['minprice'],
                    operationTime=template['operationTime'],
                    closedDay=template['closedDay']
                )
                # 기본 지불방식 추가 (첫 번째 지불방식 사용)
                default_payment = Payment.query.filter_by(payment='만나서 카드결제').first()
                if not default_payment:
                    # 지불방식이 없으면 생성
                    default_payment = Payment(payment='만나서 카드결제')
                    db.session.add(default_payment)
                    db.session.flush()
                
                store.payment_id = default_payment.id
                db.session.add(store)
                added += 1
        
        db.session.commit()
        return jsonify({'message': f'{added}개의 테스트 가게가 추가되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/stores/clear', methods=['DELETE'])
def clear_stores():
    """가게 전체 삭제"""
    try:
        # Store를 참조하는 모든 테이블 먼저 삭제
        Menu.query.delete()
        Coupon.query.delete()
        Payment.query.delete()
        Review.query.delete()
        FavoriteStore.query.delete()
        Order.query.delete()
        # 이제 Store 삭제 가능
        Store.query.delete()
        db.session.commit()
        return jsonify({'message': '모든 가게가 삭제되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/menus/seed', methods=['POST'])
def seed_menus():
    """테스트 메뉴 추가 - 각 가게마다 카테고리에 맞는 메뉴 3개씩"""
    try:
        stores = Store.query.all()
        if not stores:
            return jsonify({'error': '먼저 가게를 추가해주세요.'}), 400
        
        # 카테고리별 메뉴 데이터
        menus_by_category = {
            '한식': [
                {'menu': '김치찌개', 'price': 8000},
                {'menu': '된장찌개', 'price': 7000},
                {'menu': '비빔밥', 'price': 9000},
                {'menu': '불고기', 'price': 12000},
                {'menu': '삼겹살', 'price': 15000}
            ],
            '중식': [
                {'menu': '짜장면', 'price': 6000},
                {'menu': '짬뽕', 'price': 8000},
                {'menu': '탕수육', 'price': 15000},
                {'menu': '양장피', 'price': 20000},
                {'menu': '마파두부', 'price': 7000}
            ],
            '일식': [
                {'menu': '라면', 'price': 5000},
                {'menu': '우동', 'price': 6000},
                {'menu': '돈까스', 'price': 10000},
                {'menu': '초밥세트', 'price': 25000},
                {'menu': '규동', 'price': 8000}
            ],
            '양식': [
                {'menu': '크림파스타', 'price': 12000},
                {'menu': '토마토파스타', 'price': 11000},
                {'menu': '리조또', 'price': 13000},
                {'menu': '스테이크', 'price': 30000},
                {'menu': '피자', 'price': 18000}
            ],
            '분식': [
                {'menu': '떡볶이', 'price': 4000},
                {'menu': '순대', 'price': 5000},
                {'menu': '김밥', 'price': 3000},
                {'menu': '튀김세트', 'price': 6000},
                {'menu': '어묵탕', 'price': 5000}
            ],
            '패스트푸드': [
                {'menu': '햄버거세트', 'price': 8000},
                {'menu': '치킨버거', 'price': 6000},
                {'menu': '치킨', 'price': 18000},
                {'menu': '타코', 'price': 5000},
                {'menu': '나쵸', 'price': 4000}
            ]
        }
        
        added = 0
        for store in stores:
            # 가게의 카테고리 가져오기
            category = db.session.get(Category, store.category_id)
            if not category:
                continue
            
            category_name = category.category
            # 카테고리에 맞는 메뉴 목록 가져오기
            category_menus = menus_by_category.get(category_name, [])
            
            # 각 가게당 최소 3개씩 메뉴 추가
            for menu_data in category_menus[:3]:
                existing = Menu.query.filter_by(store_id=store.id, menu=menu_data['menu']).first()
                if not existing:
                    menu = Menu(store_id=store.id, **menu_data)
                    db.session.add(menu)
                    added += 1
        
        db.session.commit()
        return jsonify({'message': f'{added}개의 테스트 메뉴가 추가되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/menus/clear', methods=['DELETE'])
def clear_menus():
    """메뉴 전체 삭제"""
    try:
        Menu.query.delete()
        db.session.commit()
        return jsonify({'message': '모든 메뉴가 삭제되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/coupons/seed', methods=['POST'])
def seed_coupons():
    """테스트 쿠폰 추가"""
    try:
        stores = Store.query.all()
        if not stores:
            return jsonify({'error': '먼저 가게를 추가해주세요.'}), 400
        
        added = 0
        for store in stores:
            coupons_data = [
                {'discount': 1000, 'period': 30},
                {'discount': 2000, 'period': 60},
                {'discount': 3000, 'period': 90},
            ]
            
            for coupon_data in coupons_data:
                existing = Coupon.query.filter_by(store_id=store.id, discount=coupon_data['discount']).first()
                if not existing:
                    coupon = Coupon(store_id=store.id, is_deleted=False, **coupon_data)
                    db.session.add(coupon)
                    added += 1
        
        db.session.commit()
        return jsonify({'message': f'{added}개의 테스트 쿠폰이 추가되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/coupons/clear', methods=['DELETE'])
def clear_coupons():
    """쿠폰 전체 삭제"""
    try:
        Coupon.query.delete()
        db.session.commit()
        return jsonify({'message': '모든 쿠폰이 삭제되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/reset', methods=['POST'])
def reset_all():
    """모든 데이터 초기화"""
    try:
        # 외래키 제약 때문에 순서 중요
        # Store를 참조하는 테이블들 먼저 삭제
        Menu.query.delete()
        Coupon.query.delete()
        Payment.query.delete()
        Review.query.delete()
        FavoriteStore.query.delete()
        Order.query.delete()
        
        # 이제 Store 삭제 가능
        Store.query.delete()
        
        # Category 삭제 (Store가 이미 삭제되었으므로 가능)
        Category.query.delete()
        
        # User 삭제 (Order, Review, FavoriteStore가 이미 삭제되었으므로 가능)
        User.query.delete()
        
        # Owner 삭제 (Store가 이미 삭제되었으므로 가능)
        Owner.query.delete()
        
        # Rider 삭제 (Order가 이미 삭제되었으므로 가능)
        Rider.query.delete()
        
        db.session.commit()
        return jsonify({'message': '모든 데이터가 초기화되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 직접 입력 생성 API
@bp.route('/categories/create', methods=['POST'])
def create_categories():
    """카테고리 직접 생성"""
    try:
        data = request.get_json()
        if not data or 'categories' not in data:
            return jsonify({'error': '카테고리 데이터가 필요합니다.'}), 400
        
        categories = data['categories']
        if not isinstance(categories, list) or len(categories) < 1:
            return jsonify({'error': '최소 1개 이상의 카테고리가 필요합니다.'}), 400
        
        added = 0
        for cat_name in categories:
            if not cat_name or not cat_name.strip():
                continue
            existing = Category.query.filter_by(category=cat_name.strip()).first()
            if not existing:
                category = Category(category=cat_name.strip())
                db.session.add(category)
                added += 1
        
        db.session.commit()
        return jsonify({'message': f'{added}개의 카테고리가 추가되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/users/create', methods=['POST'])
def create_users():
    """사용자 직접 생성"""
    try:
        data = request.get_json()
        if not data or 'users' not in data:
            return jsonify({'error': '사용자 데이터가 필요합니다.'}), 400
        
        users = data['users']
        if not isinstance(users, list) or len(users) < 1:
            return jsonify({'error': '최소 1개 이상의 사용자가 필요합니다.'}), 400
        
        added = 0
        for user_data in users:
            if not all(k in user_data for k in ['user_id', 'passwd', 'email', 'name', 'address']):
                continue
            
            existing = User.query.filter_by(user_id=user_data['user_id']).first()
            if not existing:
                user = User(
                    user_id=user_data['user_id'],
                    email=user_data['email'],
                    name=user_data['name'],
                    address=user_data['address']
                )
                user.set_password(user_data['passwd'])
                db.session.add(user)
                added += 1
        
        db.session.commit()
        return jsonify({'message': f'{added}개의 사용자가 추가되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/stores/create', methods=['POST'])
def create_stores():
    """가게 직접 생성"""
    try:
        data = request.get_json()
        if not data or 'stores' not in data:
            return jsonify({'error': '가게 데이터가 필요합니다.'}), 400
        
        stores = data['stores']
        if not isinstance(stores, list) or len(stores) < 1:
            return jsonify({'error': '최소 1개 이상의 가게가 필요합니다.'}), 400
        
        # Owner 확인/생성
        owner = Owner.query.first()
        if not owner:
            owner = Owner(
                owner_id='admin_owner',
                email='admin@admin.com',
                owner_passwd='admin123'
            )
            owner.set_password('admin123')
            db.session.add(owner)
            db.session.flush()
        
        from models import Payment
        
        added = 0
        for store_data in stores:
            # 필수 필드 검증 (모든 필드가 있어야 함)
            required_fields = ['store_name', 'category_id', 'phone', 'minprice', 'operationTime', 'closedDay', 'payment_id']
            if not all(k in store_data for k in required_fields):
                continue
            
            # 각 필드 값 검증
            if not store_data['store_name'] or not store_data['store_name'].strip():
                continue
            if not store_data['phone'] or not store_data['phone'].strip():
                continue
            if not store_data['minprice'] or not store_data['minprice'].strip():
                continue
            if not store_data['operationTime'] or not store_data['operationTime'].strip():
                continue
            if not store_data['closedDay'] or not store_data['closedDay'].strip():
                continue
            
            # 지불방식 검증
            payment_id = store_data.get('payment_id')
            if not payment_id:
                continue
            
            # 지불방식 ID가 유효한지 확인
            payment = db.session.get(Payment, payment_id)
            if not payment:
                # 존재하지 않는 지불방식 ID가 있으면 스킵
                continue
            
            # category_id로 Category 테이블에서 확인
            category = db.session.get(Category, store_data['category_id'])
            if not category:
                # 카테고리가 없으면 스킵
                continue
            
            existing = Store.query.filter_by(store_name=store_data['store_name']).first()
            if not existing:
                # category_id로 Category 테이블에서 확인하고 category 필드에 자동으로 채우기
                store = Store(
                    owner_id=owner.id,
                    category_id=store_data['category_id'],
                    payment_id=payment_id,
                    store_name=store_data['store_name'],
                    category=category.category,  # Category 테이블에서 가져온 카테고리 이름
                    phone=store_data['phone'],
                    minprice=store_data['minprice'],
                    operationTime=store_data['operationTime'],
                    closedDay=store_data['closedDay']
                )
                db.session.add(store)
                added += 1
        
        db.session.commit()
        return jsonify({'message': f'{added}개의 가게가 추가되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/menus/create', methods=['POST'])
def create_menus():
    """메뉴 직접 생성"""
    try:
        data = request.get_json()
        if not data or 'menus' not in data:
            return jsonify({'error': '메뉴 데이터가 필요합니다.'}), 400
        
        menus = data['menus']
        if not isinstance(menus, list) or len(menus) < 1:
            return jsonify({'error': '최소 1개 이상의 메뉴가 필요합니다.'}), 400
        
        added = 0
        for menu_data in menus:
            if not all(k in menu_data for k in ['store_id', 'menu', 'price']):
                continue
            
            # 가게 확인
            store = Store.query.get(menu_data['store_id'])
            if not store:
                continue
            
            existing = Menu.query.filter_by(store_id=menu_data['store_id'], menu=menu_data['menu']).first()
            if not existing:
                menu = Menu(
                    store_id=menu_data['store_id'],
                    menu=menu_data['menu'],
                    price=int(menu_data['price'])
                )
                db.session.add(menu)
                added += 1
        
        db.session.commit()
        return jsonify({'message': f'{added}개의 메뉴가 추가되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/coupons/create', methods=['POST'])
def create_coupons():
    """쿠폰 직접 생성"""
    try:
        data = request.get_json()
        if not data or 'coupons' not in data:
            return jsonify({'error': '쿠폰 데이터가 필요합니다.'}), 400
        
        coupons = data['coupons']
        if not isinstance(coupons, list) or len(coupons) < 1:
            return jsonify({'error': '최소 1개 이상의 쿠폰이 필요합니다.'}), 400
        
        added = 0
        for coupon_data in coupons:
            if not all(k in coupon_data for k in ['store_id', 'discount']):
                continue
            
            # 가게 확인
            store = Store.query.get(coupon_data['store_id'])
            if not store:
                continue
            
            coupon = Coupon(
                store_id=coupon_data['store_id'],
                discount=int(coupon_data['discount']),
                period=int(coupon_data.get('period', 30)),
                is_deleted=False
            )
            db.session.add(coupon)
            added += 1
        
        db.session.commit()
        return jsonify({'message': f'{added}개의 쿠폰이 추가되었습니다.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/categories', methods=['GET'])
def get_categories():
    """카테고리 목록 조회 (직접 입력 시 선택용)"""
    try:
        categories = Category.query.all()
        return jsonify([{
            'id': cat.id,
            'category': cat.category
        } for cat in categories]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/stores/list', methods=['GET'])
def get_stores_list():
    """가게 목록 조회 (직접 입력 시 선택용)"""
    try:
        stores = Store.query.all()
        return jsonify([{
            'id': store.id,
            'store_name': store.store_name,
            'category_id': store.category_id
        } for store in stores]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

