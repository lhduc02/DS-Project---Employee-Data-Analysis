import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import streamlit as st
import base64
import plotly.express as px
import seaborn as sns
from collections import Counter

# Kết nối đến MySQL
# mydb = mysql.connector.connect(
#     host='localhost',
#     user='root',
#     password='mysql',
#     database='ds_db'
# )
# mycursor = mydb.cursor()

# sql_query = f"select * from jobs"
# mycursor.execute(sql_query)
# myresult = mycursor.fetchall()
# df = pd.read_sql(sql_query, mydb)


# Background
df = px.data.iris()

@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


# Title
original_title = '<p style="font-family:Arial; color:White; font-size: 32px; text-align: center; font-weight:600">PHÂN TÍCH THỊ TRƯỜNG VIỆC LÀM TRÊN CÁC NỀN TẢNG TUYỂN DỤNG</p>'
st.markdown(original_title, unsafe_allow_html=True)
st.write(" ")
st.write("  ")


# Main
data = pd.read_csv("D:\\.Repo\\Incomplete Project\\DS Project --- Labor market analysis\\cleaned_test.csv")


# Preprocess data
data['salary_min'] = data['salary_min'].fillna(0)
data['salary_max'] = data['salary_max'].fillna(0)
data['salary_avg'] = (data['salary_min'] + data['salary_max']) / 2


# Function to plot bar chart
def plot_bar_chart(x, y, title, xlabel, ylabel):
    fig, ax = plt.subplots()
    ax.barh(x, y, color='skyblue')
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    st.pyplot(fig)



# Thông tin chính
st.write("Số bản công việc thu thập được: 769")
st.write("Dữ liệu được tính từ ngày 10/04/2024 đến ngày 09/05/2024")
st.write(" ")
st.write("  ")



# Những vị trí công việc có nhu cầu cao nhất trong ngành CNTT
st.header("Nhu cầu lao động hiện tại")
job_counts = data['position_name'].value_counts().head(10).sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(job_counts.index, job_counts.values, color='skyblue')
for bar in bars:
    width = bar.get_width()
    ax.text(width, bar.get_y() + bar.get_height() / 2, f'{width}', ha='left', va='center')
ax.set_title('Top 10 vị trí công việc có nhu cầu cao trong ngành CNTT')
ax.set_xlabel('Số lượng công việc')
ax.set_ylabel('Vị trí công việc')
st.pyplot(fig)
st.write("""Từ biểu đồ trên, có thể thấy rằng những vị trí trong lĩnh vực phần mềm (như Developer, Business Analyst, Tester, Project Manager)
         vẫn đang rất hot và có nhu cầu cao ở thời điểm hiện tại thậm chí là trong tương lai xa hơn.""")
st.write(" ")
st.write("  ")



# Mức lương và phúc lợi hiện tại
st.header("Mức lương và phúc lợi hiện tại")
data_salary = data.dropna(subset=['salary_min', 'salary_max'])
data_salary['salary_min'] = pd.to_numeric(data_salary['salary_min'], errors='coerce')
data_salary['salary_max'] = pd.to_numeric(data_salary['salary_max'], errors='coerce')
# Tính toán lương trung bình
data_salary['average_salary'] = (data_salary['salary_min'] + data_salary['salary_max']) / 2
# Lọc dữ liệu để loại bỏ các hàng thiếu thông tin cần thiết
filtered_data = data_salary.dropna(subset=['position_name', 'average_salary'])
# Tính lương trung bình theo vị trí
average_salary_by_position = filtered_data.groupby('position_name')['average_salary'].mean()
job_counts_by_position = filtered_data['position_name'].value_counts()
average_salary_and_counts = average_salary_by_position.reset_index()
average_salary_and_counts.columns = ['Position', 'Average Salary']
average_salary_and_counts['Job Count'] = average_salary_and_counts['Position'].map(job_counts_by_position)
# Chuyển đổi tên công việc thành chữ thường để tìm kiếm
filtered_data['job_title_lower'] = filtered_data['job_title_separated'].str.lower()
count_junior = filtered_data[filtered_data['job_title_lower'].str.contains('junior', na=False)].groupby('position_name').size()
count_middle = filtered_data[filtered_data['job_title_lower'].str.contains('middle', na=False)].groupby('position_name').size()
count_senior = filtered_data[filtered_data['job_title_lower'].str.contains('senior', na=False)].groupby('position_name').size()
count_lead = filtered_data[filtered_data['job_title_lower'].str.contains('lead', na=False)].groupby('position_name').size()
# Thêm thông tin về số lượng vị trí công việc theo cấp độ
average_salary_and_counts['Count Junior'] = average_salary_and_counts['Position'].map(count_junior).fillna(0).astype(int)
average_salary_and_counts['Count Middle'] = average_salary_and_counts['Position'].map(count_middle).fillna(0).astype(int)
average_salary_and_counts['Count Senior'] = average_salary_and_counts['Position'].map(count_senior).fillna(0).astype(int)
average_salary_and_counts['Count Lead'] = average_salary_and_counts['Position'].map(count_lead).fillna(0).astype(int)
average_salary_and_counts['Rest'] = (average_salary_and_counts['Job Count'] - average_salary_and_counts['Count Junior'] - average_salary_and_counts['Count Middle'] - average_salary_and_counts['Count Senior'] - average_salary_and_counts['Count Lead']).astype(int)
average_salary_and_counts = average_salary_and_counts.dropna(subset=['Job Count']).sort_values(by='Job Count', ascending=False)
average_salary_and_counts['Average Salary'] = average_salary_and_counts['Average Salary'].round(1)

