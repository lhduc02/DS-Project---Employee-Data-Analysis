# DS-Project---Employee-Data-Analysis

- Để chạy file code_crawl_data.py

+ Cài đặt python3: https://www.python.org/downloads/

+ Tải chromdriver: https://googlechromelabs.github.io/chrome-for-testing/#stable

+ Sau khi cài đặt python3, cài đặt pip: https://pip.pypa.io/en/stable/installation/

+ Cài đặt các module bằng câu lệnh sau trên terminal: python3 -m pip install selenium pandas jsonlib-python3 undetected-chromedriver beautifulsoup4 google-auth google-auth-oauthlib google-api-python-client mysql-connector-python

+ Tạo file Credentials của Google console để thực hiện việc upload dữ liệu lên Google Sheet: https://developers.google.com/sheets/api/quickstart/go?hl=vi

+ Chạy câu lệnh sau trên terminal để thực thi việc lấy dữ liệu: python3 code_crawl_data.py



- Để chạy file "Phân tích thị trường việc làm.py" cần đổi địa chỉ file "cleaned_test.csv" trong file Python sau đó chạy câu lệnh sau trên terminal:

streamlit run "địa chỉ file Phân tích thị trường việc làm.py"

Ví dụ: streamlit run "C:\DS Project --- Employee-Data-Analysis\Phân tích thị trường việc làm.py"
