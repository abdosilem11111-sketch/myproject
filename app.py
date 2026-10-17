import random
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="نظام إدارة مخازن مرسيدس - الفروع المتعددة",
    page_icon="🚗",
    layout="wide",
)

# --- تنسيقات التصميم (Custom CSS) ---
st.markdown(
    """
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div[data-testid="stForm"] { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    </style>
""",
    unsafe_allow_html=True,
)


# 2. إعداد قاعدة البيانات المركزية
@st.cache_resource
def get_database_connection():
  db_url = "sqlite:///mercedes_central_inventory.db"
  engine = create_engine(db_url)
  return engine


engine = get_database_connection()


# دالة لتوليد وتعبئة 500 صنف تلقائياً (تتم مرة واحدة لو الجدول فارغ)
def seed_inventory():
  import sqlite3

  local_conn = sqlite3.connect("mercedes_central_inventory.db")
  local_c = local_conn.cursor()

  local_c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            branch_name TEXT,
            oem_number TEXT,
            part_name TEXT,
            category TEXT,
            model_compat TEXT,
            quantity INTEGER,
            price REAL,
            location TEXT
        )
    """)

  local_c.execute("SELECT COUNT(*) FROM inventory")
  count = local_c.fetchone()[0]

  if count == 0:
    branches = [
        "الفرع الرئيسي - القاهرة",
        "فرع الإسكندرية",
        "فرع سموحة",
        "فرع الجيزة",
    ]

    parts_catalog = [
        (
            "تيل فرامل أمامي",
            "الفرامل",
            ["204", "212", "221", "205", "213"],
            "420",
            1500.0,
            4500.0,
        ),
        (
            "تيل فرامل خلفي",
            "الفرامل",
            ["204", "212", "221", "205", "213"],
            "421",
            1200.0,
            3800.0,
        ),
        (
            "طنبورة فرامل أمامية",
            "الفرامل",
            ["204", "212", "221", "213"],
            "421",
            2500.0,
            7500.0,
        ),
        (
            "حساس فرامل ABS",
            "الكهرباء والحساسات",
            ["204", "212", "205"],
            "540",
            800.0,
            2800.0,
        ),
        (
            "فلتر زيت المحرك",
            "زيوت وفلاتر",
            ["271", "274", "276", "651"],
            "180",
            350.0,
            950.0,
        ),
        (
            "فلتر هواء المحرك",
            "زيوت وفلاتر",
            ["271", "274", "276", "112"],
            "094",
            600.0,
            1800.0,
        ),
        (
            "فلتر تكييف كربون",
            "الصالون والكماليات",
            ["204", "212", "205", "213"],
            "830",
            700.0,
            2200.0,
        ),
        (
            "شمعة احتراق (بوجيه)",
            "المحرك",
            ["004", "270", "274"],
            "159",
            300.0,
            900.0,
        ),
        (
            "مساعد أمامي غاز",
            "العفشة والتعليق",
            ["204", "212", "221", "205"],
            "320",
            4500.0,
            13000.0,
        ),
        (
            "مساعد خلفي غاز",
            "العفشة والتعليق",
            ["204", "212", "221", "205"],
            "326",
            3800.0,
            11000.0,
        ),
        (
            "مقص سفلي أمامي",
            "العفشة والتعليق",
            ["204", "212", "205"],
            "330",
            3000.0,
            8500.0,
        ),
        (
            "بارة دركسيون خارجية",
            "العفشة والتعليق",
            ["204", "212", "205"],
            "338",
            1000.0,
            2800.0,
        ),
        (
            "طلمبة مياه المحرك",
            "المحرك",
            ["271", "274", "276"],
            "200",
            3200.0,
            9500.0,
        ),
        (
            "سير دينامو متعرج",
            "المحرك",
            ["001", "002", "003"],
            "993",
            600.0,
            2000.0,
        ),
        (
            "حساس حرارة المبرد",
            "الكهرباء والحساسات",
            ["000", "905", "004"],
            "542",
            750.0,
            2500.0,
        ),
        (
            "حساس أكسجين (إكمان)",
            "الكهرباء والحساسات",
            ["000", "905", "006"],
            "542",
            2200.0,
            6500.0,
        ),
        (
            "فانوس أمامي LED كامل",
            "الجسم الخارجي",
            ["204", "212", "205", "213"],
            "820",
            10000.0,
            32000.0,
        ),
        (
            "فانوس خلفي ليد",
            "الجسم الخارجي",
            ["204", "212", "205", "213"],
            "820",
            6000.0,
            19000.0,
        ),
        (
            "مرآة جانبية كهرباء",
            "الجسم الخارجي",
            ["204", "212", "205"],
            "810",
            4500.0,
            14000.0,
        ),
        (
            "موتور مساحات الزجاج",
            "الكهرباء والحساسات",
            ["204", "212", "205"],
            "820",
            2800.0,
            8500.0,
        ),
    ]

    models_map = {
        "204": "C-Class W204",
        "212": "E-Class W212",
        "221": "S-Class W221",
        "205": "C-Class W205",
        "213": "E-Class W213",
        "271": "C/E-Class M271",
        "274": "C/E-Class M274",
        "276": "S/E-Class M276",
        "651": "C/E-Class Diesel",
        "112": "E/S-Class M112",
        "270": "A/B-Class M270",
        "004": "جميع الموديلات",
        "000": "جميع الموديلات",
        "001": "جميع الموديلات",
        "002": "جميع الموديلات",
        "003": "جميع الموديلات",
        "905": "جميع الموديلات",
        "006": "جميع الموديلات",
    }

    sample_data = []
    used_oems = set()

    for branch in branches:
      for i in range(1, 126):  # 125 صنف لكل فرع = 500 صنف
        part = random.choice(parts_catalog)
        chassis = random.choice(part[2])
        group = part[3]

        while True:
          sub1 = f"{random.randint(0, 99):02d}"
          sub2 = f"{random.randint(0, 99):02d}"
          oem_code = f"A{chassis}{group}{sub1}{sub2}"
          if oem_code not in used_oems:
            used_oems.add(oem_code)
            break

        part_fullname = f"{part[0]} - دفعة #{i}"
        price = round(random.uniform(part[4], part[5]), 2)
        qty = random.randint(1, 25)
        category = part[1]
        model_compat = models_map.get(chassis, "Mercedes-Benz")
        location = f"الرف-{random.choice(['A','B','C','D'])}-{random.randint(1,8)}"

        sample_data.append((
            branch,
            oem_code,
            part_fullname,
            category,
            model_compat,
            qty,
            price,
            location,
        ))

    local_c.executemany(
        """
            INSERT INTO inventory (branch_name, oem_number, part_name, category, model_compat, quantity, price, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sample_data,
    )
    local_conn.commit()

  local_conn.close()


