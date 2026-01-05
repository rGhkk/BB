"""
ImageFX Selenium Automation Script
디버깅 모드로 기존 Chrome 브라우저에 연결하여 ImageFX에서 이미지를 생성하고 다운로드합니다.
"""

import os
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
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
            time.sleep(5)  # 페이지 로딩 대기 (증가)
            print("✅ ImageFX 페이지 로드 완료")
            return True
        except Exception as e:
            print(f"❌ ImageFX 페이지 로드 실패: {e}")
            return False

    def enter_prompt(self, prompt):
        """프롬프트 입력"""
        print(f"\n📝 프롬프트 입력: {prompt}")

        # 프롬프트 입력창 찾기 (여러 선택자 시도)
        selectors = [
            "textarea",
            "input[type='text']",
            "[contenteditable='true']",
            "div.input-box",
            "#prompt-input"
        ]

        input_element = None
        selected_selector = None

        # 먼저 요소가 존재할 때까지 대기
        for selector in selectors:
            try:
                input_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                selected_selector = selector
                print(f"✅ 입력창 찾음 (선택자: {selector})")
                break
            except TimeoutException:
                continue

        if not input_element:
            print("❌ 프롬프트 입력창을 찾을 수 없습니다.")
            print("💡 수동으로 프롬프트를 입력하려면 아래 안내를 따르세요:")
            print(f"   1. 브라우저에서 ImageFX 프롬프트 입력창을 찾으세요")
            print(f"   2. 다음 프롬프트를 입력하세요: {prompt}")
            print(f"   3. 생성 버튼을 클릭하세요")
            input("   4. Enter를 눌러 계속하세요...")
            return True

        # 입력 시도 - JavaScript 우선 방식으로 변경
        print("🔄 프롬프트 입력 시도 중...")

        # 방법 1: JavaScript로 직접 입력 (가장 안정적)
        try:
            # 요소를 뷰포트에 스크롤
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});",
                input_element
            )
            time.sleep(1)

            # JavaScript로 포커스 및 값 설정
            self.driver.execute_script("""
                var element = arguments[0];
                var text = arguments[1];

                // 포커스
                element.focus();

                // 값 설정
                element.value = text;

                // React/Vue 등을 위한 다양한 이벤트 트리거
                element.dispatchEvent(new Event('focus', { bubbles: true }));
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
                element.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true }));
                element.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
            """, input_element, prompt)

            time.sleep(1)
            print("✅ 프롬프트 입력 완료 (JavaScript)")
            return True

        except Exception as e1:
            print(f"⚠️ JavaScript 입력 실패, Selenium으로 재시도: {e1}")

            # 방법 2: Selenium Actions 사용
            try:
                from selenium.webdriver.common.action_chains import ActionChains

                actions = ActionChains(self.driver)
                actions.move_to_element(input_element).click().perform()
                time.sleep(0.5)

                # 기존 텍스트 삭제
                input_element.clear()
                time.sleep(0.3)

                # 텍스트 입력
                input_element.send_keys(prompt)
                time.sleep(1)

                print("✅ 프롬프트 입력 완료 (Selenium Actions)")
                return True

            except Exception as e2:
                print(f"⚠️ Selenium Actions도 실패, 일반 send_keys 시도: {e2}")

                # 방법 3: 기본 send_keys
                try:
                    input_element.click()
                    time.sleep(0.5)
                    input_element.clear()
                    input_element.send_keys(prompt)
                    time.sleep(1)

                    print("✅ 프롬프트 입력 완료 (send_keys)")
                    return True

                except Exception as e3:
                    print(f"❌ 모든 자동 입력 방법 실패: {e3}")
                    print("💡 수동으로 프롬프트를 입력해주세요:")
                    print(f"   프롬프트: {prompt}")
                    input("   입력 완료 후 Enter를 누르세요...")
                    return True

    def click_generate_button(self):
        """생성 버튼 클릭"""
        print("\n🔘 생성 버튼 찾는 중...")

        # 생성 버튼 선택자들
        button_selectors = [
            "button[aria-label*='Generate']",
            "button[aria-label*='Create']",
            "//button[contains(text(), 'Generate')]",
            "//button[contains(text(), 'Create')]",
            "button.generate-button",
            "button[type='submit']"
        ]

        button = None
        for selector in button_selectors:
            try:
                if selector.startswith("//"):
                    button = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                else:
                    button = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                print(f"✅ 생성 버튼 찾음 (선택자: {selector})")
                break
            except TimeoutException:
                continue

        if not button:
            print("❌ 생성 버튼을 찾을 수 없습니다.")
            print("💡 수동으로 생성 버튼을 클릭한 후 Enter를 누르세요...")
            input()
            return True

        # JavaScript 우선 방식으로 클릭
        print("🔄 생성 버튼 클릭 시도 중...")

        # 방법 1: JavaScript 클릭 (가장 안정적)
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});",
                button
            )
            time.sleep(0.5)

            self.driver.execute_script("arguments[0].click();", button)
            time.sleep(1)
            print("✅ 생성 버튼 클릭 완료 (JavaScript)")
            return True

        except Exception as e1:
            print(f"⚠️ JavaScript 클릭 실패, Actions로 재시도: {e1}")

            # 방법 2: Selenium Actions
            try:
                from selenium.webdriver.common.action_chains import ActionChains

                actions = ActionChains(self.driver)
                actions.move_to_element(button).click().perform()
                time.sleep(1)
                print("✅ 생성 버튼 클릭 완료 (Actions)")
                return True

            except Exception as e2:
                print(f"⚠️ Actions 클릭 실패, 일반 클릭 시도: {e2}")

                # 방법 3: 일반 클릭
                try:
                    button.click()
                    time.sleep(1)
                    print("✅ 생성 버튼 클릭 완료 (일반 클릭)")
                    return True

                except Exception as e3:
                    print(f"❌ 모든 클릭 방법 실패: {e3}")
                    print("💡 수동으로 생성 버튼을 클릭한 후 Enter를 누르세요...")
                    input()
                    return True

    def wait_for_images(self, timeout=120):
        """이미지 생성 완료 대기"""
        try:
            print(f"\n⏳ 이미지 생성 대기 중... (최대 {timeout}초)")
            start_time = time.time()

            while time.time() - start_time < timeout:
                # 이미지 요소 찾기 시도
                images = self.driver.find_elements(By.TAG_NAME, "img")

                # src가 있는 실제 이미지 필터링
                valid_images = [
                    img for img in images
                    if img.get_attribute("src") and
                    not img.get_attribute("src").startswith("data:") and
                    "icon" not in img.get_attribute("src").lower()
                ]

                if len(valid_images) >= 4:
                    print(f"✅ {len(valid_images)}개 이미지 생성 완료!")
                    return True

                # 진행 상황 표시
                elapsed = int(time.time() - start_time)
                if elapsed % 10 == 0 and elapsed > 0:
                    print(f"   {elapsed}초 경과... (발견된 이미지: {len(valid_images)}개)")

                time.sleep(2)

            print(f"⚠️ 타임아웃: {timeout}초 내에 4개의 이미지가 생성되지 않았습니다.")
            return False

        except Exception as e:
            print(f"❌ 이미지 대기 중 오류: {e}")
            return False

    def download_images(self, prompt):
        """생성된 이미지 4개 다운로드"""
        try:
            print("\n💾 이미지 다운로드 시작...")

            # 모든 이미지 요소 찾기
            images = self.driver.find_elements(By.TAG_NAME, "img")

            # 유효한 이미지 URL 필터링
            image_urls = []
            for img in images:
                src = img.get_attribute("src")
                if src and not src.startswith("data:") and "icon" not in src.lower():
                    image_urls.append(src)

            print(f"📸 발견된 이미지: {len(image_urls)}개")

            # 최대 4개만 다운로드
            download_urls = image_urls[:4]

            if not download_urls:
                print("❌ 다운로드할 이미지를 찾을 수 없습니다.")
                return []

            # 타임스탬프 기반 폴더명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = "".join(c for c in prompt[:50] if c.isalnum() or c in (' ', '-', '_')).strip()
            session_dir = os.path.join(self.download_dir, f"{timestamp}_{safe_prompt}")
            os.makedirs(session_dir, exist_ok=True)

            downloaded_files = []

            for idx, url in enumerate(download_urls, 1):
                try:
                    print(f"   [{idx}/4] 다운로드 중...")

                    # 이미지 다운로드
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()

                    # 파일명 생성
                    filename = f"image_{idx}.png"
                    filepath = os.path.join(session_dir, filename)

                    # 파일 저장
                    with open(filepath, 'wb') as f:
                        f.write(response.content)

                    downloaded_files.append(filepath)
                    print(f"   ✅ 저장 완료: {filepath}")

                except Exception as e:
                    print(f"   ❌ 이미지 {idx} 다운로드 실패: {e}")

            # 메타데이터 저장
            metadata = {
                "prompt": prompt,
                "timestamp": timestamp,
                "downloaded_count": len(downloaded_files),
                "image_urls": download_urls
            }

            metadata_path = os.path.join(session_dir, "metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            print(f"\n✨ 다운로드 완료: {len(downloaded_files)}개 이미지")
            print(f"📁 저장 위치: {session_dir}")

            return downloaded_files

        except Exception as e:
            print(f"❌ 이미지 다운로드 실패: {e}")
            return []

    def process_prompt(self, prompt):
        """프롬프트 처리 전체 플로우"""
        print(f"\n{'='*60}")
        print(f"🎨 프롬프트 처리 시작")
        print(f"{'='*60}")

        # 1. 프롬프트 입력
        if not self.enter_prompt(prompt):
            return False

        # 2. 생성 버튼 클릭
        if not self.click_generate_button():
            return False

        # 3. 이미지 생성 대기
        if not self.wait_for_images():
            print("⚠️ 이미지 생성이 완료되지 않았을 수 있습니다.")
            print("💡 계속 진행하려면 Enter를 누르세요 (취소하려면 Ctrl+C)...")
            try:
                input()
            except KeyboardInterrupt:
                print("\n❌ 사용자가 취소했습니다.")
                return False

        # 4. 이미지 다운로드
        downloaded_files = self.download_images(prompt)

        if downloaded_files:
            print(f"\n✅ 프롬프트 처리 완료: {len(downloaded_files)}개 이미지 다운로드")
            return True
        else:
            print("\n⚠️ 이미지 다운로드에 실패했습니다.")
            return False

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
