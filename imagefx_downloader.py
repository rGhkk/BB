"""
ImageFX Selenium Automation Script
디버깅 모드로 기존 Chrome 브라우저에 연결하여 ImageFX에서 이미지를 생성하고 다운로드합니다.
"""

import os
import time
import json
import base64
import hashlib
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests


class ImageFXDownloader:
    def __init__(self, debug_port=9222, download_dir="downloads"):
        """
        ImageFX 다운로더 초기화

        Args:
            debug_port: Chrome 디버그 포트 (기본값: 9222)
            download_dir: 이미지 저장 디렉토리 (기본값: downloads)
        """
        self.debug_port = debug_port
        self.download_dir = download_dir
        self.driver = None

        # 다운로드 디렉토리 생성
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            print(f"✅ 다운로드 디렉토리 생성: {download_dir}")

    def connect_to_browser(self):
        """디버그 모드로 실행 중인 Chrome 브라우저에 연결"""
        try:
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.debug_port}")

            self.driver = webdriver.Chrome(options=chrome_options)
            print(f"✅ Chrome 브라우저 연결 성공 (포트: {self.debug_port})")
            return True
        except Exception as e:
            print(f"❌ Chrome 브라우저 연결 실패: {e}")
            print(f"\n💡 Chrome을 다음 명령어로 실행했는지 확인하세요:")
            print(f"   Windows: chrome.exe --remote-debugging-port={self.debug_port}")
            print(f"   Mac: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port={self.debug_port}")
            print(f"   Linux: google-chrome --remote-debugging-port={self.debug_port}")
            return False

    def navigate_to_imagefx(self):
        """ImageFX 페이지로 이동"""
        try:
            imagefx_url = "https://aitestkitchen.withgoogle.com/tools/image-fx"
            print(f"\n🌐 ImageFX 페이지로 이동: {imagefx_url}")
            self.driver.get(imagefx_url)
            time.sleep(3)  # 페이지 로딩 대기
            print("✅ ImageFX 페이지 로드 완료")
            return True
        except Exception as e:
            print(f"❌ ImageFX 페이지 로드 실패: {e}")
            return False

    def enter_prompt(self, prompt):
        """프롬프트 입력"""
        try:
            print(f"\n📝 프롬프트 입력: {prompt}")

            # contenteditable div 찾기 (ImageFX는 div를 사용)
            input_element = None
            try:
                # contenteditable div 찾기
                input_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[contenteditable='true']"))
                )
                print(f"✅ 입력창 찾음 (contenteditable div)")
            except TimeoutException:
                print("❌ 프롬프트 입력창을 찾을 수 없습니다.")
                print("💡 수동으로 프롬프트를 입력하려면 아래 안내를 따르세요:")
                print(f"   1. 브라우저에서 ImageFX 프롬프트 입력창을 찾으세요")
                print(f"   2. 다음 프롬프트를 입력하세요: {prompt}")
                print(f"   3. 생성 버튼을 클릭하세요")
                input("   4. Enter를 눌러 계속하세요...")
                return True

            # 스크롤하여 요소를 화면에 표시
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_element)
            time.sleep(0.5)

            # 포커스 주기
            self.driver.execute_script("arguments[0].focus();", input_element)
            time.sleep(0.3)

            # 기존 내용 전체 선택 후 삭제
            input_element.click()
            time.sleep(0.3)

            # Ctrl+A로 전체 선택
            from selenium.webdriver.common.keys import Keys
            input_element.send_keys(Keys.CONTROL + "a")
            time.sleep(0.2)

            # 삭제
            input_element.send_keys(Keys.DELETE)
            time.sleep(0.5)

            # 프롬프트 입력 (send_keys 사용 - 가장 확실한 방법)
            input_element.send_keys(prompt)
            time.sleep(2)

            # 입력 완료를 위한 클릭 (focus 유지)
            input_element.click()
            time.sleep(0.5)

            # 입력 확인
            current_text = self.driver.execute_script("return arguments[0].textContent;", input_element)
            if prompt in current_text:
                print("✅ 프롬프트 입력 완료")
                return True
            else:
                print(f"⚠️ 입력 확인 실패. 예상: '{prompt[:50]}...', 실제: '{current_text[:50]}...'")
                # 재시도 - send_keys 사용
                print("⚠️ send_keys로 재시도...")
                input_element.click()
                time.sleep(0.5)
                input_element.send_keys(prompt)
                time.sleep(1)
                print("✅ 프롬프트 입력 완료 (재시도)")
                return True

        except Exception as e:
            print(f"❌ 프롬프트 입력 실패: {e}")
            import traceback
            traceback.print_exc()
            return False

    def click_generate_button(self):
        """생성 버튼 클릭 ('상식 여행' 버튼)"""
        try:
            print("\n🔘 생성 버튼 찾는 중...")

            # XPath 선택자 (한국어 "상식 여행" 텍스트 기반)
            xpath_selectors = [
                # "상식 여행" 텍스트 포함
                "//button[contains(., '상식 여행')]",
                "//button[contains(., '상식')]",
                # casino 아이콘이 있는 버튼
                "//button[.//i[contains(text(), 'casino')]]",
                # type=submit인 버튼 (마지막 옵션)
                "//button[@type='submit' and contains(., '상식')]",
            ]

            # CSS 선택자
            css_selectors = [
                # 분석된 클래스명
                "button.gdArnN",
                "button.fzQimn",
            ]

            button = None

            # XPath 선택자 시도 (한국어 텍스트가 더 정확하므로 먼저 시도)
            for selector in xpath_selectors:
                try:
                    button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"✅ 생성 버튼 찾음 ('상식 여행' 버튼)")
                    break
                except TimeoutException:
                    continue
                except Exception:
                    continue

            # CSS 선택자 시도
            if not button:
                for selector in css_selectors:
                    try:
                        button = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        # 텍스트 확인
                        btn_text = button.text
                        if '상식' in btn_text:
                            print(f"✅ 생성 버튼 찾음 ('상식 여행' 버튼)")
                            break
                    except TimeoutException:
                        continue
                    except Exception:
                        continue

            if not button:
                print("❌ 생성 버튼을 찾을 수 없습니다.")
                print("💡 수동으로 '상식 여행' 버튼을 클릭한 후 Enter를 누르세요...")
                input()
                return True

            # 버튼 클릭 (여러 방법 시도)
            try:
                # 스크롤하여 버튼을 화면에 표시
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(0.5)

                # JavaScript로 클릭 시도
                try:
                    self.driver.execute_script("arguments[0].click();", button)
                    print("✅ 생성 버튼 클릭 완료")
                except:
                    button.click()
                    print("✅ 생성 버튼 클릭 완료")

                return True
            except Exception as e:
                print(f"⚠️ 버튼 클릭 실패, 재시도: {e}")
                button.click()
                print("✅ 생성 버튼 클릭 완료")
                return True

        except Exception as e:
            print(f"❌ 생성 버튼 클릭 실패: {e}")
            import traceback
            traceback.print_exc()
            return False

    def capture_current_image_hashes(self):
        """현재 페이지의 이미지 해시 저장 (생성 버튼 클릭 전에 호출)"""
        hashes = set()
        try:
            images = self.driver.find_elements(By.TAG_NAME, "img")
            for img in images:
                try:
                    src = img.get_attribute("src")
                    if src and src.startswith("data:") and len(src) > 50000:
                        width = img.size.get('width', 0)
                        if width > 100:
                            img_hash = hashlib.md5(src[:1000].encode()).hexdigest()
                            hashes.add(img_hash)
                except:
                    continue

            if hashes:
                print(f"   📋 현재 이미지 {len(hashes)}개 감지됨 (중복 방지용)")
        except Exception as e:
            print(f"   ⚠️ 이미지 해시 캡처 실패: {e}")

        return hashes

    def wait_for_images(self, timeout=30, initial_hashes=None):
        """이미지 생성 완료 대기 (변화 감지 방식)"""
        try:
            print(f"\n⏳ 이미지 생성 대기 중... (최대 {timeout}초)")
            start_time = time.time()
            previous_count = 0
            stable_count = 0
            target_images = 4  # ImageFX는 4개 생성
            last_print_time = 0
            check_interval = 5  # 5초마다 확인

            # initial_hashes가 제공되면 중복 체크
            if initial_hashes is None:
                initial_hashes = set()

            if initial_hashes:
                print(f"   📋 이전 이미지 {len(initial_hashes)}개 제외, 새 이미지만 대기 중...")

            while time.time() - start_time < timeout:
                # 이미지 요소 찾기 시도
                images = self.driver.find_elements(By.TAG_NAME, "img")

                # 생성된 이미지 필터링 (data: URL만 사용 - 프로필 이미지 제외)
                valid_images = []
                current_hashes = set()

                for img in images:
                    try:
                        src = img.get_attribute("src")
                        if not src:
                            continue

                        # ImageFX 생성 이미지는 data: URL만 사용
                        if src.startswith("data:"):
                            if len(src) > 50000:  # 50KB 이상 (실제 이미지)
                                # 썸네일 제외 (너비 100 이상만)
                                width = img.size.get('width', 0)
                                if width > 100:
                                    img_hash = hashlib.md5(src[:1000].encode()).hexdigest()
                                    current_hashes.add(img_hash)

                                    # 새 이미지인지 확인
                                    if not initial_hashes or img_hash not in initial_hashes:
                                        valid_images.append(img)
                    except:
                        continue

                current_count = len(valid_images)

                # 이미지 개수가 3회 연속 동일하면 생성 완료로 판단
                if current_count == previous_count:
                    stable_count += 1
                else:
                    stable_count = 0

                previous_count = current_count

                # 3회 연속 동일 (15초) 또는 4개 도달 시 완료
                if (stable_count >= 3 and current_count > 0) or current_count >= target_images:
                    if current_count > 0:
                        print(f"✅ {current_count}개 새 이미지 생성 완료!")
                        return True

                # 진행 상황 표시 (5초마다)
                elapsed = int(time.time() - start_time)
                if elapsed - last_print_time >= check_interval and elapsed > 0:
                    print(f"   {elapsed}초 경과... (새 이미지: {current_count}개, 안정: {stable_count}/3)")
                    last_print_time = elapsed

                time.sleep(check_interval)

            # 타임아웃: 이미지 개수에 따라 처리
            if len(valid_images) > 0:
                print(f"⚠️ 타임아웃 ({timeout}초) - {len(valid_images)}개 이미지로 계속 진행합니다.")
                return True
            else:
                print(f"⚠️ 타임아웃 ({timeout}초) - 이미지 생성 실패. 다음 프롬프트로 진행합니다.")
                return False

        except Exception as e:
            print(f"❌ 이미지 대기 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return False

    def download_images(self, prompt):
        """생성된 이미지 4개 다운로드 (hover로 다운로드 버튼 활성화)"""
        try:
            print("\n💾 이미지 다운로드 시작...")

            # 모든 이미지 요소 찾기
            images = self.driver.find_elements(By.TAG_NAME, "img")

            # 유효한 이미지 필터링 (data: URL만 - 프로필 이미지 제외)
            valid_images = []
            for img in images:
                try:
                    src = img.get_attribute("src")
                    if not src:
                        continue

                    # ImageFX 생성 이미지는 data: URL만 사용
                    if src.startswith("data:"):
                        if len(src) > 50000:  # 50KB 이상 (실제 이미지)
                            width = img.size.get('width', 0)
                            if width > 100:  # 썸네일 제외
                                valid_images.append((img, src))
                except:
                    continue

            print(f"📸 발견된 이미지: {len(valid_images)}개")

            if not valid_images:
                print("❌ 다운로드할 이미지를 찾을 수 없습니다.")
                return []

            # 타임스탬프 기반 폴더명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = "".join(c for c in prompt[:50] if c.isalnum() or c in (' ', '-', '_')).strip()
            session_dir = os.path.join(self.download_dir, f"{timestamp}_{safe_prompt}")
            os.makedirs(session_dir, exist_ok=True)

            downloaded_files = []
            actions = ActionChains(self.driver)

            # 최대 4개 이미지 다운로드
            for idx, (img_element, img_url) in enumerate(valid_images[:4], 1):
                try:
                    print(f"\n   [{idx}/4] 이미지 다운로드 중...")

                    # 이미지 요소로 스크롤
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", img_element)
                    time.sleep(0.5)

                    # 이미지 데이터 직접 저장 (버튼 클릭 불필요 - data: URL 사용)
                    print(f"   ⏳ 이미지 데이터 저장 중...")

                    # 파일명 생성
                    filename = f"image_{idx}.jpg"  # ImageFX는 jpg 사용
                    filepath = os.path.join(session_dir, filename)

                    # data: URL인 경우 base64 디코딩
                    if img_url.startswith("data:"):
                        # data:image/jpg;base64,... 형식에서 base64 부분 추출
                        base64_data = img_url.split(',', 1)[1]
                        image_data = base64.b64decode(base64_data)

                        with open(filepath, 'wb') as f:
                            f.write(image_data)
                    else:
                        # 일반 URL의 경우
                        response = requests.get(img_url, timeout=30)
                        response.raise_for_status()

                        with open(filepath, 'wb') as f:
                            f.write(response.content)

                    downloaded_files.append(filepath)
                    print(f"   ✅ 저장 완료: {filepath}")

                except Exception as e:
                    print(f"   ❌ 이미지 {idx} 다운로드 실패: {e}")
                    import traceback
                    traceback.print_exc()

            # 메타데이터 저장
            metadata = {
                "prompt": prompt,
                "timestamp": timestamp,
                "downloaded_count": len(downloaded_files),
                "image_urls": [url for _, url in valid_images[:4]]
            }

            metadata_path = os.path.join(session_dir, "metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            print(f"\n✨ 다운로드 완료: {len(downloaded_files)}개 이미지")
            print(f"📁 저장 위치: {session_dir}")

            return downloaded_files

        except Exception as e:
            print(f"❌ 이미지 다운로드 실패: {e}")
            import traceback
            traceback.print_exc()
            return []

    def process_prompt(self, prompt):
        """프롬프트 처리 전체 플로우"""
        print(f"\n{'='*60}")
        print(f"🎨 프롬프트 처리 시작")
        print(f"{'='*60}")

        # 1. 프롬프트 입력
        if not self.enter_prompt(prompt):
            return False

        # 2. 생성 버튼 클릭 전에 현재 이미지 해시 캡처 (중복 방지)
        initial_hashes = self.capture_current_image_hashes()

        # 3. 생성 버튼 클릭
        if not self.click_generate_button():
            return False

        # 4. 이미지 생성 대기 (이전 이미지 해시 전달)
        self.wait_for_images(initial_hashes=initial_hashes)
        # 이미지 생성 실패해도 계속 진행 (0개일 수도 있음)

        # 5. 이미지 다운로드
        downloaded_files = self.download_images(prompt)

        if downloaded_files:
            print(f"\n✅ 프롬프트 처리 완료: {len(downloaded_files)}개 이미지 다운로드")
        else:
            print("\n⚠️ 이미지가 생성되지 않았습니다. 다음 프롬프트로 진행합니다.")

        # 성공/실패 상관없이 항상 True 반환 (계속 진행)
        return True

    def close(self):
        """브라우저 연결 종료 (브라우저는 닫지 않음)"""
        if self.driver:
            print("\n👋 Selenium 연결 종료 (브라우저는 계속 실행됩니다)")
            self.driver.quit()


def main():
    """메인 실행 함수"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║          ImageFX Selenium Automation Tool                    ║
║          디버그 모드로 이미지 자동 생성 및 다운로드           ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # 설정
    DEBUG_PORT = 9222
    DOWNLOAD_DIR = "downloads"
    PROMPTS_FILE = "prompts.txt"

    # ImageFX 다운로더 초기화
    downloader = ImageFXDownloader(debug_port=DEBUG_PORT, download_dir=DOWNLOAD_DIR)

    # Chrome 브라우저 연결
    if not downloader.connect_to_browser():
        print("\n❌ Chrome 브라우저에 연결할 수 없습니다.")
        print("💡 다음 단계를 따르세요:")
        print("   1. 모든 Chrome 창을 닫으세요")
        print(f"   2. 디버그 모드로 Chrome을 실행하세요:")
        print(f"      - Windows: chrome.exe --remote-debugging-port={DEBUG_PORT} --user-data-dir=remote-profile")
        print(f"      - Mac: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port={DEBUG_PORT} --user-data-dir=remote-profile")
        print(f"      - Linux: google-chrome --remote-debugging-port={DEBUG_PORT} --user-data-dir=remote-profile")
        print("   3. 스크립트를 다시 실행하세요")
        return

    # ImageFX 페이지로 이동
    if not downloader.navigate_to_imagefx():
        print("\n❌ ImageFX 페이지로 이동할 수 없습니다.")
        downloader.close()
        return

    print("\n💡 Google 계정 로그인이 필요한 경우 브라우저에서 로그인하세요.")
    print("   로그인 후 Enter를 눌러 계속하세요...")
    input()

    # 프롬프트 읽기
    prompts = []
    if os.path.exists(PROMPTS_FILE):
        print(f"\n📄 프롬프트 파일 읽기: {PROMPTS_FILE}")
        with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
            prompts = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"✅ {len(prompts)}개 프롬프트 로드됨")
    else:
        print(f"\n⚠️ 프롬프트 파일이 없습니다: {PROMPTS_FILE}")
        print("💡 대화형 모드로 프롬프트를 입력하세요 (종료하려면 빈 줄 입력)")
        while True:
            prompt = input("\n프롬프트 입력: ").strip()
            if not prompt:
                break
            prompts.append(prompt)

    if not prompts:
        print("\n⚠️ 처리할 프롬프트가 없습니다.")
        downloader.close()
        return

    # 각 프롬프트 처리
    print(f"\n{'='*60}")
    print(f"🚀 총 {len(prompts)}개 프롬프트 처리 시작")
    print(f"{'='*60}")

    success_count = 0
    for idx, prompt in enumerate(prompts, 1):
        print(f"\n[{idx}/{len(prompts)}] 프롬프트: {prompt}")

        if downloader.process_prompt(prompt):
            success_count += 1

        # 마지막 프롬프트가 아니면 대기
        if idx < len(prompts):
            print("\n⏸️ 다음 프롬프트를 처리하기 전에 10초 대기...")
            time.sleep(10)

    # 완료 메시지
    print(f"\n{'='*60}")
    print(f"✨ 모든 작업 완료!")
    print(f"{'='*60}")
    print(f"성공: {success_count}/{len(prompts)}")
    print(f"다운로드 위치: {os.path.abspath(DOWNLOAD_DIR)}")

    # 연결 종료
    downloader.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 사용자가 프로그램을 중단했습니다.")
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
