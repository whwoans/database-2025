# 배달 앱 백엔드 시스템

Flask 기반의 배달 앱 백엔드 시스템입니다. 사용자(고객), 사장, 라이더 3가지 역할을 지원하는 배달 플랫폼입니다.

## 🚀 시작하기

### 필수 요구사항
- Python 3.8 이상
- MySQL 8.0 이상
- pip

### 설치 방법

1. **저장소 클론 및 디렉토리 이동**
```bash
cd database
```

2. **가상환경 생성 및 활성화**
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
```

4. **환경 변수 설정**
`.env` 파일을 프로젝트 루트에 생성하고 다음 내용을 추가하세요:
```env
SECRET_KEY=your-secret-key-here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=test
DB_PORT=3306
```

또는 비밀번호가 없는 경우:
```env
SECRET_KEY=your-secret-key-here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=test
DB_PORT=3306
```

5. **애플리케이션 실행**
```bash
python app.py
```

서버가 `http://localhost:5001`에서 실행됩니다.

> **참고**: 애플리케이션 실행 시 데이터베이스와 테이블이 자동으로 생성되며, 기본 데이터(지불방식 2개, 카테고리 6개)가 자동으로 삽입됩니다.

## 📁 프로젝트 구조

```
database/
├── app.py                 # Flask 애플리케이션 메인 파일
├── config.py              # 데이터베이스 설정 파일
├── models.py              # SQLAlchemy 모델 정의
├── requirements.txt       # Python 패키지 의존성
├── create.sql            # 데이터베이스 스키마 및 기본 데이터
├── README.md             # 프로젝트 문서
├── FEATURES.md           # 기능 목록 문서
├── routes/               # 라우터 Blueprint
│   ├── __init__.py
│   ├── users.py          # 사용자 라우터
│   ├── owners.py         # 사장 라우터
│   ├── riders.py         # 라이더 라우터
│   ├── stores.py         # 가게 라우터
│   ├── customer.py       # 고객 라우터
│   ├── favorites.py      # 찜하기 라우터
│   ├── reviews.py        # 리뷰 라우터
│   ├── payments.py       # 결제수단 라우터
│   ├── coupons.py        # 쿠폰 라우터
│   └── admin.py          # 관리자 라우터
├── templates/            # Jinja2 템플릿
│   ├── firstpage.html    # 첫 페이지 (로그인/회원가입)
│   ├── signup.html       # 회원가입 페이지
│   ├── main.html         # 메인 페이지 (카테고리별 가게 목록)
│   ├── storelist2.html   # 가게 목록 페이지
│   ├── storedetail.html  # 가게 상세 페이지
│   ├── cart.html         # 장바구니 페이지
│   ├── order.html        # 주문 내역 페이지
│   ├── orderlist2.html   # 주문 목록 페이지
│   ├── like.html         # 찜 목록 페이지
│   ├── payment.html      # 결제 페이지
│   ├── owner.html        # 사장님 페이지
│   ├── rider.html        # 라이더 페이지
│   ├── setting.html      # 설정 페이지
│   └── admin.html        # 관리자 페이지
└── utils/                # 유틸리티 함수
    └── auth.py           # 인증 관련 함수 (login_required, owner_required 등)
```

## 📋 주요 기능

### 사용자 (User)
- 회원가입/로그인
- 사용자 정보 조회 및 수정
- 주소 수정
- 세션 기반 인증

### 사장 (Owner)
- 사장 회원가입/로그인
- 가게 등록 및 수정
- 메뉴 관리 (추가/삭제)
- 리뷰 조회 및 삭제
- 지불방식 선택
- 카테고리 선택

### 라이더 (Rider)
- 라이더 등록
- 라이더 정보 조회

### 고객 (Customer)
- 카테고리별 가게 목록 조회
- 가게 상세 정보 조회
- 메뉴 조회
- 장바구니 기능
- 주문 생성 및 조회
- 주문 내역 확인
- 리뷰 작성
- 찜하기 기능

### 관리자 (Admin)
- 카테고리 관리 (생성, 삭제, 초기화)
- 사용자 관리 (생성, 삭제, 초기화)
- 가게 관리 (생성, 삭제, 초기화)
- 메뉴 관리 (생성, 삭제, 초기화)
- 쿠폰 관리 (생성, 삭제, 초기화)
- 테스트 데이터 생성 (seed)
- 전체 데이터 초기화

### 기타 기능
- 찜하기 (Favorite Store)
- 리뷰 작성 및 조회
- 지불방식 관리 (Payment)
- 쿠폰 관리 (Coupon)
- 세션 유효성 검사 미들웨어

## 🗄️ 데이터베이스 구조

### 기본 데이터
애플리케이션 실행 시 자동으로 삽입되는 기본 데이터:

**지불방식 (Payment)**
- 만나서 카드결제
- 만나서 현금 결제

