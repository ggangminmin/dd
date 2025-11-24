"""
이메일 발송 서비스 - Gmail SMTP 사용
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        # 이메일 주소에 따라 SMTP 서버 자동 선택
        self.sender_email = os.getenv('SMTP_EMAIL')
        self.sender_password = os.getenv('SMTP_PASSWORD')

        # 네이버 이메일인 경우 네이버 SMTP 사용
        if self.sender_email and 'naver.com' in self.sender_email:
            self.smtp_server = "smtp.naver.com"
            self.smtp_port = 587
        else:
            # Gmail SMTP (기본값)
            self.smtp_server = "smtp.gmail.com"
            self.smtp_port = 587

    def is_configured(self):
        """이메일 서비스가 설정되어 있는지 확인"""
        return bool(self.sender_email and self.sender_password)

    def send_password_reset_email(self, recipient_email, reset_link, username):
        """비밀번호 재설정 이메일 발송"""
        if not self.is_configured():
            print("[EMAIL] SMTP not configured. Please add SMTP_EMAIL and SMTP_PASSWORD to .env file.")
            return False

        try:
            # 이메일 내용 작성
            subject = "비밀번호 재설정 요청"

            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <h2 style="color: #667eea; margin-bottom: 20px;">비밀번호 재설정 요청</h2>

                        <p style="color: #333; line-height: 1.6;">안녕하세요, <strong>{username}</strong>님</p>

                        <p style="color: #333; line-height: 1.6;">
                            계정의 비밀번호 재설정 요청을 받았습니다. 아래 버튼을 클릭하여 비밀번호를 재설정하세요.
                        </p>

                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_link}"
                               style="display: inline-block; padding: 15px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                      color: white; text-decoration: none; border-radius: 25px; font-weight: bold;">
                                비밀번호 재설정하기
                            </a>
                        </div>

                        <p style="color: #666; font-size: 14px; line-height: 1.6;">
                            또는 아래 링크를 복사하여 브라우저에 붙여넣으세요:<br>
                            <span style="color: #667eea; word-break: break-all;">{reset_link}</span>
                        </p>

                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                            <p style="color: #999; font-size: 12px; line-height: 1.6;">
                                [!] 이 링크는 1시간 동안만 유효합니다.<br>
                                [!] 비밀번호 재설정을 요청하지 않았다면 이 이메일을 무시하세요.
                            </p>
                        </div>
                    </div>
                </body>
            </html>
            """

            # 이메일 메시지 생성
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient_email

            # HTML 파트 추가
            html_part = MIMEText(html_body, "html", "utf-8")
            message.attach(html_part)

            # SMTP 서버 연결 및 전송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # TLS 암호화
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            print(f"[EMAIL] Password reset email sent successfully to: {recipient_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            print("[EMAIL] SMTP authentication failed: Invalid email or password")
            return False
        except smtplib.SMTPException as e:
            print(f"[EMAIL] SMTP error: {e}")
            return False
        except Exception as e:
            print(f"[EMAIL] Unexpected error: {e}")
            return False
