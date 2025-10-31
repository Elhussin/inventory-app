# data_handlers.py
from utils.dp_utils import fetch_products 
from constants.index import DB_FILE
import sqlite3
# -------------------------
# Load / Insert helper
# -------------------------

def _format_cell_value(col, val):
    if val is None:
        val = ""
    if col in ("cost", "retail"):
        try:
            return f"{float(val):.2f}"
        except Exception:
            return "0.00"
    return val

def update_stats(stat_vars, total_required, total_good, total_damaged, total_gift, total_stock):
    stat_req_val, stat_good_val, stat_dam_val, stat_gift_val, stat_tot_val = stat_vars
    stat_req_val.config(text=f"{total_required:,}")
    stat_good_val.config(text=f"{total_good:,}")
    stat_dam_val.config(text=f"{total_damaged:,}")
    stat_gift_val.config(text=f"{total_gift:,}")
    stat_tot_val.config(text=f"{total_stock:,}")



# -------------------------
# وظيفة مساعدة لتحويل آمن
# -------------------------
def safe_int(r, key):
    """يسترجع القيمة كعدد صحيح (int) من صف SQLite Row، بمعالجة None، السلسلة الفارغة، أو الفشل."""
    # استخدام .get() مع row_factory=sqlite3.Row يعمل بشكل جيد
    val = r[key] 
    
    if val is None or val == "":
        return 0
    
    # محاولة التحويل المرن (float ثم int)
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return 0 # إرجاع صفر إذا كان التحويل غير ممكن (مثل نص غير متوقع)

# -------------------------
# Load Data
# -------------------------
def load_data(tree, search="", stat_vars=None, COLUMNS=None):
    """
    تحميل البيانات من قاعدة البيانات إلى Treeview وتحديث الإحصائيات.
    """
    tree.delete(*tree.get_children())
    total_required = total_good = total_damaged = total_gift = total_stock = 0
    
    # يجب التأكد من تمرير COLUMNS في main_app.py
    if COLUMNS is None:
        # إذا لم يتم تمرير COLUMNS، نستخدم المفاتيح المسترجعة، ولكن هذا ليس جيداً لتنسيق الجدول
        rows = fetch_products(search)
        if rows and len(rows) > 0:
            COLUMNS = rows[0].keys()
        else:
            COLUMNS = [] # لتجنب الخطأ في حلقة for
    else:
        rows = fetch_products(search)
    
    for idx, r in enumerate(rows):
        tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
        
        # استخدام COLUMNS لضمان الترتيب الصحيح للأعمدة في الجدول
        values = tuple(_format_cell_value(col, r[col]) for col in COLUMNS) 
        
        tree.insert("", "end", values=values, tags=(tag,))
        
        # استخدام الدالة الآمنة لتجميع الإحصائيات
        total_required += safe_int(r, "required_qty")
        total_good += safe_int(r, "good_qty")
        total_damaged += safe_int(r, "damaged_qty")
        total_gift += safe_int(r, "gift")
        total_stock += safe_int(r, "total_qty")
        
    if stat_vars:
        update_stats(stat_vars, total_required, total_good, total_damaged, total_gift, total_stock)


def search_products(tree, search_var, FIRST_EDITABLE_INDEX):
    """Focus first row in tree and optionally start editing."""
    search = search_var.get()
    # (هنا يجب عليك إعادة تحميل البيانات أولاً لضمان وجود نتائج محدثة)
    # load_data(tree, search, stat_vars) # تحتاج إلى تمرير stat_vars إذا كنت تريد تحديث الإحصائيات مع البحث
    
    children = tree.get_children()
    if not children:
        return "break"
    first = children[0]
    tree.selection_set(first)
    tree.focus(first)
    tree.see(first)
    tree.focus_set()  # give keyboard focus to tree

    # التأخير الصغير يضمن أن الـ Treeview استقر بعد تغيير الاختيار
    tree.after(50, lambda: tree.event_generate("<<EditCell>>", data=(first, FIRST_EDITABLE_INDEX)))

    return "break"


# db_operations.py / data_handlers.py

def update_product_full(product_id, data):
    # data هو قاموس يحتوي على جميع حقول الإدخال
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    print ("you call me")
    try:
        c.execute("""
            UPDATE products SET
               
                total_qty = ?, good_qty = ?, damaged_qty = ?, gift = ?, note = ?
            WHERE id = ?
        """, (
            data['total_qty'], data['good_qty'], data['damaged_qty'], data['gift'], data['note'],
            product_id
        ))
        conn.commit()
        print ("updated")
        conn.close()
    except Exception as e:
        print (e)


def fetch_product_by_id(product_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = c.fetchone()
    conn.close()
    return row # سيعيد كائن sqlite3.Row