seed_inventory()

# --- القائمة الجانبية: اختيار الفرع والتنقل ---
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/9/90/Mercedes-Logo.svg",
    width=70,
)
st.sidebar.title("إدارة الفروع والمخزون")

branches = [
    "الفرع الرئيسي - القاهرة",
    "فرع الإسكندرية",
    "فرع سموحة",
    "فرع الجيزة",
]
selected_branch = st.sidebar.selectbox("📍 اختر الفرع الحالي:", branches)

st.sidebar.markdown("---")
menu = [
    "📊 لوحة مخزون الفرع",
    "🔄 صرف/بيع قطعة (تحديث فوري)",
    "➕ إضافة صنف جديد للفرع",
    "✏️ تعديل أسعار أو كميات ومواقع الأصناف",
    "🌐 عرض مخزون جميع الفروع",
    "⚠️ تقرير النقص المشترك",
]
choice = st.sidebar.selectbox("القائمة الرئيسية", menu)

# جلب بيانات الفرع الحالي من قاعدة البيانات
df_branch = pd.read_sql(
    "SELECT * FROM inventory WHERE branch_name = ?",
    engine,
    params=(selected_branch,),
)

# ---------------------------------------------------------
# 1. لوحة مخزون الفرع الحالي
# ---------------------------------------------------------
if choice == "📊 لوحة مخزون الفرع":
  st.title(f"📦 مخزون: {selected_branch}")

  col1, col2, col3 = st.columns(3)
  total_items = len(df_branch)
  total_qty = df_branch["quantity"].sum() if not df_branch.empty else 0
  total_val = (
      (df_branch["quantity"] * df_branch["price"]).sum()
      if not df_branch.empty
      else 0
  )

  col1.metric("عدد الأصناف", total_items)
  col2.metric("إجمالي القطع المتاحة", total_qty)
  col3.metric("قيمة مخزون الفرع (EGP)", f"{total_val:,.2f} ج.م")

  st.markdown("---")
  search_query = st.text_input(
      "🔍 بحث برقم القطعة (OEM) أو اسم القطعة في هذا الفرع:"
  )

  if search_query:
    query = """
            SELECT oem_number AS 'رقم OEM', part_name AS 'اسم القطعة', 
                   category AS 'التصنيف', model_compat AS 'الموديل', 
                   quantity AS 'الكمية', price AS 'السعر (EGP)', location AS 'الموقع' 
            FROM inventory WHERE branch_name = ? AND (oem_number LIKE ? OR part_name LIKE ?)
        """
    params = (selected_branch, f"%{search_query}%", f"%{search_query}%")
  else:
    query = """
            SELECT oem_number AS 'رقم OEM', part_name AS 'اسم القطعة', 
                   category AS 'التصنيف', model_compat AS 'الموديل', 
                   quantity AS 'الكمية', price AS 'السعر (EGP)', location AS 'الموقع' 
            FROM inventory WHERE branch_name = ?
        """
    params = (selected_branch,)

  df_display = pd.read_sql(query, engine, params=params)
  st.dataframe(df_display, use_container_width=True)

