#!/data/data/com.termux/files/usr/bin/bash
# ╔══════════════════════════════════════════════════════╗
# ║     SnapYTube Ultimate — تشغيل السيرفر               ║
# ╚══════════════════════════════════════════════════════╝

# ═══ الألوان ═══
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

PORT=5001

# ═══ الشعار ═══
clear
echo ""
echo -e "${PURPLE}${BOLD}"
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   🎬 SnapYTube Ultimate v4.0             ║"
echo "  ║   منصة تحميل الفيديو متعددة المنصات     ║"
echo "  ╚══════════════════════════════════════════╝"
echo -e "${NC}"

# ═══ فحص الملفات ═══
for f in run.py config.py downloader.py index.html; do
    if [ ! -f "$PROJECT_DIR/$f" ]; then
        echo -e "${RED}❌ الملف $f مفقود!${NC}"
        echo -e "${YELLOW}شغّل أولاً: bash setup.sh${NC}"
        exit 1
    fi
done

# ═══ فحص Flask ═══
if ! python -c "import flask" 2>/dev/null; then
    echo -e "${RED}❌ Flask غير مثبت!${NC}"
    echo -e "${YELLOW}شغّل أولاً: bash setup.sh${NC}"
    exit 1
fi

# ═══ الحصول على IP المحلي ═══
LOCAL_IP=$(python -c "
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    print(s.getsockname()[0])
    s.close()
except:
    print('127.0.0.1')
" 2>/dev/null)

SERVER_URL="http://${LOCAL_IP}:${PORT}"
LOCALHOST_URL="http://localhost:${PORT}"

# ═══ فحص اختياري لتحديث yt-dlp ═══
echo -e "${CYAN}🔄 فحص تحديثات yt-dlp...${NC}"
if [ -d "/data/data/com.termux" ]; then
    PIP_FLAG="--break-system-packages"
else
    PIP_FLAG=""
fi
python -m pip install -U yt-dlp -q $PIP_FLAG 2>/dev/null && \
    echo -e "${GREEN}✅ yt-dlp محدّث${NC}" || \
    echo -e "${YELLOW}⚠️  لم يتم التحديث (تحقق من الإنترنت)${NC}"

echo ""

# ═══ إحصائيات المشروع ═══
VIDEO_COUNT=$(find "$PROJECT_DIR/users" -name "*.mp4" -o -name "*.mkv" -o -name "*.webm" 2>/dev/null | wc -l)
DISK_USED=$(du -sh "$PROJECT_DIR/users" 2>/dev/null | cut -f1)
YT_DLP_VER=$(python -c "import yt_dlp; print(yt_dlp.version.__version__)" 2>/dev/null)

echo -e "${WHITE}════════════════════════════════════════${NC}"
echo -e "  ${BOLD}📊 إحصائيات${NC}"
echo -e "  ${GREEN}🎬 فيديوهات محملة:${NC} ${VIDEO_COUNT:-0}"
echo -e "  ${GREEN}💾 مساحة مستخدمة:${NC} ${DISK_USED:-0}"
echo -e "  ${GREEN}🔧 إصدار yt-dlp:${NC}   v${YT_DLP_VER:-غير معروف}"
echo -e "${WHITE}════════════════════════════════════════${NC}"
echo ""

# ═══ عنوان السيرفر ═══
echo -e "${WHITE}════════════════════════════════════════${NC}"
echo -e "  ${BOLD}🌐 عناوين السيرفر${NC}"
echo -e "  ${GREEN}📱 شبكة محلية:${NC}  ${CYAN}${BOLD}${SERVER_URL}${NC}"
echo -e "  ${GREEN}💻 المتصفح:${NC}     ${CYAN}${LOCALHOST_URL}${NC}"
echo -e "${WHITE}════════════════════════════════════════${NC}"
echo ""

# ═══ QR Code ═══
if command -v qrencode &>/dev/null; then
    echo -e "${BOLD}${YELLOW}📲 امسح الـ QR Code بهاتف آخر على نفس الشبكة:${NC}"
    echo ""
    qrencode -t ANSIUTF8 -m 1 "$SERVER_URL"
    echo ""
elif python -c "import qrcode" 2>/dev/null; then
    echo -e "${BOLD}${YELLOW}📲 QR Code للاتصال من الشبكة المحلية:${NC}"
    echo ""
    python -c "
import qrcode, sys
url = sys.argv[1]
qr = qrcode.QRCode(border=1)
qr.add_data(url)
qr.make(fit=True)
qr.print_ascii(invert=True)
" "$SERVER_URL" 2>/dev/null
    echo ""
fi

# ═══ منصات مدعومة ═══
echo -e "${WHITE}════════════════════════════════════════${NC}"
echo -e "  ${BOLD}🎯 المنصات المدعومة${NC}"
echo -e "  ${RED}▶${NC} YouTube (حتى 4K)  ${YELLOW}▶${NC} TikTok"
echo -e "  ${PURPLE}▶${NC} Instagram         ${BLUE}▶${NC} Facebook"
echo -e "  ${CYAN}▶${NC} Twitter/X         ${GREEN}▶${NC} Vimeo & CapCut"
echo -e "${WHITE}════════════════════════════════════════${NC}"
echo ""

# ═══ تعليمات الإيقاف ═══
echo -e "  ${YELLOW}⚡ السيرفر يعمل... اضغط ${BOLD}Ctrl+C${NC}${YELLOW} لإيقافه${NC}"
echo -e "  ${YELLOW}📁 ملفاتك تُحفظ في:${NC} users/device_<IP>/downloads/"
echo ""

# ═══ تشغيل السيرفر ═══
python run.py

echo ""
echo -e "${RED}${BOLD}🛑 تم إيقاف السيرفر${NC}"
