# ImageFX Selenium Automation

Selenium을 사용하여 Google ImageFX에서 이미지 프롬프트를 입력하고 생성된 이미지 4개를 자동으로 다운로드하는 Python 스크립트입니다.

## 주요 기능

- 🔌 **디버그 모드**: 기존 Chrome 브라우저에 연결하여 작업
- 📝 **자동 프롬프트 입력**: 텍스트 파일에서 프롬프트를 읽어 자동 입력
- 🖼️ **이미지 다운로드**: 생성된 이미지 4개를 자동으로 다운로드
- 📁 **체계적인 저장**: 타임스탬프와 프롬프트 기반으로 폴더 구조화
- 🔄 **배치 처리**: 여러 프롬프트를 순차적으로 처리 가능

## 사전 준비사항

### 1. Python 설치
- Python 3.8 이상 필요
- [Python 공식 웹사이트](https://www.python.org/downloads/)에서 다운로드

### 2. Chrome 브라우저 설치
- Google Chrome 브라우저가 설치되어 있어야 합니다
- [Chrome 다운로드](https://www.google.com/chrome/)

### 3. ChromeDriver 설치
- ChromeDriver는 Selenium Manager가 자동으로 관리하므로 별도 설치 불필요

### 4. Google 계정
- ImageFX 사용을 위해 Google 계정 로그인 필요

## 설치 방법

### 1. 저장소 클론
```bash
git clone <repository-url>
cd BB
```

### 2. 가상환경 생성 (선택사항이지만 권장)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

## 사용 방법

### Step 1: Chrome 디버그 모드로 실행

스크립트를 실행하기 **전에** 먼저 Chrome을 디버그 모드로 실행해야 합니다.

#### Windows
```cmd
# 명령 프롬프트 (cmd)
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=remote-profile

# PowerShell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=remote-profile
```

#### macOS
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=remote-profile
```

#### Linux
```bash
google-chrome --remote-debugging-port=9222 --user-data-dir=remote-profile
```

**중요 사항:**
- 디버그 모드로 실행하기 전에 **모든 Chrome 창을 닫아야** 합니다
- `--user-data-dir=remote-profile`은 별도의 프로필을 사용하여 기존 브라우저 설정과 분리합니다
- 포트 9222는 기본값이며, 필요시 다른 포트로 변경 가능합니다

### Step 2: 프롬프트 파일 준비

`prompts.txt` 파일을 생성하고 생성하고 싶은 이미지 프롬프트를 한 줄에 하나씩 입력합니다.

```txt
A serene mountain landscape at sunset with purple sky
A futuristic city with flying cars and neon lights
A cute cat wearing a wizard hat surrounded by magical sparkles
```

- `#`로 시작하는 줄은 주석으로 처리됩니다
- 빈 줄은 무시됩니다
- 파일이 없으면 대화형 모드로 프롬프트를 입력할 수 있습니다

### Step 3: 스크립트 실행

```bash
python imagefx_downloader.py
```

### Step 4: 진행 과정

1. **브라우저 연결**: 스크립트가 디버그 모드로 실행 중인 Chrome에 연결
2. **ImageFX 이동**: 자동으로 ImageFX 페이지로 이동
3. **로그인 대기**: Google 계정 로그인이 필요한 경우 수동으로 로그인 후 Enter 키 입력
4. **자동 처리**: 각 프롬프트에 대해:
   - 프롬프트 입력
   - 생성 버튼 클릭
   - 이미지 생성 대기 (최대 120초)
   - 생성된 이미지 4개 다운로드
5. **완료**: 모든 이미지가 `downloads/` 폴더에 저장됨

## 다운로드된 파일 구조

```
downloads/
├── 20260105_143022_A_serene_mountain_landscape/
│   ├── image_1.png
│   ├── image_2.png
│   ├── image_3.png
│   ├── image_4.png
│   └── metadata.json
├── 20260105_143155_A_futuristic_city_with_flying/
│   ├── image_1.png
│   ├── image_2.png
│   ├── image_3.png
│   ├── image_4.png
│   └── metadata.json
...
```

각 폴더는 다음을 포함합니다:
- `image_1.png ~ image_4.png`: 생성된 이미지 4개
- `metadata.json`: 프롬프트, 타임스탬프, 이미지 URL 등의 메타데이터

## 설정 옵션

`imagefx_downloader.py` 파일의 `main()` 함수에서 다음 설정을 변경할 수 있습니다:

```python
DEBUG_PORT = 9222           # Chrome 디버그 포트
DOWNLOAD_DIR = "downloads"  # 다운로드 폴더 경로
PROMPTS_FILE = "prompts.txt"  # 프롬프트 파일 경로
```

## 문제 해결

### 1. "Chrome 브라우저 연결 실패" 오류
**원인**: Chrome이 디버그 모드로 실행되지 않았거나 포트가 다름

**해결**:
- 모든 Chrome 창을 닫고 디버그 모드로 다시 실행
- 포트 번호가 일치하는지 확인
- 방화벽에서 해당 포트가 차단되지 않았는지 확인

### 2. "프롬프트 입력창을 찾을 수 없습니다" 오류
**원인**: ImageFX 페이지 구조가 변경되었거나 페이지가 완전히 로드되지 않음

**해결**:
- 스크립트가 안내하는 대로 수동으로 프롬프트 입력
- 페이지 로딩 시간을 늘려야 할 수 있음 (코드의 `time.sleep()` 값 증가)

### 3. "생성 버튼을 찾을 수 없습니다" 오류
**원인**: 페이지 구조 변경 또는 버튼이 아직 활성화되지 않음

**해결**:
- 수동으로 생성 버튼 클릭 후 계속 진행
- 스크립트가 프롬프트를 입력한 후 잠시 대기

### 4. 이미지 생성 타임아웃
**원인**: 서버가 느리거나 네트워크 문제

**해결**:
- `wait_for_images()` 함수의 `timeout` 값 증가
- 수동으로 생성 완료를 확인하고 Enter 키 입력

### 5. 이미지 다운로드 실패
**원인**: 네트워크 문제 또는 이미지 URL 접근 권한 문제

**해결**:
- 네트워크 연결 확인
- 브라우저에서 수동으로 이미지 다운로드 시도
- VPN 사용 시 비활성화 후 재시도

## 고급 사용법

### 대화형 모드
`prompts.txt` 파일이 없으면 대화형 모드로 실행됩니다:
```bash
python imagefx_downloader.py
```
프롬프트를 하나씩 입력하고, 빈 줄을 입력하면 처리 시작됩니다.

### 커스텀 다운로드 디렉토리
```python
downloader = ImageFXDownloader(debug_port=9222, download_dir="my_images")
```

### 단일 프롬프트 처리
코드를 수정하여 프로그래밍 방식으로 사용:
```python
from imagefx_downloader import ImageFXDownloader

downloader = ImageFXDownloader()
downloader.connect_to_browser()
downloader.navigate_to_imagefx()
downloader.process_prompt("A beautiful sunset over the ocean")
downloader.close()
```

## 주의사항

1. **Google 정책 준수**: ImageFX 서비스 약관을 준수하며 사용하세요
2. **API 제한**: 과도한 요청은 계정 제한을 초래할 수 있습니다
3. **로그인 상태**: 세션이 만료되면 수동으로 다시 로그인해야 합니다
4. **페이지 변경**: ImageFX 페이지 구조가 변경되면 스크립트 수정이 필요할 수 있습니다
5. **네트워크**: 안정적인 인터넷 연결이 필요합니다

## 라이선스

이 프로젝트는 교육 및 개인 용도로 제공됩니다. Google ImageFX의 이용 약관을 준수하여 사용하세요.

## 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

## 업데이트 내역

- **v1.0.0** (2026-01-05): 초기 릴리스
  - 디버그 모드 브라우저 연결
  - 자동 프롬프트 입력 및 이미지 생성
  - 이미지 다운로드 및 메타데이터 저장
  - 배치 처리 지원
