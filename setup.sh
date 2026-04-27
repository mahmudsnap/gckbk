#!/data/data/com.termux/files/usr/bin/bash
# ╔══════════════════════════════════════════════════════╗
# ║     SnapYTube Ultimate — إعداد تلقائي كامل           ║
# ║     نسخة Termux | يعمل من الصفر                      ║
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
NC='\033[0m' # No Color

# ═══ الشعار ═══
clear
echo ""
echo -e "${PURPLE}${BOLD}"
echo "  ███████╗███╗   ██╗ █████╗ ██████╗ "
echo "  ██╔════╝████╗  ██║██╔══██╗██╔══██╗"
echo "  ███████╗██╔██╗ ██║███████║██████╔╝"
echo "  ╚════██║██║╚██╗██║██╔══██║██╔═══╝ "
echo "  ███████║██║ ╚████║██║  ██║██║     "
echo "  ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     "
echo -e "${CYAN}       YouTube Ultimate Downloader v4${NC}"
echo ""
echo -e "${WHITE}════════════════════════════════════════${NC}"
echo -e "${YELLOW}  📦 جاري إعداد البيئة الكاملة...${NC}"
echo -e "${WHITE}════════════════════════════════════════${NC}"
echo ""

# ═══ مسار المشروع ═══
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# ═══ دالة الطباعة المنسقة ═══
ok()   { echo -e "  ${GREEN}✅${NC} $1"; }
info() { echo -e "  ${CYAN}ℹ️ ${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠️ ${NC} $1"; }
err()  { echo -e "  ${RED}❌${NC} $1"; }
step() { echo -e "\n${BOLD}${BLUE}▶ $1${NC}"; }

# ═══ فحص إذا كان Termux ═══
if [ ! -d "/data/data/com.termux" ]; then
    warn "لم يتم اكتشاف Termux — جاري التشغيل كـ Linux عادي"
    PKG_CMD="apt-get"
    PIP_FLAG=""
else
    PKG_CMD="pkg"
    PIP_FLAG="--break-system-packages"
fi

# ═══════════════════════════════
# الخطوة 1: تحديث المستودعات
# ═══════════════════════════════
step "تحديث مستودعات Termux"
$PKG_CMD update -y -q 2>/dev/null | tail -1
ok "تم تحديث المستودعات"

# ═══════════════════════════════
# الخطوة 2: تثبيت حزم النظام
# ═══════════════════════════════
step "تثبيت حزم النظام المطلوبة"

SYSTEM_PKGS=("python" "ffmpeg" "git" "curl" "libzmq" "libjpeg-turbo")

for pkg in "${SYSTEM_PKGS[@]}"; do
    if ! command -v "$pkg" &>/dev/null && ! $PKG_CMD list-installed 2>/dev/null | grep -q "^$pkg"; then
        echo -ne "  ${CYAN}📥 تثبيت ${pkg}...${NC}"
        $PKG_CMD install -y -q "$pkg" 2>/dev/null
        echo -e " ${GREEN}✓${NC}"
    else
        ok "$pkg موجود مسبقاً"
    fi
done

# qrencode اختياري
if command -v qrencode &>/dev/null; then
    ok "qrencode موجود"
else
    echo -ne "  ${CYAN}📥 تثبيت qrencode (اختياري)...${NC}"
    $PKG_CMD install -y -q qrencode 2>/dev/null && echo -e " ${GREEN}✓${NC}" || echo -e " ${YELLOW}تخطي${NC}"
fi

# ═══════════════════════════════
# الخطوة 3: تثبيت حزم Python
# ═══════════════════════════════
step "تثبيت مكتبات Python"

# ترقية pip أولاً
echo -ne "  ${CYAN}🐍 ترقية pip...${NC}"
python -m pip install --upgrade pip -q $PIP_FLAG 2>/dev/null
echo -e " ${GREEN}✓${NC}"

# تثبيت المكتبات
PY_PKGS=(
    "flask>=2.3.0"
    "flask-cors>=4.0.0"
    "yt-dlp>=2024.0.0"
    "qrcode[pil]"
    "requests"
)

for pkg in "${PY_PKGS[@]}"; do
    pkg_name=$(echo "$pkg" | sed 's/[>=\[].*//')
    echo -ne "  ${CYAN}📦 ${pkg_name}...${NC}"
    pip install "$pkg" -q $PIP_FLAG 2>/dev/null
    echo -e " ${GREEN}✓${NC}"
done

# ═══════════════════════════════
# الخطوة 4: تحديث yt-dlp
# ═══════════════════════════════
step "تحديث yt-dlp للإصدار الأحدث"
echo -ne "  ${CYAN}🔄 تحديث yt-dlp...${NC}"
pip install -U yt-dlp -q $PIP_FLAG 2>/dev/null
YT_DLP_VER=$(python -c "import yt_dlp; print(yt_dlp.version.__version__)" 2>/dev/null)
echo -e " ${GREEN}✓ v${YT_DLP_VER}${NC}"

# ═══════════════════════════════
# الخطوة 5: إنشاء المجلدات
# ═══════════════════════════════
step "إنشاء هيكل المجلدات"
mkdir -p logs cache users templates static
ok "تم إنشاء المجلدات الأساسية"

# ═══════════════════════════════
# الخطوة 6: فحص الملفات
# ═══════════════════════════════
step "فحص ملفات المشروع"

REQUIRED=("run.py" "config.py" "downloader.py" "index.html")
ALL_OK=true

for f in "${REQUIRED[@]}"; do
    if [ -f "$f" ]; then
        ok "$f موجود"
    else
        err "$f مفقود!"
        ALL_OK=false
    fi
done

if [ "$ALL_OK" = false ]; then
    echo ""
    err "ملفات مفقودة! تأكد من أن كل الملفات موجودة في نفس المجلد"
    exit 1
fi

# ═══════════════════════════════
# الخطوة 7: فحص ffmpeg
# ═══════════════════════════════
step "فحص ffmpeg"
if command -v ffmpeg &>/dev/null; then
    FFMPEG_VER=$(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')
    ok "ffmpeg v${FFMPEG_VER} جاهز"
else
    warn "ffmpeg غير موجود! بعض الفيديوهات لن تُدمج بشكل صحيح"
    warn "شغّل: pkg install ffmpeg"
fi

# ═══════════════════════════════
# النهاية: الإعداد تم
# ═══════════════════════════════
echo ""
echo -e "${WHITE}════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  🎉 اكتمل الإعداد بنجاح!${NC}"
echo -e "${WHITE}════════════════════════════════════════${NC}"
echo ""
echo -e "  لتشغيل السيرفر:"
echo -e "  ${BOLD}${CYAN}bash start.sh${NC}"
echo ""
