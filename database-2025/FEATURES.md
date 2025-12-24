# 프로젝트 기능 목록

## 📋 개요
배달 앱 백엔드 시스템으로, 사용자(고객), 사장, 라이더 3가지 역할을 지원하는 배달 플랫폼입니다.

---

## 👤 1. 사용자 (User) 기능
**라우터**: `/users`

### API 엔드포인트
- `POST /users/register` - 회원가입
- `POST /users/login` - 로그인
- `GET /users/{user_id}` - 사용자 정보 조회
- `POST /users/modify/address` - 주소 수정

### 템플릿 페이지
- `firstpage.html` - 로그인/회원가입 첫 페이지
- `signup.html` - 회원가입 페이지

### 주요 기능
- 회원가입 (아이디, 비밀번호, 이메일, 이름, 주소)
- 로그인 인증
- 주소 수정
- 아이디 중복 확인 (서비스 레이어에 구현됨)

---

## 🏪 2. 가게 (Store) 기능
**라우터**: `/stores`

### API 엔드포인트
- `POST /stores/register` - 가게 등록 (사장 인증 필요)
- `GET /stores/category/{category_id}` - 카테고리별 가게 목록
- `GET /stores/{store_id}` - 가게 상세 정보
- `GET /stores/owner/{owner_id}` - 사장별 가게 목록

### 템플릿 페이지
- `storedetail.html` - 가게 상세 페이지

### 주요 기능
- 가게 등록 (사장 인증 후)
- 카테고리별 가게 조회
- 가게 상세 정보 조회
- 사장별 가게 목록 조회

---

## 👨‍💼 3. 사장 (Owner) 기능
**라우터**: `/owners`

### API 엔드포인트
- `POST /owners/register` - 사장 회원가입
- `POST /owners/login` - 사장 로그인
- `GET /owners/{owner_id}` - 사장 정보 조회

### 템플릿 페이지
- `owner.html` - 사장 페이지

### 주요 기능
- 사장 회원가입
- 사장 로그인
- 사장 정보 조회

---

## 🛵 4. 라이더 (Rider) 기능
**라우터**: `/riders`

### API 엔드포인트
- `POST /riders/register` - 라이더 등록
- `GET /riders/{rider_id}` - 라이더 정보 조회

### 템플릿 페이지
- `rider.html` - 라이더 페이지

### 주요 기능
- 라이더 등록
- 라이더 정보 조회

---

## 🛒 5. 고객 (Customer) 기능
**라우터**: `/customer`

### API 엔드포인트
- `GET /customer/categories` - 모든 카테고리 조회
- `GET /customer/categories/{category_id}/stores` - 카테고리별 가게 목록
- `GET /customer/stores/{store_id}/menus` - 가게 메뉴 목록
- `GET /customer/stores/{store_id}/payments` - 가게 결제 수단 목록
- `GET /customer/stores/{store_id}/coupons` - 가게 쿠폰 목록
- `POST /customer/orders` - 주문 생성 (사용자 인증 필요)

### 템플릿 페이지
- `main.html` - 메인 페이지
- `storelist2.html` - 가게 목록 페이지
- `orderlist2.html` - 주문 목록 페이지
- `order.html` - 주문 페이지

### 주요 기능
- 카테고리 조회
- 가게 목록 조회
- 메뉴 조회
- 결제 수단 조회
- 쿠폰 조회
- 주문 생성

---

## ❤️ 6. 찜하기 (Favorite) 기능
**라우터**: `/favorites`

### API 엔드포인트
- `POST /favorites` - 찜하기 추가 (사용자 인증 필요)
- `DELETE /favorites/{store_id}` - 찜하기 제거 (사용자 인증 필요)
- `GET /favorites` - 찜한 가게 목록 (사용자 인증 필요)

### 템플릿 페이지
- `like.html` - 찜한 가게 목록 페이지

### 주요 기능
- 가게 찜하기 추가
- 찜하기 제거
- 찜한 가게 목록 조회

---

## ⭐ 7. 리뷰 (Review) 기능
**라우터**: `/reviews`

### API 엔드포인트
- `POST /reviews` - 리뷰 작성 (사용자 인증 필요)
- `GET /reviews/store/{store_id}` - 가게 리뷰 목록

### 주요 기능
- 리뷰 작성 (평점, 내용)
- 가게별 리뷰 조회

---

## 💳 8. 결제 수단 (Payment) 기능
**라우터**: `/payments`

### API 엔드포인트
- `POST /payments/store/{store_id}` - 결제 수단 추가 (사장 인증 + 소유권 확인)
- `DELETE /payments/store/{store_id}/{payment_id}` - 결제 수단 제거 (사장 인증 + 소유권 확인)
- `GET /payments/store/{store_id}` - 가게 결제 수단 목록

### 템플릿 페이지
- `payment.html` - 결제 페이지

### 주요 기능
- 결제 수단 추가 (카드, 현금 등)
- 결제 수단 제거
- 가게별 결제 수단 조회

---

## 🎫 9. 쿠폰 (Coupon) 기능
**라우터**: `/coupons`

### API 엔드포인트
- `POST /coupons/store/{store_id}` - 쿠폰 생성 (사장 인증 + 소유권 확인)
- `GET /coupons/store/{store_id}` - 가게 쿠폰 목록
- `DELETE /coupons/store/{store_id}/{coupon_id}` - 쿠폰 삭제 (사장 인증 + 소유권 확인)

### 주요 기능
- 쿠폰 생성 (할인율, 기간)
- 쿠폰 목록 조회
- 쿠폰 삭제

---

## 📊 데이터베이스 모델

### 주요 엔티티
1. **User** - 사용자 (고객)
2. **Owner** - 사장
3. **Rider** - 라이더
4. **Store** - 가게
5. **Category** - 카테고리
6. **Menu** - 메뉴
7. **Order** - 주문
8. **Review** - 리뷰
9. **Favorite_store** - 찜한 가게
10. **Payment** - 결제 수단
11. **Coupon** - 쿠폰

---

## 🔐 인증 및 권한

### 사용자 인증
- 회원가입/로그인을 통한 사용자 인증
- 대부분의 기능에서 사용자 인증 필요

### 사장 인증
- 사장 회원가입/로그인
- 가게 등록, 결제 수단 관리, 쿠폰 관리 시 사장 인증 + 소유권 확인 필요

---

## 📄 템플릿 페이지 목록

1. `firstpage.html` - 로그인/회원가입 첫 페이지
2. `signup.html` - 회원가입 페이지
3. `main.html` - 메인 페이지
4. `storelist2.html` - 가게 목록 페이지
5. `storedetail.html` - 가게 상세 페이지
6. `order.html` - 주문 페이지
7. `orderlist2.html` - 주문 목록 페이지
8. `like.html` - 찜한 가게 목록 페이지
9. `payment.html` - 결제 페이지
10. `owner.html` - 사장 페이지
11. `rider.html` - 라이더 페이지
12. `setting.html` - 설정 페이지

---

## 🛠️ 기술 스택

- **프레임워크**: FastAPI (현재 Flask로 전환 중)
- **데이터베이스**: MySQL 8.0
- **ORM**: SQLAlchemy
- **템플릿 엔진**: Jinja2
- **데이터 검증**: Pydantic
- **컨테이너**: Docker & Docker Compose

---

## 📝 총 API 엔드포인트 수: 30개

### 역할별 분류
- **사용자**: 4개
- **사장**: 3개
- **라이더**: 2개
- **가게**: 4개
- **고객**: 6개
- **찜하기**: 3개
- **리뷰**: 2개
- **결제 수단**: 3개
- **쿠폰**: 3개