average_salary_and_counts.columns = ['Position', 'Avg Salary', 'Cnt Job', 'Cnt Junior', 'Cnt Middle', 'Cnt Senior', 'Cnt Lead', 'Rest']
top_10_positions = average_salary_and_counts.head(10)
st.dataframe(top_10_positions.set_index('Position').reset_index())


fig, ax = plt.subplots(figsize=(10, 6)) # Biểu đồ cột
ax.barh(top_10_positions['Position'], top_10_positions['Avg Salary'], color='lightgreen')
ax.set_xlabel('Mức lương trung bình (USD)')
ax.set_title('Top 10 vị trí có mức lương trung bình cao nhất')
st.pyplot(fig)
st.write(" ")
st.write("  ")



# Các kỹ năng đang được yêu cầu nhiều nhất
st.header("Các kỹ năng đang được yêu cầu nhiều nhất")
skills = data['skill'].str.get_dummies(sep=', ')
if 'Fresher Accepted' in skills.columns:
    skills = skills.drop(columns=['Fresher Accepted'])
skill_counts = skills.sum().sort_values(ascending=False).head(15)
total_jobs = len(data)
fig, ax = plt.subplots(figsize=(10, 6))
colors = ['skyblue'] * len(skill_counts)
colors[1] = 'red'
bars = ax.bar(skill_counts.index, skill_counts.values, color=colors)
for bar in bars:
    height = bar.get_height()
    percentage = (height / total_jobs) * 100
    ax.text(bar.get_x() + bar.get_width() / 2, height, f'{percentage:.1f}%', ha='center', va='bottom')
ax.set_title('Top 15 kỹ năng được yêu cầu nhiều nhất')
ax.set_xlabel('Kỹ năng')
ax.set_ylabel('Số lượng')
ax.set_xticklabels(skill_counts.index, rotation=45, ha='right')
st.pyplot(fig)
st.write("""Từ biểu đồ trên, có thể thấy rằng kỹ năng lập trình (như Java, JavaScript, Python,...) vẫn luôn được đặt lên hàng đầu.
         Cùng với đó, những trình độ Tiếng anh đang ngày càng trở nên quan trọng và trở thành điều kiện cần nếu ứng viên muốn nhận được công việc mà họ mong muốn.""")
st.write(" ")
st.write("  ")



# Phân loại hình công việc
st.subheader('Phân loại hình công việc')
fig1, ax1 = plt.subplots()
employment_type_counts = data['employment_type'].value_counts()
def format_label(pct, allvals):
    absolute = int(pct/100.*np.sum(allvals))
    return "{:.1f}%\n({:d})".format(pct, absolute)
colors = ['#FF9999', '#66B3FF', '#99FF99', '#FFCC99', '#FFD700', '#FF6347', '#FF69B4']
ax1.pie(employment_type_counts.values, labels=employment_type_counts.index, autopct=lambda pct: format_label(pct, employment_type_counts.values), colors=colors)
ax1.set_title('Phân loại hình công việc')
st.pyplot(fig1)
st.write("Từ biểu đồ tròn trên, có thể thấy rằng yêu cầu làm việc tại văn phòng chiếm tỷ lệ khá cao (77.8%).")
st.write("Cùng với đó, có một lượng không nhỏ công ty cho phép nhân viên có thể linh hoạt làm việc tại văn phòng hoặc từ xa (chiếm 20.3%).")
st.write("Hiện nay, mới chỉ có một số lượng rất ít công việc cho phép làm việc hoàn toàn từ xa (chỉ 2.0%). Điều này có thể đến từ việc các công ty cần sự giao tiếp trực tiếp giữa các nhân viên để tạo ra sự hiệu quả cao nhất trong công việc")
st.write(" ")
st.write("  ")



