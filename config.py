# config.py
# SnapYTube Ultimate - مع دعم مجلدات منفصلة لكل مستخدم

import os
import socket
from datetime import datetime

class Config:
    """الإعدادات العامة للتطبيق"""

    # معلومات التطبيق
    APP_NAME = "SnapYTube Ultimate"
    APP_VERSION = "4.0.0"
    APP_AUTHOR = "SnapYTube Team"
    APP_DESCRIPTION = "منصة متكاملة لتحميل الفيديوهات من جميع المنصات بجودة 4K"

    # إعدادات السيرفر
    HOST = '0.0.0.0'
    PORT = 5001
    DEBUG = False

    # المسارات الأساسية
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # ⭐ مجلد المستخدمين (كل مستخدم له مجلد خاص)
    USERS_FOLDER = os.path.join(BASE_DIR, 'users')
    
    # ⭐ مجلد التحميل الحالي (بيتغير حسب المستخدم)
    DOWNLOAD_FOLDER = None
    
    # مجلدات السيرفر الأساسية (برا مجلد المستخدمين)
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
    STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
    LOGS_FOLDER = os.path.join(BASE_DIR, 'logs')
    CACHE_FOLDER = os.path.join(BASE_DIR, 'cache')

    # إعدادات التحميل
    MAX_FILE_SIZE_MB = 8000  # 8 GB
    MAX_CONCURRENT_DOWNLOADS = 2
    DOWNLOAD_TIMEOUT = 900   # 15 دقيقة

    # إعدادات الأداء
    CACHE_ENABLED = True
    CACHE_TIMEOUT = 3600

    # المنصات المدعومة
    SUPPORTED_PLATFORMS = {
        'youtube': {
            'name': 'YouTube',
            'icon': 'fab fa-youtube',
            'color': '#FF0000',
            'format': (
                'bestvideo[height=2160][ext=mp4]+bestaudio[ext=m4a]'
                '/bestvideo[height=2160]+bestaudio'
                '/bestvideo[height>=1440][ext=mp4]+bestaudio[ext=m4a]'
                '/bestvideo[height>=1440]+bestaudio'
                '/bestvideo[ext=mp4]+bestaudio[ext=m4a]'
                '/best[ext=mp4]/best'
            )
        },
        'tiktok': {
            'name': 'TikTok',
            'icon': 'fab fa-tiktok',
            'color': '#000000',
            'format': 'best[ext=mp4]/best'
        },
        'instagram': {
            'name': 'Instagram',
            'icon': 'fab fa-instagram',
            'color': '#E4405F',
            'format': 'best[ext=mp4]/best'
        },
        'facebook': {
            'name': 'Facebook',
            'icon': 'fab fa-facebook',
            'color': '#1877F2',
            'format': 'best[ext=mp4]/best'
        },
        'twitter': {
            'name': 'Twitter/X',
            'icon': 'fab fa-twitter',
            'color': '#1DA1F2',
            'format': 'best[ext=mp4]/best'
        },
        'capcut': {
            'name': 'CapCut',
            'icon': 'fas fa-cut',
            'color': '#00D4FF',
            'format': 'best[ext=mp4]/best'
        },
        'vimeo': {
            'name': 'Vimeo',
            'icon': 'fab fa-vimeo',
            'color': '#1AB7EA',
            'format': 'best[ext=mp4]/best'
        }
    }

    # رسائل النظام
    MESSAGES = {
        'download_start': '🎬 بدء تحميل الفيديو...',
        'download_success': '✅ تم تحميل الفيديو بنجاح!',
        'download_error': '❌ فشل التحميل: {error}',
        'invalid_url': '⚠️ الرابط غير صالح',
        'file_not_found': '📁 الملف غير موجود',
        'server_start': '🚀 السيرفر يعمل الآن',
        'server_stop': '🛑 تم إيقاف السيرفر',
        'welcome': '✨ مرحباً بك في SnapYTube Ultimate',
        'processing': '⚙️ جاري المعالجة...'
    }

    @classmethod
    def get_client_ip(cls, request=None):
        """الحصول على IP العميل"""
        if request:
            if request.headers.get('X-Forwarded-For'):
                return request.headers.get('X-Forwarded-For').split(',')[0].strip()
            elif request.headers.get('X-Real-IP'):
                return request.headers.get('X-Real-IP').strip()
            elif request.remote_addr:
                return request.remote_addr
        return 'local'

    @classmethod
    def get_user_folder(cls, client_ip):
        """الحصول على مسار مجلد المستخدم"""
        clean_ip = client_ip.replace('.', '_').replace(':', '_')
        return os.path.join(cls.USERS_FOLDER, f'device_{clean_ip}')

    @classmethod
    def setup_user_folders(cls, client_ip):
        """إعداد مجلدات المستخدم وتحديد DOWNLOAD_FOLDER"""
        user_folder = cls.get_user_folder(client_ip)
        
        # إنشاء المجلدات
        downloads_folder = os.path.join(user_folder, 'downloads')
        logs_folder = os.path.join(user_folder, 'logs')
        
        os.makedirs(downloads_folder, exist_ok=True)
        os.makedirs(logs_folder, exist_ok=True)
        
        # تعيين مجلد التحميل
        cls.DOWNLOAD_FOLDER = downloads_folder
        
        return user_folder

    @classmethod
    def setup_directories(cls):
        """إنشاء المجلدات الأساسية للسيرفر"""
        folders = [
            cls.USERS_FOLDER,
            cls.TEMPLATE_FOLDER,
            cls.STATIC_FOLDER,
            cls.LOGS_FOLDER,
            cls.CACHE_FOLDER
        ]
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
        return True

    @classmethod
    def get_local_ip(cls):
        """الحصول على عنوان IP المحلي"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    @classmethod
    def get_banner(cls):
        """شعار التطبيق"""
        banner = f"""
╔══════════════════════════════════════════════════════════╗
║       SnapYTube Ultimate v{cls.APP_VERSION} — 4K Mode            ║
║       {cls.APP_DESCRIPTION[:45]}   ║
║                                                          ║
║  📁 مجلد المستخدمين: users/                              ║
║  🔒 كل جهاز له مجلد خاص (حسب IP)                         ║
╚══════════════════════════════════════════════════════════╝
        """
        return banner

# تهيئة المجلدات الأساسية
Config.setup_directories()
