# 멀티턴 LLM 챗봇 예제

## 1. 개요

아래 추가 조건을 만족하는 멀티턴 LLM 챗봇을 구현한다.

### 추가조건

1. 대화내역을 DB에 저장한다.
   - 해당 프로젝트에서는 `postgre` DB를 사용한다.
2. 멀티턴이 가능하다.
3. 멀티턴의 `window_size`를 조절할 수 있다.
   - 기존에 대화내역에서 최대 `window_size` 만큼만 대화내역만 사용한다.
4. 멀티턴 context 초기화가 가능하다.
   - 초기화를 진행하면 `.env`의 `CONTEXT_REFRESH_AI_MESSAGE`가 기록되며 LLM에게 기존의 히스토리를 더 이상 전달하지 않는다.
   - 초기화 후 대화를 다시 누적하면 최대 `window_size` 만큼 대화내역을 다시 누적하여 사용한다.
5. 대화내역을 n개 테이블로 샤딩하여 관리한다.
   - 이 부분은 아래 [테이블 구조](#2-테이블-구조)에서 자세히 설명한다.

## 2. 테이블 구조

기존 Langchain에서 구현하는 `BaseChatMessageHistory` 구현체들의 예시는 "message_store" 생성하여 대화내역을 저장하도록 세팅되어 있다.

- [구현체 코드 예시](https://python.langchain.com/v0.2/api_reference/_modules/langchain_community/chat_message_histories/postgres.html#PostgresChatMessageHistory.__init__)

한 테이블에서 관리하는 것이 조금 버거울 수 있겠다는 생각에 테이블을 유저 식별자로 파티셔닝하여 관리하는 방식을 생각해 보았다.
`수평(Horizontal) 분할`을 하여 기간별로 새로운 테이블을 가지게 되면 대화내역이 이어지는 것에 곤란함이 있을 것 같다고 생각했다.
따라서 `수직(Vertical) 분할`을 하는 것으로 결정했다. (유저 식별자가 바뀌지 않을수록 수직 분할의 장점이 생긴다.)

유저 식별자를 해싱하여 파티셔닝하는 작업은 서비스마다 다를 것이다.

해당 프로젝트에서는 유저 이메일 주소가 식별자라 첫글자로 간단하게 해싱했다.

- [프로젝트에서 구현한 해싱함수 예시](tablename_hasher.py)

## 3. 동작 테스트

### 1) 가상환경 세팅 (poetry 사용)

```shell
poetry install
```

### 2) Database 생성 및 .env 세팅
[.env_sample](.env_sample) 참고

### 3) 프로젝트 실행

```shell
python -m uvicorn main:app --reload
```

### 4) 테스트

1. api로 request -> [api request 예시](./test-request/request.http)
2. langserver 로 runnable 서빙 -> [stream request 예시](./test-request/langserve.http) 

