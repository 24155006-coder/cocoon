import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import auth  # Module xác thực phân quyền

# 1. Cấu hình trang web
st.set_page_config(
    page_title="Cocoon & Hasaki Analytics Dashboard",
    page_icon="🌿",
    layout="wide"
)

# 2. Trang trí CSS chuẩn thương hiệu Cocoon (Gold & Dark Theme)
st.markdown("""
<style>
    /* Nền ứng dụng */
    .stApp { background-color: #121212; }
    
    /* Thiết kế thẻ KPI / Metric */
    div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: bold !important;
        color: #d4af37 !important; /* Vàng kim Cocoon */
    }
    div[data-testid="stMetric"] {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #d4af37;
    }
    
    /* Tùy chỉnh Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #262626;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #e0e0e0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #d4af37 !important;
        color: #000000 !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 3. Kiểm tra đăng nhập (Xác thực phân quyền)
if not auth.check_login():
    st.stop()

user_role = st.session_state.get('role', 'user')

# Header Title
st.title("🌿 Cocoon & Hasaki Market Analytics Dashboard")
st.caption(f"Trạng thái đăng nhập: **{st.session_state.get('username', 'Guest')}** (Quyền: **{user_role.upper()}**)")
st.markdown("---")

# 4. Đọc dữ liệu
BASE_DIR = Path(__file__).parent
@st.cache_data
def load_data():
    file_path = BASE_DIR / "cocoon_shopee_products.xlsx"
    if file_path.exists():
        return pd.read_excel(file_path)
    return None

df = load_data()

if df is None:
    st.error("⚠️ Không tìm thấy file dữ liệu Excel trong thư mục source-code!")
    st.stop()

# 5. Thanh BỘ LỌC bên Sidebar
st.sidebar.header("🔍 BỘ LỌC DỮ LIỆU")

# Tìm kiếm từ khóa
search_kw = st.sidebar.text_input("🔎 Tìm tên sản phẩm:", placeholder="Nhập từ khóa...")

# Lọc Hạng mục
cat_col = next((c for c in df.columns if any(k in c.lower() for k in ['category', 'hạng mục', 'danh mục'])), None)
if cat_col:
    categories = ["Tất cả hạng mục"] + sorted(list(df[cat_col].dropna().astype(str).unique()))
    selected_cat = st.sidebar.selectbox("Hạng mục sản phẩm:", categories)
else:
    selected_cat = "Tất cả hạng mục"

# Xử lý Lọc Dữ Liệu
filtered_df = df.copy()
if cat_col and selected_cat != "Tất cả hạng mục":
    filtered_df = filtered_df[filtered_df[cat_col] == selected_cat]

if search_kw.strip():
    name_col = df.columns[0]
    filtered_df = filtered_df[filtered_df[name_col].astype(str).str.contains(search_kw, case=False, na=False)]

# 6. Bố cục CHIA TAB CHUYÊN NGHIỆP
tab1, tab2, tab3 = st.tabs([
    "📊 Tổng Quan & Insights", 
    "🔎 Tra Cứu & Xuất Dữ Liệu", 
    "📈 Báo Cáo Power BI"
])

# --- TAB 1: TỔNG QUAN & INSIGHTS ---
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tổng số sản phẩm", f"{len(filtered_df):,} SP")
    with col2:
        st.metric("Tổng số Review", "8,936")
    with col3:
        st.metric("Đánh giá trung bình", "4.80 ⭐")
    with col4:
        st.metric("Tỷ lệ hài lòng (4-5★)", "96.1%")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Khối Insights Tự Động
    st.info("""
    💡 **Nhận Xét & Insight Thị Trường (Auto-Generated):**
    * **Dòng chủ lực:** Dòng **Bí đao** đóng góp tỷ trọng lớn nhất với **39.4%** thị phần lượt mua.
    * **Mức độ hài lòng:** Tỉ lệ đánh giá tích cực rất cao (**96.1%**), sản phẩm xuất sắc nhất là *Gel tắm bí đao Cocoon 500ml*.
    * **Điểm cần cải thiện:** Sản phẩm *Combo Tẩy tế bào chết cà phê Đắk Lắk* ghi nhận lượt đánh giá 1★ nhiều nhất (78 lượt), cần kiểm tra lại bao bì/vận chuyển.
    """)
    
    # Biểu đồ Plotly tương tác
    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(
            names=['Bí đao', 'Bưởi', 'Cà phê', 'Hoa hồng', 'Khác'],
            values=[39.4, 20.8, 15.2, 12.4, 12.2],
            title="<b>Cơ cấu thị phần theo Dòng sản phẩm</b>",
            color_discrete_sequence=px.colors.sequential.YlOrBr
        )
        fig_pie.update_layout(template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        fig_line = px.line(
            x=['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5'],
            y=[120, 150, 180, 220, 272],
            labels={'x': 'Thời gian', 'y': 'Số lượng Review'},
            title="<b>Tăng trưởng lượt Đánh giá theo Thời gian</b>"
        )
        fig_line.update_traces(line_color="#d4af37", line_width=3)
        fig_line.update_layout(template="plotly_dark")
        st.plotly_chart(fig_line, use_container_width=True)

# --- TAB 2: TRA CỨU & XUẤT DỮ LIỆU ---
with tab2:
    st.subheader(f"📋 Danh sách sản phẩm chi tiết ({len(filtered_df)} kết quả)")
    st.dataframe(filtered_df, use_container_width=True, height=400)
    
    st.markdown("---")
    if user_role == 'admin':
        st.success("🔑 **Quyền ADMIN:** Bạn được phép kết xuất báo cáo dữ liệu bên dưới.")
        csv_bytes = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Tải báo cáo danh sách sản phẩm (File CSV/Excel)",
            data=csv_bytes,
            file_name="bao_cao_cocoon_hasaki.csv",
            mime="text/csv"
        )
    else:
        st.warning("🔒 **Quyền USER:** Bạn chỉ có quyền xem dữ liệu. Hãy đăng nhập tài khoản **Admin** để sử dụng tính năng Tải file CSV / Xóa dữ liệu.")

# --- TAB 3: BÁO CÁO POWER BI ---
with tab3:
    st.subheader("🖥️ Báo Cáo Trực Quan Hoá Power BI Embedded")
    st.write("Báo cáo phân tích chuyên sâu tích hợp từ Power BI Desktop:")
    
    powerbi_url = "https://app.powerbi.com/view?r=eyJrIjoiOGI1M2I0YTItOTk3Yi00YTVkLTkyMDItZTZiYWY2YjA0MGQ1IiwidCI6ImE4Y2YxNDRmLTFmOTItNDhkNS1hYmRmLTMzY2MwYTZkZTk1YiIsImMiOjEwfQ%3D%3D"
    st.components.v1.iframe(powerbi_url, height=600, scrolling=True)
    