# ---------------------------------------------------------
# 2. صرف / بيع قطعة (تحديث فوري)
# ---------------------------------------------------------
elif choice == "🔄 صرف/بيع قطعة (تحديث فوري)":
  st.title("🔄 صرف أو بيع قطعة غيار")
  st.info(
      f"أنت تقوم بإجراء عملية داخل فرع: **{selected_branch}** (سيتم تحديث"
      " المخزون فوراً وتنبيه النظام المركزي)."
  )

  if df_branch.empty:
    st.warning("لا توجد أصناف مسجلة في هذا الفرع حالياً للإصدار أو البيع.")
  else:
    options = {
        f"{row['part_name']} (OEM: {row['oem_number']}) - المتاح: {row['quantity']}": row[
            "oem_number"
        ]
        for _, row in df_branch.iterrows()
    }

    selected_option = st.selectbox(
        "اختر القطعة المراد صرفها/بيعها:", list(options.keys())
    )
    oem_to_sell = options[selected_option]

    current_qty = df_branch[df_branch["oem_number"] == oem_to_sell][
        "quantity"
    ].values[0]

    sold_qty = st.number_input(
        "الكمية المراد سحبها/بيعها:", min_value=1, max_value=int(current_qty), value=1
    )

    if st.button("تأكيد عملية الصرف/البيع", type="primary"):
      new_quantity = current_qty - sold_qty

      with engine.connect() as conn:
        conn.execute(
            "UPDATE inventory SET quantity = ? WHERE branch_name = ? AND"
            " oem_number = ?",
            (new_quantity, selected_branch, oem_to_sell),
        )
        conn.commit()

      st.success(
          f"✅ تم صرف عدد ({sold_qty}) بنجاح. الكمية المتبقية الآن في الفرع:"
          f" {new_quantity}"
      )
      st.rerun()