# Địa điểm tuyển dụng phổ biến
st.header("Địa điểm tuyển dụng phổ biến")
city_counts = data['city'].value_counts()
def format_label(pct, allvals):
    absolute = int(pct/100.*np.sum(allvals))
    return "{:.1f}%\n({:d})".format(pct, absolute)
fig, ax = plt.subplots()
colors = plt.cm.tab20.colors
ax.pie(city_counts.values, labels=city_counts.index, autopct=lambda pct: format_label(pct, city_counts.values), colors=colors)
st.pyplot(fig)
st.write("""Từ biểu đồ tròn trên, có thể thấy rằng TP.Hồ Chí Minh và Hà Nội là nơi có nhu cầu tuyển dụng lao động ngành CNTT khi chiếm tới 93.7% tổng số công việc.
         Trong đó, Tp. Hồ Chí Minh chiếm 63.3% và Hà Nội chiếm 30.4%. Còn lại, Đà Nẵng có 36 công việc chiếm tỷ lệ 4.9% còn lại là các tỉnh thành khác (1.4%).""")
st.write(" ")
st.write("  ")



# Yêu cầu kỹ năng và kinh nghiệm
st.header("Yêu cầu kỹ năng và kinh nghiệm")
def clean_job_titles(job_titles):
    split_titles = job_titles.str.split(r'[,/]', expand=True).stack().str.strip()
    return split_titles.reset_index(drop=True)
cleaned_titles = clean_job_titles(data['job_title_separated'])  # Đây là biểu đồ cột
experience_counts = cleaned_titles.value_counts().head(10)
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(experience_counts.index, experience_counts.values, color='skyblue')
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height}', ha='center', va='bottom')
ax.set_title('Yêu cầu kinh nghiệm')
ax.set_xlabel('Chức danh công việc')
ax.set_ylabel('Số lượng công việc')
ax.set_xticklabels(experience_counts.index, rotation=45, ha='right')
st.pyplot(fig)


cleaned_titles = clean_job_titles(data['job_title_separated'])  # Đây là biểu đồ tròn
top_titles = cleaned_titles.value_counts().nlargest(4)
other_titles_count = cleaned_titles.value_counts().iloc[4:].sum()
top_titles['Other'] = other_titles_count
def format_label(pct, allvals):
    absolute = int(pct/100.*np.sum(allvals))
    return "{:.1f}%\n({:d})".format(pct, absolute)
fig, ax = plt.subplots(figsize=(10, 6))
colors = plt.cm.tab20.colors
ax.pie(top_titles.values, labels=top_titles.index, autopct=lambda pct: format_label(pct, top_titles.values), colors=colors)
ax.set_title('Yêu cầu kinh nghiệm')
st.pyplot(fig)
st.write("""Hiện nay, các công ty thị trường lao động hiện tại đang thiên về việc tuyển dụng những ứng viên có nhiều kinh nghiệm, kỹ năng cao.
         Thị trường việc làm dành cho sinh viên mới ra trường hoặc những người ít kinh nghiệm là vô cùng cạnh tranh.""")
st.write(" ")
st.write("  ")



# Cơ hội cho người mới tốt nghiệp
st.header("Thị trường lao động cho người mới tốt nghiệp")
fresh_grad_positions = data[data['job_title_separated'].str.contains("Junior|Fresher", na=False)]
fresh_grad_counts = fresh_grad_positions['position_name'].value_counts().head(10)
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(fresh_grad_counts.index, fresh_grad_counts.values, color='skyblue')
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height}', ha='center', va='bottom')
ax.set_title('Cơ hội cho người mới tốt nghiệp')
ax.set_xlabel('Vị trí công việc')
ax.set_ylabel('Số lượng công việc')
ax.set_xticklabels(fresh_grad_counts.index, rotation=45, ha='right')

st.pyplot(fig)
st.write(" ")
st.write("  ")










