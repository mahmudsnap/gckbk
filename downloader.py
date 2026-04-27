# downloader.py
# SnapYTube Ultimate - محرك تحميل مع دعم مجلدات المستخدمين وشريط تقدم حقيقي

import os
import re
import time
import json
import threading
from datetime import datetime
import yt_dlp
from config import Config


class DownloadLogger:
    """نظام تسجيل التحميلات - لكل مستخدم سجل خاص"""
    
    def __init__(self, log_folder=None):
        self.log_folder = log_folder or Config.LOGS_FOLDER
        self.log_file = os.path.join(self.log_folder, 'downloads.json')
        self.history = []
        self.load_history()

    def load_history(self):
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []

    def save_history(self):
        try:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.history[-500:], f, ensure_ascii=False, indent=2)
        except:
            pass

    def add(self, data):
        data['timestamp'] = time.time()
        data['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.history.insert(0, data)
        self.save_history()

    def get_all(self, limit=100):
        return self.history[:limit]

    def get_stats(self):
        stats = {
            'total': len(self.history),
            'by_platform': {},
            'today': 0,
            'this_week': 0,
            'total_size': 0
        }
        today = datetime.now().strftime('%Y-%m-%d')
        week_ago = time.time() - (7 * 24 * 3600)

        for item in self.history:
            platform = item.get('platform', 'other')
            stats['by_platform'][platform] = stats['by_platform'].get(platform, 0) + 1
            if item.get('date', '').startswith(today):
                stats['today'] += 1
            if item.get('timestamp', 0) > week_ago:
                stats['this_week'] += 1
            stats['total_size'] += item.get('filesize', 0)

        return stats


class MediaDownloader:
    """الفئة الرئيسية لتحميل الوسائط"""
    
    def __init__(self):
        self.download_folder = None
        self.log_folder = None
        self.logger = None
        self.active_downloads = {}
        self.download_lock = threading.Lock()
        self.progress_callbacks = {}
        
        # إعدادات yt-dlp
        self.base_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'noplaylist': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'retries': 3,
            'fragment_retries': 3,
            'socket_timeout': 30,
            'sleep_requests': 0,
            'sleep_interval': 0,
            'concurrent_fragment_downloads': 16,
            'http_chunk_size': 10485760,
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }

    def setup_for_client(self, client_ip):
        """إعداد المجلدات للمستخدم الحالي"""
        user_folder = Config.setup_user_folders(client_ip)
        self.download_folder = Config.DOWNLOAD_FOLDER
        self.log_folder = os.path.join(user_folder, 'logs')
        self.logger = DownloadLogger(self.log_folder)
        
        # التأكد من وجود مجلد التحميل
        os.makedirs(self.download_folder, exist_ok=True)
        
        return self.download_folder

    def detect_platform(self, url):
        """تحديد المنصة من الرابط"""
        url_lower = url.lower()
        domains = {
            'youtube':   ['youtube.com', 'youtu.be'],
            'tiktok':    ['tiktok.com', 'vt.tiktok', 'vm.tiktok'],
            'instagram': ['instagram.com', 'instagr.am'],
            'facebook':  ['facebook.com', 'fb.watch', 'fb.com'],
            'twitter':   ['twitter.com', 'x.com'],
            'capcut':    ['capcut.com', 'capcut.net'],
            'vimeo':     ['vimeo.com']
        }
        for platform, domain_list in domains.items():
            if any(d in url_lower for d in domain_list):
                return platform
        return 'other'

    def validate_url(self, url):
        """التحقق من صحة الرابط"""
        pattern = re.compile(
            r'^https?://'
            r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'
            r'(/[^\s]*)?$'
        )
        return bool(pattern.match(url.strip()))

    def get_thumbnail(self, url, platform):
        """الحصول على صورة مصغرة للفيديو"""
        if platform == 'youtube':
            for pattern in [r'youtube\.com/watch\?v=([^&]+)', r'youtu\.be/([^?]+)']:
                match = re.search(pattern, url)
                if match:
                    return f"https://img.youtube.com/vi/{match.group(1)}/mqdefault.jpg"
        return None

    def _resolution_label(self, info):
        """تحديد تسمية الجودة"""
        height = info.get('height', 0) or 0
        if height >= 2160:
            return '4K (2160p)'
        elif height >= 1440:
            return '1440p (2K)'
        elif height >= 1080:
            return '1080p (FHD)'
        elif height >= 720:
            return '720p (HD)'
        elif height > 0:
            return f'{height}p'
        return 'Unknown'

    # ═══════════════════════════════════════════════════════════════
    # ⭐⭐⭐ دالة التحميل المصححة - مع شريط تقدم حقيقي بالميغابايت ⭐⭐⭐
    # ═══════════════════════════════════════════════════════════════
    def download(self, url, progress_callback=None, download_id=None):
        """تحميل الفيديو مع شريط تقدم حقيقي"""
        
        url = url.strip()
        
        if not self.validate_url(url):
            return {'success': False, 'error': Config.MESSAGES['invalid_url']}

        platform = self.detect_platform(url)
        platform_info = Config.SUPPORTED_PLATFORMS.get(
            platform,
            {'name': 'Other', 'format': 'best[ext=mp4]/best'}
        )

        if not download_id:
            download_id = str(int(time.time() * 1000))

        # ⭐ هيكل بيانات التقدم
        progress_data = {
            'percent': 0,
            'speed': 0,
            'speed_mb': 0,
            'speed_str': '0 MB/s',
            'eta': '?',
            'status': 'starting',
            'downloaded': 0,
            'total': 0
        }

        # ⭐ إرسال الحالة الأولية
        if progress_callback:
            self.progress_callbacks[download_id] = progress_callback
            progress_callback(progress_data.copy())

        print(f"\n🎬 [{platform_info['name']}] {url[:60]}...")

        def progress_hook(d):
            """خطاف التقدم من yt-dlp - نسخة مصححة"""
            try:
                if d['status'] == 'downloading':
                    # ⭐ استخراج النسبة المئوية
                    percent = 0
                    if '_percent_str' in d:
                        percent_str = d['_percent_str'].strip().replace('%', '').strip()
                        try:
                            percent = float(percent_str)
                        except:
                            percent = 0
                    elif 'total_bytes' in d and d['total_bytes'] > 0:
                        downloaded = d.get('downloaded_bytes', 0)
                        total = d.get('total_bytes', 1)
                        percent = (downloaded / total) * 100
                    
                    # ⭐ استخراج السرعة بالميغابايت
                    speed_mb = 0
                    speed_str = '0 MB/s'
                    
                    if 'speed' in d and d['speed'] is not None:
                        speed_bytes = float(d['speed'])
                        speed_mb = round(speed_bytes / (1024 * 1024), 2)
                        if speed_mb >= 1:
                            speed_str = f"{speed_mb:.1f} MB/s"
                        else:
                            speed_kb = round(speed_bytes / 1024, 1)
                            speed_str = f"{speed_kb:.1f} KB/s"
                    elif '_speed_str' in d:
                        raw_speed = d['_speed_str'].strip()
                        if 'MiB/s' in raw_speed:
                            val = float(raw_speed.replace('MiB/s', '').strip())
                            speed_mb = round(val * 1.048576, 2)
                            speed_str = f"{speed_mb:.1f} MB/s"
                        elif 'MB/s' in raw_speed:
                            speed_mb = float(raw_speed.replace('MB/s', '').strip())
                            speed_str = raw_speed
                        elif 'KiB/s' in raw_speed:
                            val = float(raw_speed.replace('KiB/s', '').strip())
                            speed_mb = round(val / 1024, 2)
                            speed_str = f"{speed_mb:.1f} MB/s" if speed_mb >= 0.1 else raw_speed
                        elif 'KB/s' in raw_speed:
                            val = float(raw_speed.replace('KB/s', '').strip())
                            speed_mb = round(val / 1024, 2)
                            speed_str = raw_speed
                        else:
                            speed_str = raw_speed
                    
                    # ⭐ استخراج الوقت المتبقي
                    eta_str = d.get('_eta_str', '?').strip() if '_eta_str' in d else '?'
                    
                    # ⭐ حساب الحجم المحمّل والكلي
                    downloaded_mb = 0
                    total_mb = 0
                    
                    if 'downloaded_bytes' in d:
                        downloaded_mb = round(d['downloaded_bytes'] / (1024 * 1024), 2)
                    if 'total_bytes' in d and d['total_bytes']:
                        total_mb = round(d['total_bytes'] / (1024 * 1024), 2)
                    elif 'total_bytes_estimate' in d:
                        total_mb = round(d['total_bytes_estimate'] / (1024 * 1024), 2)
                    
                    # ⭐ تحديث البيانات
                    progress_data['percent'] = round(percent, 1)
                    progress_data['speed'] = speed_mb
                    progress_data['speed_mb'] = speed_mb
                    progress_data['speed_str'] = speed_str
                    progress_data['eta'] = eta_str
                    progress_data['status'] = 'downloading'
                    progress_data['downloaded'] = downloaded_mb
                    progress_data['total'] = total_mb
                    
                    # ⭐ شريط تقدم في الترمكس
                    bar_length = 30
                    filled = int(bar_length * percent / 100)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    print(f"\r{bar} {percent:.1f}% | {speed_str} | {eta_str}     ", end='', flush=True)
                    
                    # ⭐ إرسال التحديث للـ frontend
                    if progress_callback:
                        progress_callback(progress_data.copy())
                    
                elif d['status'] == 'finished':
                    progress_data['status'] = 'processing'
                    progress_data['percent'] = 100
                    progress_data['downloaded'] = progress_data['total']
                    
                    print(f"\n⚙️  جاري المعالجة والدمج...")
                    
                    if progress_callback:
                        progress_callback(progress_data.copy())
                    
                elif d['status'] == 'error':
                    progress_data['status'] = 'error'
                    print(f"\n❌ خطأ في التحميل")
                    
                    if progress_callback:
                        progress_callback(progress_data.copy())
                        
            except Exception as e:
                print(f"\n⚠️ خطأ في progress_hook: {e}")

        # إعدادات yt-dlp
        opts = self.base_opts.copy()
        opts['format'] = platform_info.get('format', 'best[ext=mp4]/best')
        opts['progress_hooks'] = [progress_hook]
        opts['outtmpl'] = os.path.join(self.download_folder, '%(title).80s_%(id)s.%(ext)s')
        opts['progress_with_newline'] = False

        # إعدادات خاصة بالمنصات
        if platform == 'tiktok':
            opts['http_headers']['Referer'] = 'https://www.tiktok.com/'
        elif platform == 'instagram':
            opts['http_headers']['Referer'] = 'https://www.instagram.com/'
        elif platform == 'twitter':
            opts['http_headers']['Referer'] = 'https://twitter.com/'

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)

            print()

            if info is None:
                return {'success': False, 'error': 'فشل استخراج معلومات الفيديو'}

            # البحث عن الملف المحمّل
            filepath = None
            
            try:
                filepath = ydl.prepare_filename(info)
            except:
                pass
            
            if not filepath or not os.path.exists(filepath):
                base = os.path.splitext(filepath)[0] if filepath else None
                if base:
                    for ext in ['.mp4', '.mkv', '.webm', '.m4a']:
                        test_path = base + ext
                        if os.path.exists(test_path):
                            filepath = test_path
                            break
            
            if not filepath or not os.path.exists(filepath):
                files = [
                    os.path.join(self.download_folder, f)
                    for f in os.listdir(self.download_folder)
                    if f.lower().endswith(('.mp4', '.mkv', '.webm'))
                ]
                if files:
                    filepath = max(files, key=os.path.getmtime)
                    print(f"✅ تم العثور على أحدث ملف: {os.path.basename(filepath)}")

            if not filepath or not os.path.exists(filepath):
                return {'success': False, 'error': 'الملف غير موجود'}

            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
            filesize_mb = round(filesize / (1024 * 1024), 2)

            # ⭐ إرسال حالة الاكتمال
            progress_data['status'] = 'completed'
            progress_data['percent'] = 100
            progress_data['downloaded'] = filesize_mb
            progress_data['total'] = filesize_mb
            if progress_callback:
                progress_callback(progress_data.copy())

            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            quality = self._resolution_label(info)

            print(f"\n✅ تم التحميل: {filename}")
            print(f"📊 الحجم: {filesize_mb} MB | الجودة: {quality}")
            print(f"📁 المسار: {filepath}")

            # تسجيل في السجل
            if self.logger:
                self.logger.add({
                    'filename': filename,
                    'title': title,
                    'platform': platform,
                    'url': url,
                    'duration': duration,
                    'filesize': filesize,
                    'quality': quality,
                    'thumbnail': self.get_thumbnail(url, platform)
                })

            # تنظيف
            if download_id in self.progress_callbacks:
                del self.progress_callbacks[download_id]

            return {
                'success': True,
                'filename': filename,
                'title': title,
                'platform': platform,
                'duration': duration,
                'filesize': filesize,
                'filesize_mb': filesize_mb,
                'quality': quality,
                'thumbnail': self.get_thumbnail(url, platform),
                'filepath': filepath
            }

        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if 'ffmpeg' in error_msg.lower():
                error_msg = 'ffmpeg غير موجود — شغّل: pkg install ffmpeg'
            elif 'timeout' in error_msg.lower():
                error_msg = 'انتهت مهلة الاتصال — تأكد من الإنترنت'
            elif 'unavailable' in error_msg.lower():
                error_msg = 'الفيديو غير متاح أو محذوف'
            
            print(f"\n❌ خطأ: {error_msg}")
            
            progress_data['status'] = 'error'
            if progress_callback:
                progress_callback(progress_data.copy())
            
            if download_id in self.progress_callbacks:
                del self.progress_callbacks[download_id]
            
            return {'success': False, 'error': error_msg}

        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ خطأ غير متوقع: {error_msg}")
            
            progress_data['status'] = 'error'
            if progress_callback:
                progress_callback(progress_data.copy())
            
            if download_id in self.progress_callbacks:
                del self.progress_callbacks[download_id]
            
            return {'success': False, 'error': error_msg}

    def get_info(self, url):
        """الحصول على معلومات الفيديو بدون تحميل"""
        if not self.validate_url(url):
            return {'success': False, 'error': Config.MESSAGES['invalid_url']}

        opts = self.base_opts.copy()
        opts['extract_flat'] = False

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)

            if info is None:
                return {'success': False, 'error': 'تعذر جلب معلومات الفيديو'}

            return {
                'success': True,
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'views': info.get('view_count', 0),
                'platform': self.detect_platform(url),
                'thumbnail': info.get('thumbnail') or self.get_thumbnail(url, self.detect_platform(url))
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_stats(self):
        if self.logger:
            return self.logger.get_stats()
        return {'total': 0, 'by_platform': {}, 'today': 0, 'this_week': 0, 'total_size': 0}

    def get_history(self, limit=50):
        if self.logger:
            return self.logger.get_all(limit)
        return []


downloader = MediaDownloader()