# ---------------------------------------------------------
# 3. إضافة صنف جديد للفرع
# ---------------------------------------------------------
elif choice == "➕ إضافة صنف جديد للفرع":
  st.title(f"➕ إضافة صنف جديد إلى مخزن: {selected_branch}")

  with st.form("add_branch_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
      oem = st.text_input(
          "رقم القطعة (OEM Number)*", placeholder="A2044200120"
      ).strip()
      name = st.text_input(
          "اسم القطعة*", placeholder="حساس حرارة / Brake Pads"
      ).strip()
      category = st.selectbox(
          "التصنيف*",
          [
              "المحرك",
              "العفشة والتعليق",
              "الفرامل",
              "الكهرباء والحساسات",
              "الجسم الخارجي",
              "الصالون والكماليات",
              "زيوت وفلاتر",
          ],
      )
    with col2:
      model = st.text_input("الموديلات المتوافقة", placeholder="C-Class W204")
      qty = st.number_input("الكمية المتاحة في الفرع", min_value=0, value=5)
      price = st.number_input("سعر البيع (EGP)", min_value=0.0, value=1500.0)
      loc = st.text_input("موقع التخزين داخل الفرع", placeholder="الرف A-2")

    submit = st.form_submit_button(
        "حفظ وإضافة الصنف للفرع", use_container_width=True
    )

    if submit:
      if oem and name:
        check_exist = pd.read_sql(
            "SELECT * FROM inventory WHERE branch_name = ? AND oem_number = ?",
            engine,
            params=(selected_branch, oem),
        )
        if not check_exist.empty:
          st.error("❌ رقم القطعة OEM مسجل مسبقاً في هذا الفرع!")
        else:
          with engine.connect() as conn:
            conn.execute(
                """
                            INSERT INTO inventory (branch_name, oem_number, part_name, category, model_compat, quantity, price, location)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                (
                    selected_branch,
                    oem,
                    name,
                    category,
                    model,
                    qty,
                    price,
                    loc,
                ),
            )
            conn.commit()
          st.success(f"✅ تمت إضافة القطعة ({name}) إلى {selected_branch} بنجاح!")
          st.rerun()
      else:
        st.warning("⚠️ يرجى ملء الحقول الإجبارية (*)")

# ---------------------------------------------------------
# 4. تعديل أسعار أو كميات ومواقع الأصناف
# ---------------------------------------------------------
elif choice == "✏️ تعديل أسعار أو كميات ومواقع الأصناف":
  st.title(f"✏️ تعديل بيانات صنف في مخزن: {selected_branch}")
  st.info(
      "من هنا يمكنك تعديل السعر، الكمية الحالية، أو مكان التخزين (الرف) لأي صنف"
      " في الفرع."
  )

  if df_branch.empty:
    st.warning("لا توجد أصناف في هذا الفرع للتعديل عليها.")
  else:
    edit_options = {
        f"{row['part_name']} (OEM: {row['oem_number']})": row["oem_number"]
        for _, row in df_branch.iterrows()
    }
    selected_edit_item = st.selectbox(
        "اختر الصنف المراد تعديله:", list(edit_options.keys())
    )
    target_oem = edit_options[selected_edit_item]

    # جلب بيانات الصنف الحالي
    item_row = df_branch[df_branch["oem_number"] == target_oem].iloc[0]

    with st.form("edit_form"):
      new_price = st.number_input(
          "السعر الجديد (EGP):",
          min_value=0.0,
          value=float(item_row["price"]),
      )
      new_qty = st.number_input(
          "الكمية الحالية الجديدة:",
          min_value=0,
          value=int(item_row["quantity"]),
      )
      new_loc = st.text_input(
          "موقع التخزين الجديد (الرف):", value=str(item_row["location"])
      )

      save_changes = st.form_submit_button(
          "حفظ التعديلات", use_container_width=True
      )

      if save_changes:
        with engine.connect() as conn:
          conn.execute(
              """
                        UPDATE inventory 
                        SET price = ?, quantity = ?, location = ? 
                        WHERE branch_name = ? AND oem_number = ?
                    """,
              (new_price, new_qty, new_loc, selected_branch, target_oem),
          )
          conn.commit()
        st.success("✅ تم تحديث بيانات الصنف بنجاح!")
        st.rerun()

# ---------------------------------------------------------
# 5. عرض مخزون جميع الفروع
# ---------------------------------------------------------
elif choice == "🌐 عرض مخزون جميع الفروع":
  st.title("🌐 الرؤية الشاملة لمخازن جميع الفروع")
  st.write(
      "من خلال هذه الشاشة يمكنك رؤية الكميات المتاحة من نفس القطعة في كل فرع:"
  )

  df_all_branches = pd.read_sql("SELECT * FROM inventory", engine)

  if df_all_branches.empty:
    st.info("لا توجد بيانات مسجلة في أي فرع حتى الآن.")
  else:
    search_all = st.text_input("🔍 بحث عام عن قطعة في كل الفروع:")
    if search_all:
      df_all_branches = df_all_branches[
          df_all_branches["oem_number"].str.contains(
              search_all, case=False, na=False
          )
          | df_all_branches["part_name"].str.contains(
              search_all, case=False, na=False
          )
      ]

    df_all_branches = df_all_branches[
        [
            "branch_name",
            "oem_number",
            "part_name",
            "category",
            "model_compat",
            "quantity",
            "price",
            "location",
        ]
    ]
    df_all_branches.columns = [
        "اسم الفرع",
        "رقم OEM",
        "اسم القطعة",
        "التصنيف",
        "الموديل",
        "الكمية",
        "السعر (EGP)",
        "الموقع",
    ]
    st.dataframe(df_all_branches, use_container_width=True)

# ---------------------------------------------------------
# 6. تقرير النقص المشترك
# ---------------------------------------------------------
elif choice == "⚠️ تقرير النقص المشترك":
  st.title("⚠️ تقرير النقص عبر جميع الفروع (أقل من 3 قطع)")

  df_low_all = pd.read_sql(
      "SELECT branch_name AS 'الفرع', oem_number AS 'رقم OEM', part_name AS"
      " 'اسم القطعة', quantity AS 'الكمية المتبقية' FROM inventory WHERE"
      " quantity < 3",
      engine,
  )

  if not df_low_all.empty:
    st.warning("الأصناف التالية في الفروع المختلفة بحاجة لإعادة توريد:")
    st.dataframe(df_low_all, use_container_width=True)
  else:
    st.success("🎉 جميع الفروع تمتلك كميات آمنة ولا يوجد نقص حالياً!")