**카테고리 (Category)**
- 한식
- 일식
- 중식
- 양식
- 분식
- 패스트푸드

### 주요 테이블
- `user` - 사용자 정보
- `owner` - 사장 정보
- `rider` - 라이더 정보
- `store` - 가게 정보
- `category` - 카테고리 정보
- `payment` - 지불방식 정보
- `menu` - 메뉴 정보
- `order` - 주문 정보
- `review` - 리뷰 정보
- `favorite_store` - 찜하기 정보
- `coupon` - 쿠폰 정보

## 🔌 주요 API 엔드포인트

### 사용자 관련
- `POST /users/register` - 회원가입
- `POST /users/login` - 로그인
- `GET /users/me` - 현재 사용자 정보 조회
- `GET /users/setting` - 설정 페이지
- `POST /users/check-id` - 아이디 중복 확인

### 고객 관련
- `GET /customer/categories` - 카테고리 목록
- `GET /customer/categories/{category_id}/stores` - 카테고리별 가게 목록
- `GET /customer/stores/{store_id}` - 가게 상세 정보
- `GET /customer/stores/{store_id}/menus` - 가게 메뉴 목록
- `GET /customer/stores/{store_id}/payments` - 가게 지불방식 목록
- `GET /customer/payment-methods` - 모든 지불방식 목록
- `POST /customer/orders` - 주문 생성
- `GET /customer/orders` - 주문 목록 조회

### 가게 관련
- `POST /stores/register` - 가게 등록
- `PUT /stores/{store_id}` - 가게 정보 수정
- `GET /stores/owner/{user_id}` - 사장별 가게 목록

### 찜하기 관련
- `POST /favorites` - 찜하기 추가
- `DELETE /favorites/{favorite_id}` - 찜하기 삭제
- `GET /favorites/page` - 찜 목록 페이지

### 리뷰 관련
- `POST /reviews` - 리뷰 작성
- `GET /reviews/store/{store_id}` - 가게별 리뷰 목록
- `GET /reviews/order/{order_id}` - 주문별 리뷰 작성 페이지

### 관리자 관련
- `GET /admin/page` - 관리자 페이지
- `POST /admin/categories/create` - 카테고리 생성
- `POST /admin/users/create` - 사용자 생성
- `POST /admin/stores/create` - 가게 생성
- `POST /admin/menus/create` - 메뉴 생성
- `POST /admin/coupons/create` - 쿠폰 생성
- `POST /admin/categories/seed` - 카테고리 테스트 데이터 생성
- `POST /admin/users/seed` - 사용자 테스트 데이터 생성
- `POST /admin/stores/seed` - 가게 테스트 데이터 생성
- `POST /admin/menus/seed` - 메뉴 테스트 데이터 생성
- `POST /admin/coupons/seed` - 쿠폰 테스트 데이터 생성
- `POST /admin/reset` - 전체 데이터 초기화

## 🛠️ 기술 스택

- **프레임워크**: Flask 3.0.0
- **데이터베이스**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0.44
- **템플릿 엔진**: Jinja2 3.1.2
- **인증**: Flask Session 기반
- **데이터베이스 드라이버**: PyMySQL 1.1.0
- **환경 변수 관리**: python-dotenv 1.0.0

## 🔒 보안 기능

- 세션 기반 인증
- 비밀번호 해싱 (Werkzeug)
- 세션 유효성 검사 미들웨어 (사용자/사장 삭제 시 자동 로그아웃)
- 로그인 필요 경로 보호 (`@login_required` 데코레이터)
- 사장 권한 검증 (`@owner_required` 데코레이터)

## 📝 주요 특징

1. **자동 데이터베이스 초기화**: 앱 실행 시 데이터베이스와 테이블이 자동으로 생성됩니다.
2. **기본 데이터 자동 삽입**: 지불방식 2개와 카테고리 6개가 자동으로 삽입됩니다.
3. **세션 유효성 검사**: 모든 요청 전에 세션의 사용자/사장 정보가 실제로 존재하는지 확인합니다.
4. **관리자 기능**: 웹 인터페이스를 통한 데이터 관리 및 테스트 데이터 생성 기능을 제공합니다.
5. **카테고리별 정렬**: 가게 목록을 리뷰 수, 평균 별점, 주문 수로 정렬할 수 있습니다.

## 🐛 문제 해결

### 데이터베이스 연결 실패
- MySQL 서버가 실행 중인지 확인하세요.
- `.env` 파일의 `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`이 올바른지 확인하세요.
- 데이터베이스가 생성되어 있는지 확인하세요.

### 포트 충돌
- 기본 포트는 5001입니다. 다른 포트를 사용하려면 환경 변수 `PORT`를 설정하세요.

### 기본 데이터가 없을 때
- 앱을 재시작하면 자동으로 기본 데이터가 삽입됩니다.
- 또는 관리자 페이지에서 수동으로 데이터를 생성할 수 있습니다.

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.
