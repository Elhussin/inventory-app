import pandas as pd

def update_or_add_required_qty(old_csv, new_csv, output_csv):
    old_df = pd.read_csv(old_csv, encoding='utf-8-sig')
    new_df = pd.read_csv(new_csv, encoding='utf-8-sig')

    updated_df = old_df.merge(
        new_df[['code', 'required_qty']],
        on='code',
        how='outer',
        suffixes=('', '_new'),
        indicator=True
    )

    # تحديث القيم القديمة بالقيم الجديدة عند التطابق
    updated_df['required_qty'] = updated_df['required_qty_new'].combine_first(updated_df['required_qty'])
    updated_df.drop(columns=['required_qty_new'], inplace=True)

    # لو في صفوف جديدة (تظهر كـ '_merge' == 'right_only') نملأ باقي الأعمدة الفارغة بقيم افتراضية
    for col in old_df.columns:
        if col not in updated_df.columns:
            updated_df[col] = ""

    # إعادة ترتيب الأعمدة بنفس ترتيب الملف القديم
    updated_df = updated_df[old_df.columns]

    # حفظ النتيجة
    updated_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"✅ تم التحديث بنجاح، والملف الناتج جاهز: {output_csv}")



# مثال للتشغيل
if __name__ == "__main__":
    update_or_add_required_qty(
        old_csv="old.csv",
        new_csv="new.csv",
        output_csv="updated.csv"
    )
