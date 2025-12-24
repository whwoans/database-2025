import os
import pymysql
from flask import Flask
from config import DB_CONFIG
from models import db
from routes import users, owners, riders, stores, customer, favorites, reviews, payments, coupons, admin

def create_app():
    app = Flask(__name__)
    
    # SECRET_KEY 설정 (세션을 위해 필요)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 데이터베이스 URI 구성
    db_port = os.environ.get('DB_PORT', '3306')
    # 비밀번호가 있는 경우와 없는 경우를 처리
    if DB_CONFIG['password']:
        db_uri = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{db_port}/{DB_CONFIG['database']}"
    else:
        db_uri = f"mysql+pymysql://{DB_CONFIG['user']}@{DB_CONFIG['host']}:{db_port}/{DB_CONFIG['database']}"
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    
    # 데이터베이스 초기화
    db.init_app(app)
    
    # Blueprint 등록
    app.register_blueprint(users.bp, url_prefix='/users')
    app.register_blueprint(owners.bp, url_prefix='/owners')
    app.register_blueprint(riders.bp, url_prefix='/riders')
    app.register_blueprint(stores.bp, url_prefix='/stores')
    app.register_blueprint(customer.bp, url_prefix='/customer')
    app.register_blueprint(favorites.bp, url_prefix='/favorites')
    app.register_blueprint(reviews.bp, url_prefix='/reviews')
    app.register_blueprint(payments.bp, url_prefix='/payments')
    app.register_blueprint(coupons.bp, url_prefix='/coupons')
    app.register_blueprint(admin.bp, url_prefix='/admin')
    
    # Middleware: 세션 유효성 검사
    @app.before_request
    def validate_session():
        """모든 요청 전에 세션의 사용자/사장 정보가 실제로 존재하는지 확인"""
        from flask import session, request
        from models import User, Owner
        
        # 체크하지 않을 경로들
        excluded_paths = [
            '/users/login',
            '/users/register',
            '/users/check-id',
            '/users/firstpage',
            '/users/signup',
            '/owners/login',
            '/owners/register',
            '/admin/page',
            '/admin/categories/seed',
            '/admin/users/seed',
            '/admin/stores/seed',
            '/admin/menus/seed',
            '/admin/coupons/seed',
            '/admin/categories/clear',
            '/admin/users/clear',
            '/admin/stores/clear',
            '/admin/menus/clear',
            '/admin/coupons/clear',
            '/admin/reset',
            '/admin/categories',
            '/admin/stores/list',
            '/admin/categories/create',
            '/admin/users/create',
            '/admin/stores/create',
            '/admin/menus/create',
            '/admin/coupons/create',
        ]
        
        # 제외된 경로는 체크하지 않음
        if any(request.path.startswith(path) for path in excluded_paths):
            return None
        
        # 세션에 user_id가 있으면 실제 User가 존재하는지 확인
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if not user:
                # User가 삭제되었으면 세션 클리어
                session.pop('user_id', None)
                print(f"⚠️ 세션에 저장된 user_id({user_id})에 해당하는 User가 없어 세션을 클리어했습니다.")
        
        # 세션에 owner_id가 있으면 실제 Owner가 존재하는지 확인
        owner_id = session.get('owner_id')
        if owner_id:
            owner = Owner.query.get(owner_id)
            if not owner:
                # Owner가 삭제되었으면 세션 클리어
                session.pop('owner_id', None)
                print(f"⚠️ 세션에 저장된 owner_id({owner_id})에 해당하는 Owner가 없어 세션을 클리어했습니다.")
        
        return None
    
    # 루트 경로 - 첫 페이지로 리다이렉트
    @app.route('/')
    def index():
        from flask import redirect
        return redirect('/users/firstpage')
    
    # 데이터베이스가 없으면 자동 생성
    db_name = DB_CONFIG['database']
    try:
        # 데이터베이스 없이 연결 (데이터베이스 생성용)
        if DB_CONFIG['password']:
            conn = pymysql.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                port=int(db_port),
                charset='utf8mb4'
            )
        else:
            conn = pymysql.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                port=int(db_port),
                charset='utf8mb4'
            )
        
        with conn.cursor() as cursor:
            # 데이터베이스가 없으면 생성
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci")
            print(f"✅ 데이터베이스 '{db_name}' 확인/생성 완료")
        conn.close()
    except Exception as e:
        print(f"⚠️ 데이터베이스 생성 시도 중 오류 (이미 존재할 수 있음): {e}")
    
    # 데이터베이스 테이블 생성 (연결 실패 시 에러 메시지 표시)
    with app.app_context():
        try:
            db.create_all()
            print(f"✅ 데이터베이스 연결 성공: {DB_CONFIG['host']}:{db_port}/{DB_CONFIG['database']}")
            
            # 기본 데이터 삽입 (지불방식, 카테고리)
            from models import Payment, Category
            
            # 지불방식 기본 데이터 확인 및 삽입
            if Payment.query.count() == 0:
                payment1 = Payment(payment='만나서 카드결제')
                payment2 = Payment(payment='만나서 현금 결제')
                db.session.add(payment1)
                db.session.add(payment2)
                db.session.commit()
                print("✅ 기본 지불방식 데이터 삽입 완료 (만나서 카드결제, 만나서 현금 결제)")
            
            # 카테고리 기본 데이터 확인 및 삽입
            if Category.query.count() == 0:
                categories = ['한식', '일식', '중식', '양식', '분식', '패스트푸드']
                for cat_name in categories:
                    category = Category(category=cat_name)
                    db.session.add(category)
                db.session.commit()
                print("✅ 기본 카테고리 데이터 삽입 완료 (한식, 일식, 중식, 양식, 분식, 패스트푸드)")
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            print(f"   호스트: {DB_CONFIG['host']}")
            print(f"   사용자: {DB_CONFIG['user']}")
            print(f"   데이터베이스: {DB_CONFIG['database']}")
            print("\n💡 해결 방법:")
            print("   1. MySQL 서버가 실행 중인지 확인하세요")
            print("   2. .env 파일의 DB_HOST가 'localhost'로 설정되어 있는지 확인하세요")
            print("   3. 데이터베이스가 생성되어 있는지 확인하세요")
            raise
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5001))  # 기본값을 5001로 변경
    app.run(debug=True, host='0.0.0.0', port=port)

