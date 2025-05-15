import asyncio
import os
import random
from datetime import datetime

import nest_asyncio
from playwright.async_api import async_playwright

nest_asyncio.apply()

async def login_to_linkedin_with_verification(email, password):
    async with async_playwright() as p:
        # Khởi tạo trình duyệt headless và thiết lập ghi video
        browser = await p.chromium.launch(
            headless=True,
            slow_mo=100
        )
        
        # Tạo thư mục lưu ảnh và video
        os.makedirs("linkedin_login_process", exist_ok=True)
        os.makedirs("videos", exist_ok=True)
        
        # Khởi tạo context với tùy chọn ghi video
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            record_video_dir="videos/",
            record_video_size={"width": 1280, "height": 720}
        )
        
        page = await context.new_page()
        
        try:
            print("\n=== ĐANG BẮT ĐẦU QUÁ TRÌNH ĐĂNG NHẬP ===")
            await page.goto("https://www.linkedin.com/login", wait_until="networkidle")
            
            # Chụp ảnh màn hình đăng nhập
            await page.screenshot(path="linkedin_login_process/1_login_page.png")
            print("Đã tải trang đăng nhập LinkedIn.")
            
            # Điền thông tin đăng nhập
            print("\n> Đang nhập email...")
            await page.fill('input[name="session_key"]', email)
            await asyncio.sleep(0.5)
            
            print("> Đang nhập mật khẩu...")
            await page.fill('input[name="session_password"]', password)
            await asyncio.sleep(0.5)
            
            # Chụp ảnh sau khi điền thông tin
            await page.screenshot(path="linkedin_login_process/2_credentials_filled.png")
            
            # Nhấn nút đăng nhập
            print("\n> Nhấn nút đăng nhập...")
            await page.click('button[type="submit"]')
            
            # Đợi trang tải xong sau khi đăng nhập
            await page.wait_for_load_state("networkidle")
            await page.screenshot(path="linkedin_login_process/3_after_login_click.png")
            
            # Kiểm tra xác minh bảo mật
            if "checkpoint" in page.url or await page.is_visible('text="Verify"'):
                print("\n=== YÊU CẦU XÁC MINH BẢO MẬT ĐÃ ĐƯỢC PHÁT HIỆN ===")
                await page.screenshot(path="linkedin_login_process/4_verification_required.png")
                
                # Tìm thông tin về email 
                if await page.is_visible('text="We sent a verification code"'):
                    email_text = await page.inner_text('text="We sent a verification code" >> xpath=./following::p[1]')
                    if email_text:
                        print(f"> Mã đã được gửi đến: {email_text}")
                
                # Lưu thông tin
                page_content = await page.content()
                with open("linkedin_login_process/verification_page.html", "w", encoding="utf-8") as f:
                    f.write(page_content)
                
                # Nhập mã xác minh từ email
                verification_code = input("\n> Vui lòng nhập mã xác minh từ email của bạn: ")
                
                # Thử phương pháp 1: Điền vào các ô riêng biệt nếu có
                code_inputs = await page.query_selector_all('input[type="number"]')
                if len(code_inputs) >= 4:  # Thường là từ 4-6 ô
                    print(f"> Tìm thấy {len(code_inputs)} ô nhập mã riêng biệt...")
                    for i, digit in enumerate(verification_code):
                        if i < len(code_inputs):
                            await code_inputs[i].fill(digit)
                            print(f"  - Đã điền ký tự {digit} vào ô #{i+1}")
                    
                    print("> Đã điền mã xác minh vào các ô riêng biệt")
                else:
                    # Thử phương pháp 2: Tìm một ô nhập duy nhất
                    verification_input = await page.query_selector('input[name*="verification"], input[aria-label*="code"], input[id*="verification"], input[placeholder*="code"]')
                    if verification_input:
                        await verification_input.fill(verification_code)
                        print(f"> Đã điền mã xác minh '{verification_code}' vào trường nhập")
                    else:
                        print("> Không tìm thấy trường nhập mã xác minh phù hợp")
                        
                # Chụp ảnh sau khi nhập mã
                await page.screenshot(path="linkedin_login_process/5_code_entered.png")
                
                # Tìm nút Submit
                print("\n> Đang tìm nút Submit...")
                
                # Danh sách các selector tiềm năng cho nút Submit
                submit_selectors = [
                    'button[type="submit"]',
                    'button:has-text("Submit")',
                    'button:has-text("Verify")',
                    'button:has-text("Continue")',
                    'button.form__submit',
                    'button[data-litms-control-urn="verify_pin_submit_btn"]',
                    'button.primary-action-new',
                    'button.artdeco-button--primary',
                    'form >> button'
                ]
                
                # Tìm tất cả các nút tiềm năng
                found_buttons = []
                for selector in submit_selectors:
                    buttons = await page.query_selector_all(selector)
                    if buttons:
                        for btn in buttons:
                            # Kiểm tra xem nút có hiển thị không
                            is_visible = await btn.is_visible()
                            if is_visible:
                                text = await btn.inner_text() if await btn.inner_text() else "No text"
                                found_buttons.append((btn, text, selector))
                
                if found_buttons:
                    print(f"> Tìm thấy {len(found_buttons)} nút tiềm năng:")
                    for i, (btn, text, selector) in enumerate(found_buttons):
                        print(f"  {i+1}. Nút '{text}' ({selector})")
                    
                    # Bắt đầu với nút đầu tiên
                    submit_button, btn_text, _ = found_buttons[0]
                    print(f"\n> Nhấn nút '{btn_text}'...")
                    
                    # Nhấn nút
                    await submit_button.click()
                    print("> Đã nhấn nút Submit!")
                    
                    # Đợi và chụp ảnh
                    await asyncio.sleep(2)
                    await page.screenshot(path="linkedin_login_process/6_after_submit.png")
                
                # Xử lý tùy chọn thủ công
                user_action = input("\n> Script đã cố gắng tự submit form. Bạn có muốn tự xử lý không? (y/n): ")
                
                if user_action.lower() == 'y':
                    print("\n> Vui lòng làm theo hướng dẫn sau:")
                    print("1. Mở trình duyệt web của bạn")
                    print("2. Truy cập vào LinkedIn và đăng nhập")
                    print("3. Trong email của bạn, nhấp vào liên kết xác minh LinkedIn đã gửi")
                    print("4. Sau khi hoàn tất, quay lại đây và tiếp tục")
                    
                    input("\n> Nhấn Enter khi bạn đã hoàn tất việc xác minh...")
                    
                    # ====== THAY ĐỔI Ở ĐÂY: CẢI THIỆN KIỂM TRA ĐĂNG NHẬP THÀNH CÔNG ======
                    manual_success = input("\n> Bạn đã đăng nhập thành công vào LinkedIn chưa? (y/n): ")
                    
                    if manual_success.lower() == 'y':
                        print("\n=== ĐĂNG NHẬP THÀNH CÔNG QUA XÁC MINH THỦ CÔNG! ===")
                        # Thử truy cập lại LinkedIn để kiểm tra cookie
                        try:
                            # Thử truy cập trang feed để kiểm tra đăng nhập
                            await page.goto("https://www.linkedin.com/feed/", timeout=10000)
                            await page.screenshot(path="linkedin_login_process/7_feed_page_check.png")
                            print("> Đã chụp ảnh kiểm tra trang feed")
                            return True, page, context, browser
                        except Exception as e:
                            print(f"> Không thể truy cập trang feed: {e}")
                            print("> Sử dụng cookies mới để đăng nhập...")
                            
                            # Lấy cookie từ người dùng (tùy chọn nâng cao)
                            cookies_option = input("\n> Bạn có muốn thêm cookies mới từ phiên đăng nhập thành công không? (y/n): ")
                            if cookies_option.lower() == 'y':
                                # Người dùng có thể cung cấp cookies từ phiên đăng nhập thủ công
                                # (Đây là phần nâng cao, không cần thiết cho hầu hết người dùng)
                                print("> Tính năng này cần thiết lập thêm. Đang tiếp tục...")
                            
                            # Tạo phiên mới (tùy chọn)
                            restart_option = input("\n> Bạn có muốn tạo phiên mới để kiểm tra đăng nhập không? (y/n): ")
                            if restart_option.lower() == 'y':
                                print("> Đang khởi tạo lại trình duyệt...")
                                # Tạo context mới (tùy chọn nâng cao)
                                
                            # Vẫn trả về thành công dựa trên xác nhận của người dùng
                            return True, page, context, browser
                    else:
                        print("\n> Xác minh thủ công không thành công")
            
            # Kiểm tra đăng nhập thành công
            await page.screenshot(path="linkedin_login_process/7_final_state.png")
            current_url = page.url
            
            print(f"\n> URL hiện tại: {current_url}")
            
            if current_url.startswith("https://www.linkedin.com/feed"):
                print("\n=== ĐĂNG NHẬP THÀNH CÔNG! ===")
                await page.screenshot(path="linkedin_login_process/8_successful_login.png")
                return True, page, context, browser
            else:
                # Thêm kiểm tra phụ
                try:
                    await page.goto("https://www.linkedin.com/feed/", timeout=10000)
                    await asyncio.sleep(2)
                    feed_url = page.url
                    await page.screenshot(path="linkedin_login_process/8_feed_check.png")
                    
                    if feed_url.startswith("https://www.linkedin.com/feed"):
                        print("\n=== ĐĂNG NHẬP THÀNH CÔNG SAU KHI KIỂM TRA FEED! ===")
                        return True, page, context, browser
                except Exception as e:
                    print(f"\n> Lỗi khi kiểm tra trang feed: {e}")
                
                print(f"\n❌ ĐĂNG NHẬP KHÔNG THÀNH CÔNG! URL hiện tại: {page.url}")
                await page.screenshot(path="linkedin_login_process/8_failed_login.png")
                return False, page, context, browser
                
        except Exception as e:
            print(f"\n❌ LỖI: {e}")
            await page.screenshot(path=f"linkedin_login_process/error_{datetime.now().strftime('%H%M%S')}.png")
            return False, None, context, browser

async def main():
    email = "imbfs123456@gmail.com"  # Thay bằng email thật
    password = "thiendc3005aA@"         # Thay bằng mật khẩu thật

    print("\n==== BẮT ĐẦU ĐĂNG NHẬP LINKEDIN ====")
    print(f"Đang đăng nhập với email: {email}")
    
    success, page, context, browser = await login_to_linkedin_with_verification(email, password)

    if success and page:
        try:
            print("\n==== ĐĂNG NHẬP THÀNH CÔNG ====")
            print("Bạn đã đăng nhập vào LinkedIn!")
            print("\nVí dụ thực hiện một số thao tác trên LinkedIn...")
            
            # Thử truy cập lại một lần nữa
            try:
                await page.goto("https://www.linkedin.com/in/me", wait_until="networkidle", timeout=10000) ### sai nèè
                await page.screenshot(path="linkedin_login_process/profile_page.png")
                print("> Đã chụp ảnh trang cá nhân: linkedin_login_process/profile_page.png")
            except Exception as e:
                print(f"> Không thể truy cập trang cá nhân: {e}")
            
        except Exception as e:
            print(f"\n❌ Lỗi khi thực hiện thao tác: {e}")
        finally:
            print("\nĐóng trình duyệt...")
            await context.close()
            await browser.close()
            
            print("\n==== THÔNG TIN QUAN TRỌNG ====")
            print("1. Ảnh chụp màn hình đã được lưu trong thư mục: linkedin_login_process/")
            print("2. Video quá trình đăng nhập đã được lưu trong thư mục: videos/")
    else:
        print("\n❌ Đăng nhập thất bại")
        if 'browser' in locals() and browser:
            await browser.close()

# Chạy hàm main
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
