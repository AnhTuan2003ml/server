# 📚 Hướng Dẫn Sử Dụng API Payment Service

## 🎯 Giới thiệu

Payment API Service là một Flask API đơn giản để tạo QR code thanh toán và xử lý các giao dịch thanh toán từ SePay. API hỗ trợ CORS và có thể truy cập từ mạng nội bộ hoặc qua ngrok tunnel.

## 🚀 Khởi động Server

### Yêu cầu hệ thống
- Python 3.6+
- Flask
- Ngrok (đã cài đặt và cấu hình)
- Các thư viện khác (xem `requirements.txt`)

### Cách chạy

**Bước 1: Mở PowerShell với quyền Administrator**
- Nhấn `Windows + X` và chọn "Windows PowerShell (Admin)" hoặc "Terminal (Admin)"
- Hoặc tìm kiếm "PowerShell" trong Start Menu, click chuột phải và chọn "Run as administrator"

**Bước 2: Chạy Ngrok để tạo tunnel**
```powershell
ngrok http 5000
```

> **Lưu ý:** Ngrok sẽ hiển thị URL công khai (ví dụ: `https://xxxx-xx-xxx-xxx-xxx.ngrok-free.app`). Sao chép URL này và cập nhật vào file `api.txt` nếu cần.

**Bước 3: Mở terminal/PowerShell mới và chạy Python server**
```powershell
python main.py
```

> **Lưu ý:** Giữ cả 2 cửa sổ terminal mở:
> - Terminal 1: Chạy ngrok (giữ nguyên)
> - Terminal 2: Chạy Python server (giữ nguyên)

### Thông tin Server

Sau khi khởi động, server sẽ chạy trên:
- **Local:** `http://localhost:5000`
- **Mạng nội bộ:** `http://<IP_LOCAL>:5000`
- **Ngrok URL:** `https://xxxx-xx-xxx-xxx-xxx.ngrok-free.app` (từ ngrok terminal)

IP local sẽ được hiển thị khi khởi động server.

### Dừng Server

Để dừng server:
1. Nhấn `Ctrl + C` trong terminal đang chạy Python server
2. Nhấn `Ctrl + C` trong terminal đang chạy ngrok

---

## 📋 Danh Sách Endpoints

### 1. GET `/qr` - Tạo QR Code Thanh Toán

Tạo và trả về ảnh QR code để thanh toán. API trả về `id` kèm theo QR code trong header hoặc JSON response.

#### Request
```
GET /qr?sl=<số_lượng>&format=<format>
```

**Query Parameters:**
- `sl` (optional): Số lượng để tính toán số tiền trong QR code. Phải là số nguyên.
- `format` (optional): Định dạng trả về. Mặc định là `image`. Dùng `json` để nhận JSON với `id` và `qr_code` base64.

#### Ví dụ Request

**Không có tham số (trả về image):**
```bash
curl http://localhost:5000/qr
```

**Có tham số sl (trả về image):**
```bash
curl http://localhost:5000/qr?sl=50
```

**Trả về JSON với id và qr_code:**
```bash
curl http://localhost:5000/qr?format=json
curl http://localhost:5000/qr?sl=50&format=json
```

**JavaScript/Fetch - Lấy image và id từ header:**
```javascript
// Không có tham số
fetch('http://localhost:5000/qr')
  .then(response => {
    const id = response.headers.get('X-QR-ID');
    console.log('QR ID:', id);
    return response.blob();
  })
  .then(blob => {
    const url = URL.createObjectURL(blob);
    const img = document.createElement('img');
    img.src = url;
    document.body.appendChild(img);
  });

// Có tham số sl
fetch('http://localhost:5000/qr?sl=50')
  .then(response => {
    const id = response.headers.get('X-QR-ID');
    console.log('QR ID:', id);
    return response.blob();
  })
  .then(blob => {
    const url = URL.createObjectURL(blob);
    const img = document.createElement('img');
    img.src = url;
    document.body.appendChild(img);
  });
```

**JavaScript/Fetch - Lấy JSON với id và qr_code:**
```javascript
// Lấy JSON response
fetch('http://localhost:5000/qr?format=json')
  .then(response => response.json())
  .then(data => {
    console.log('QR ID:', data.id);
    console.log('SL:', data.sl);
    // Hiển thị QR code từ base64
    const img = document.createElement('img');
    img.src = data.qr_code;
    document.body.appendChild(img);
  });

// Có tham số sl
fetch('http://localhost:5000/qr?sl=50&format=json')
  .then(response => response.json())
  .then(data => {
    console.log('QR ID:', data.id);
    console.log('SL:', data.sl);
    const img = document.createElement('img');
    img.src = data.qr_code;
    document.body.appendChild(img);
  });
```

**HTML:**
```html
<!-- Không có tham số -->
<img src="http://localhost:5000/qr" alt="QR Code" />

<!-- Có tham số sl -->
<img src="http://localhost:5000/qr?sl=50" alt="QR Code" />
```

**Python requests - Lấy id từ header:**
```python
import requests

response = requests.get('http://localhost:5000/qr?sl=50')
qr_id = response.headers.get('X-QR-ID')
print(f'QR ID: {qr_id}')

# Lưu ảnh QR code
with open(f'qr_{qr_id}.png', 'wb') as f:
    f.write(response.content)
```

**Python requests - Lấy JSON response:**
```python
import requests
import base64

response = requests.get('http://localhost:5000/qr?sl=50&format=json')
data = response.json()
print(f'QR ID: {data["id"]}')
print(f'SL: {data["sl"]}')

# Lưu ảnh QR code từ base64
qr_base64 = data['qr_code'].split(',')[1]  # Bỏ phần 'data:image/png;base64,'
with open(f'qr_{data["id"]}.png', 'wb') as f:
    f.write(base64.b64decode(qr_base64))
```

#### Response

**Thành công - Image format (200):**
- Content-Type: `image/png`
- Body: Ảnh QR code (PNG format)
- Headers:
  - `Content-Disposition: inline; filename=qr_<id>.png`
  - `X-QR-ID`: ID của QR code (20 ký tự ngẫu nhiên)
  - `Cache-Control: no-cache`
  - `Access-Control-Allow-Origin: *`
  - `Access-Control-Expose-Headers: X-QR-ID`

**Thành công - JSON format (200):**
```json
{
  "success": true,
  "id": "id0c0nUPf3rjZwzpA3yD",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "sl": 50
}
```

**Lỗi (400):**
```json
{
  "success": false,
  "message": "Tham số 'sl' phải là số nguyên, nhận được: abc"
}
```

**Lỗi Server (500):**
```json
{
  "success": false,
  "message": "Mô tả lỗi"
}
```

---

### 2. POST `/authentication` - Xử Lý Thanh Toán Từ SePay

API endpoint nhận callback từ SePay khi có giao dịch thanh toán và xử lý thanh toán.

#### Request
```
POST /authentication
Content-Type: application/json
```

**Body JSON:**
```json
{
  "id": 92704,
  "gateway": "Vietcombank",
  "transactionDate": "2023-03-25 14:02:37",
  "accountNumber": "0123499999",
  "code": null,
  "content": "id0c0nUPf3rjZwzpA3yD50",
  "transferType": "in",
  "transferAmount": 2277000,
  "accumulated": 19077000,
  "subAccount": null,
  "referenceCode": "MBVCB.3278907687",
  "description": ""
}
```

**Trường bắt buộc:**
- `content`: Chuỗi ký tự chứa `id_sl` (20 ký tự đầu là id, phần còn lại là sl)
- `transferAmount`: Số tiền thanh toán (số nguyên)

**Các trường khác:** Tùy chọn

#### Ví dụ Request

**cURL:**
```bash
curl -X POST http://localhost:5000/authentication \
  -H "Content-Type: application/json" \
  -d '{
    "content": "id0c0nUPf3rjZwzpA3yD50",
    "transferAmount": 2277000,
    "gateway": "Vietcombank",
    "transactionDate": "2023-03-25 14:02:37"
  }'
```

**JavaScript/Fetch:**
```javascript
fetch('http://localhost:5000/authentication', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    content: "id0c0nUPf3rjZwzpA3yD50",
    transferAmount: 2277000,
    gateway: "Vietcombank",
    transactionDate: "2023-03-25 14:02:37"
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Python requests:**
```python
import requests

url = "http://localhost:5000/authentication"
data = {
    "content": "id0c0nUPf3rjZwzpA3yD50",
    "transferAmount": 2277000,
    "gateway": "Vietcombank",
    "transactionDate": "2023-03-25 14:02:37"
}

response = requests.post(url, json=data)
print(response.json())
```

#### Response

**Thành công (200):**
```json
{
  "success": true,
  "message": "Thanh toán thành công",
  "data": {
    "id": "id0c0nUPf3rjZwzpA3yD",
    "sl": 50,
    "pay_ment": 2277000,
    "cost": 45540.0,
    "message": "Thanh toán thành công"
  }
}
```

**Lỗi - Thiếu trường (400):**
```json
{
  "success": false,
  "message": "Thiếu trường 'content' trong JSON body"
}
```

**Lỗi Server (500):**
```json
{
  "success": false,
  "message": "Mô tả lỗi",
  "data": null
}
```

---

### 3. POST `/add_count` - Chuẩn Bị Tăng Count Cho Tài Khoản

API endpoint để chuẩn bị tăng count cho tài khoản theo id với cơ chế verify. Request sẽ được lưu vào hàng đợi tạm thời và chỉ được thực hiện khi verify thành công.

**Giới hạn sử dụng:** Tổng số count hiện tại + số request pending không được vượt quá limit của tài khoản. Nếu vượt quá, sẽ không tạo được request mới.

#### Request
```
POST /add_count
Content-Type: application/json
```

**Body JSON:**
```json
{
  "id": "id0c0nUPf3rjZwzpA3yD"
}
```

**Trường bắt buộc:**
- `id`: ID của tài khoản cần tăng count (phải là chuỗi)

#### Ví dụ Request

**cURL:**
```bash
curl -X POST http://localhost:5000/add_count \
  -H "Content-Type: application/json" \
  -d '{
    "id": "id0c0nUPf3rjZwzpA3yD"
  }'
```

**JavaScript/Fetch:**
```javascript
fetch('http://localhost:5000/add_count', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    id: "id0c0nUPf3rjZwzpA3yD"
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Python requests:**
```python
import requests

url = "http://localhost:5000/add_count"
data = {
    "id": "id0c0nUPf3rjZwzpA3yD"
}

response = requests.post(url, json=data)
print(response.json())
```

#### Response

**Thành công - Tạo request pending (200):**
```json
{
  "success": true,
  "message": "Đã tạo request tăng count. Vui lòng verify với request_id: 123e4567-e89b-12d3-a456-426614174000",
  "data": {
    "request_id": "123e4567-e89b-12d3-a456-426614174000",
    "id": "id0c0nUPf3rjZwzpA3yD",
    "count": 0,
    "limit": 1,
    "active": true,
    "status": "pending"
  }
}
```

**Lỗi - Thiếu trường (400):**
```json
{
  "success": false,
  "message": "Thiếu trường 'id' trong JSON body"
}
```

**Lỗi - ID không phải chuỗi (400):**
```json
{
  "success": false,
  "message": "Trường 'id' phải là chuỗi, nhận được: number"
}
```

**Lỗi - Tài khoản bị khoá (400):**
```json
{
  "success": false,
  "message": "Tài khoản bị khoá",
  "data": {
    "error_code": "ACCOUNT_LOCKED",
    "id": "id0c0nUPf3rjZwzpA3yD",
    "active": false
  }
}
```

**Lỗi - Tài khoản hết lượt (400):**
```json
{
  "success": false,
  "message": "Tài khoản bị hết lượt và đã được xóa",
  "data": {
    "error_code": "ACCOUNT_LIMIT_EXCEEDED",
    "id": "id0c0nUPf3rjZwzpA3yD",
    "count": 2,
    "limit": 1
  }
}
```

**Lỗi - Đã đạt giới hạn sử dụng (400):**
```json
{
  "success": false,
  "message": "Tài khoản đã đạt giới hạn sử dụng. Count hiện tại: 8, Pending requests: 2, Limit: 10",
  "data": {
    "error_code": "ACCOUNT_LIMIT_REACHED",
    "id": "id0c0nUPf3rjZwzpA3yD",
    "count": 8,
    "pending_count": 2,
    "limit": 10,
    "total_used": 10
  }
}
```

**Lỗi - Không tìm thấy tài khoản (500):**
```json
{
  "success": false,
  "message": "Không tìm thấy tài khoản với id: id0c0nUPf3rjZwzpA3yD"
}
```

**Lỗi Server (500):**
```json
{
  "success": false,
  "message": "Mô tả lỗi",
  "data": null
}
```

---

### 4. POST `/verify_count` - Verify Request Tăng Count

API endpoint để xác nhận hoặc hủy request tăng count đã được tạo trước đó. Chỉ khi verify với `approved: true` thì count mới được tăng thực sự.

#### Request
```
POST /verify_count
Content-Type: application/json
```

**Body JSON:**
```json
{
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "approved": true
}
```

**Trường bắt buộc:**
- `request_id`: ID của request cần verify (phải là chuỗi UUID)
- `approved`: Quyết định xử lý (phải là boolean)
  - `true`: Thực hiện tăng count
  - `false`: Hủy request

#### Ví dụ Request

**cURL:**
```bash
curl -X POST http://localhost:5000/verify_count \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "123e4567-e89b-12d3-a456-426614174000",
    "approved": true
  }'
```

**JavaScript/Fetch:**
```javascript
fetch('http://localhost:5000/verify_count', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    request_id: "123e4567-e89b-12d3-a456-426614174000",
    approved: true
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Python requests:**
```python
import requests

url = "http://localhost:5000/verify_count"
data = {
    "request_id": "123e4567-e89b-12d3-a456-426614174000",
    "approved": true
}

response = requests.post(url, json=data)
print(response.json())
```

#### Response

**Thành công - Approve (200):**
```json
{
  "success": true,
  "message": "Đã tăng count thành công. Count hiện tại: 1",
  "data": {
    "request_id": "123e4567-e89b-12d3-a456-426614174000",
    "id": "id0c0nUPf3rjZwzpA3yD",
    "count": 1,
    "limit": 10,
    "active": true,
    "status": "completed"
  }
}
```

**Thành công - Reject (200):**
```json
{
  "success": true,
  "message": "Đã hủy request 123e4567-e89b-12d3-a456-426614174000",
  "data": {
    "request_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "cancelled"
  }
}
```

**Lỗi - Request không tồn tại (400):**
```json
{
  "success": false,
  "message": "Không tìm thấy request với ID: 123e4567-e89b-12d3-a456-426614174000"
}
```

**Lỗi - Request đã xử lý (400):**
```json
{
  "success": false,
  "message": "Request đã được xử lý với trạng thái: completed"
}
```

---

### 5. POST `/check` - Kiểm Tra Trạng Thái Tài Khoản

API endpoint để kiểm tra trạng thái tài khoản theo id. Kiểm tra xem tài khoản có tồn tại và đang hoạt động hay không.

#### Request
```
POST /check
Content-Type: application/json
```

**Body JSON:**
```json
{
  "id": "id0c0nUPf3rjZwzpA3yD"
}
```

**Trường bắt buộc:**
- `id`: ID của tài khoản cần kiểm tra (phải là chuỗi)

#### Ví dụ Request

**cURL:**
```bash
curl -X POST http://localhost:5000/check \
  -H "Content-Type: application/json" \
  -d '{
    "id": "id0c0nUPf3rjZwzpA3yD"
  }'
```

**JavaScript/Fetch:**
```javascript
fetch('http://localhost:5000/check', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    id: "id0c0nUPf3rjZwzpA3yD"
  })
})
.then(response => response.json())
.then(data => {
  console.log('Kết quả:', data);
  if (data.success) {
    console.log('Tài khoản đang hoạt động');
  } else {
    console.log('Tài khoản không tồn tại hoặc bị khóa');
  }
});
```

**Python requests:**
```python
import requests

url = "http://localhost:5000/check"
data = {
    "id": "id0c0nUPf3rjZwzpA3yD"
}

response = requests.post(url, json=data)
result = response.json()
print(result)

if result['success']:
    print('Tài khoản đang hoạt động')
else:
    print('Tài khoản không tồn tại hoặc bị khóa')
```

#### Response

**Thành công - Tài khoản đang hoạt động (200):**
```json
{
  "success": true,
  "message": "Thành công",
  "data": {
    "id": "id0c0nUPf3rjZwzpA3yD",
    "active": true,
    "count": 0,
    "limit": 1,
    "message": "ID tồn tại và tài khoản đang hoạt động"
  }
}
```

**Thất bại - ID không tồn tại (400):**
```json
{
  "success": false,
  "message": "Chưa mua thành công",
  "data": {
    "error_code": "ID_NOT_FOUND",
    "id": "invalid_id",
    "message": "ID không tồn tại trong hệ thống"
  }
}
```

**Thất bại - Tài khoản bị khóa (400):**
```json
{
  "success": false,
  "message": "Tài khoản bị khóa",
  "data": {
    "error_code": "ACCOUNT_LOCKED",
    "id": "id0c0nUPf3rjZwzpA3yD",
    "active": false,
    "message": "Tài khoản bị khóa (active = false)"
  }
}
```

**Lỗi - Thiếu trường (400):**
```json
{
  "success": false,
  "message": "Thiếu trường 'id' trong JSON body"
}
```

**Lỗi - ID không phải chuỗi (400):**
```json
{
  "success": false,
  "message": "Trường 'id' phải là chuỗi, nhận được: number"
}
```

**Lỗi Server (500):**
```json
{
  "success": false,
  "message": "Mô tả lỗi",
  "data": null
}
```

#### Các Trường Hợp Sử Dụng

1. **Kiểm tra trước khi cho phép người dùng sử dụng dịch vụ:**
```javascript
// Kiểm tra tài khoản có tồn tại và đang hoạt động không
async function checkAccount(id) {
  const response = await fetch('http://localhost:5000/check', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id })
  });
  
  const result = await response.json();
  
  if (result.success && result.data.active) {
    // Tài khoản hợp lệ, cho phép sử dụng
    return true;
  } else {
    // Tài khoản không tồn tại hoặc bị khóa
    alert(result.message);
    return false;
  }
}

// Sử dụng
checkAccount('id0c0nUPf3rjZwzpA3yD').then(isValid => {
  if (isValid) {
    // Cho phép truy cập dịch vụ
  }
});
```

2. **Kiểm tra định kỳ trạng thái tài khoản:**
```python
import requests
import time

def monitor_account(id, interval=60):
    """Kiểm tra trạng thái tài khoản mỗi interval giây"""
    while True:
        response = requests.post(
            'http://localhost:5000/check',
            json={'id': id}
        )
        result = response.json()
        
        if result['success']:
            print(f"✅ Tài khoản {id} đang hoạt động")
            print(f"   Count: {result['data']['count']}/{result['data']['limit']}")
        else:
            print(f"❌ {result['message']}")
        
        time.sleep(interval)

# Chạy monitor
monitor_account('id0c0nUPf3rjZwzpA3yD', interval=30)
```

---

## 🔒 CORS (Cross-Origin Resource Sharing)

Tất cả các endpoints đều hỗ trợ CORS với:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type, Authorization`

Bạn có thể gọi API từ bất kỳ domain nào mà không gặp vấn đề CORS.

---

## 📊 Cấu Trúc Response Chung

Tất cả các response JSON đều tuân theo format:

```json
{
  "success": true/false,
  "message": "Mô tả kết quả",
  "data": {} hoặc null
}
```

### Mã Trạng Thái HTTP

- **200**: Thành công
- **400**: Request không hợp lệ (thiếu trường, sai định dạng, tài khoản bị khoá/hết lượt)
- **500**: Lỗi server (lỗi xử lý, không tìm thấy tài khoản, lỗi đọc file)

---

## 🐛 Xử Lý Lỗi

### Lỗi Thường Gặp

1. **Thiếu trường bắt buộc**
   - Kiểm tra JSON body có đầy đủ các trường bắt buộc
   - Ví dụ: `/authentication` cần `content` và `transferAmount`

2. **Sai định dạng dữ liệu**
   - `id` phải là chuỗi (string)
   - `sl` phải là số nguyên (integer)
   - `transferAmount` phải là số

3. **Tài khoản bị khoá**
   - Kiểm tra trường `active` trong `db/data.json`
   - Set `active: true` để kích hoạt lại

4. **Tài khoản hết lượt**
   - Kiểm tra `count` và `limit` trong `db/data.json`
   - Tài khoản sẽ tự động bị xóa khi `count > limit`

5. **Không tìm thấy tài khoản**
   - Kiểm tra `id` có tồn tại trong `db/data.json`
   - Đảm bảo `id` chính xác và không có khoảng trắng thừa

6. **Ngrok không chạy**
   - Đảm bảo ngrok đang chạy trong terminal riêng
   - Kiểm tra ngrok có quyền admin không
   - Kiểm tra port 5000 có đúng không (server mặc định chạy trên port 5000)

---

## 📁 Cấu Trúc File

```
SV_payment/
├── main.py                 # Entry point của API
├── apis/
│   ├── qr_code.py         # Module xử lý QR code
│   ├── authencation.py    # Module xử lý thanh toán
│   ├── add_count.py       # Module tăng count
│   └── check.py           # Module kiểm tra trạng thái tài khoản
├── db/
│   └── data.json          # Database lưu thông tin tài khoản
├── config/
│   ├── pay_ment.json      # Config giá tiền
│   └── mytoken.txt        # Token config (nếu cần)
├── page/
│   ├── admin.html         # Trang đăng nhập admin
│   └── dashboad.html      # Trang dashboard quản lý
├── api.txt                # File lưu URL API (ngrok URL)
└── HUONG_DAN_API.md       # File hướng dẫn này
```

---

## 💡 Ví Dụ Sử Dụng Đầy Đủ

### Scenario: Tạo QR code và xử lý thanh toán

1. **Tạo QR code và lấy ID:**

**Cách 1: Lấy ID từ header (khi trả về image):**
```bash
# Tạo QR code và lấy ID từ header
curl -I http://localhost:5000/qr?sl=50
# Hoặc với Python:
python -c "import requests; r = requests.get('http://localhost:5000/qr?sl=50'); print('QR ID:', r.headers.get('X-QR-ID'))"
```

**Cách 2: Lấy ID từ JSON response:**
```bash
curl http://localhost:5000/qr?sl=50&format=json
# Response:
# {
#   "success": true,
#   "id": "id0c0nUPf3rjZwzpA3yD",
#   "qr_code": "data:image/png;base64,...",
#   "sl": 50
# }
```

**JavaScript example:**
```javascript
// Lấy QR code và ID
fetch('http://localhost:5000/qr?sl=50&format=json')
  .then(response => response.json())
  .then(data => {
    const qrId = data.id;
    console.log('QR ID:', qrId);
    
    // Hiển thị QR code
    const img = document.createElement('img');
    img.src = data.qr_code;
    document.body.appendChild(img);
    
    // Lưu ID để sử dụng sau
    localStorage.setItem('currentQRId', qrId);
  });
```

→ Lưu ảnh QR code và ID, hiển thị cho người dùng

2. **Người dùng quét QR và thanh toán**
→ SePay sẽ gửi callback đến `/authentication` với `content` chứa `id` và `sl`

3. **Kiểm tra trạng thái tài khoản sau khi thanh toán:**
```bash
curl -X POST http://localhost:5000/check \
  -H "Content-Type: application/json" \
  -d '{"id": "id0c0nUPf3rjZwzpA3yD"}'
```

4. **Chuẩn bị tăng count (tạo pending request):**
```bash
curl -X POST http://localhost:5000/add_count \
  -H "Content-Type: application/json" \
  -d '{"id": "id0c0nUPf3rjZwzpA3yD"}'
```

5. **Verify và thực hiện tăng count:**
```bash
# Lấy request_id từ response của bước 4
curl -X POST http://localhost:5000/verify_count \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "123e4567-e89b-12d3-a456-426614174000",
    "approved": true
  }'
```

**JavaScript example - Luồng hoàn chỉnh:**
```javascript
// 1. Tạo QR code
fetch('http://localhost:5000/qr?sl=50&format=json')
  .then(response => response.json())
  .then(data => {
    const qrId = data.id;
    console.log('QR ID:', qrId);
    
    // Hiển thị QR code
    const img = document.createElement('img');
    img.src = data.qr_code;
    document.body.appendChild(img);
    
    // 2. Kiểm tra định kỳ trạng thái tài khoản
    const checkInterval = setInterval(() => {
      fetch('http://localhost:5000/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: qrId })
      })
      .then(response => response.json())
      .then(result => {
        if (result.success && result.data.active) {
          console.log('✅ Tài khoản đã được kích hoạt!');
          clearInterval(checkInterval);

          // 3. Chuẩn bị tăng count (tạo pending request)
          fetch('http://localhost:5000/add_count', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: qrId })
          })
          .then(response => response.json())
          .then(addResult => {
            if (addResult.success) {
              const requestId = addResult.data.request_id;
              console.log('📋 Đã tạo request tăng count:', requestId);

              // 4. Verify và thực hiện tăng count
              fetch('http://localhost:5000/verify_count', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  request_id: requestId,
                  approved: true
                })
              })
              .then(response => response.json())
              .then(verifyResult => {
                if (verifyResult.success) {
                  console.log('✅ Đã tăng count thành công!');
                  console.log('📊 Count hiện tại:', verifyResult.data.count);
                } else {
                  console.error('❌ Lỗi khi verify:', verifyResult.message);
                }
              });
            } else {
              console.error('❌ Lỗi khi tạo request add_count:', addResult.message);
            }
          });
        } else {
          console.log('⏳ Đang chờ thanh toán...');
        }
      });
    }, 5000); // Kiểm tra mỗi 5 giây
  });
```

---

## 📝 Ghi Chú Quan Trọng

1. **Content Format trong `/authentication`:**
   - Trường `content` phải có format: `{id_20_ky_tu}{sl}`
   - 20 ký tự đầu là `id`, phần còn lại là `sl` (số lượng)
   - Ví dụ: `"id0c0nUPf3rjZwzpA3yD50"` → id: `"id0c0nUPf3rjZwzpA3yD"`, sl: `50`

2. **File `db/data.json` format:**
```json
[
  {
    "id": "id0c0nUPf3rjZwzpA3yD",
    "count": 0,
    "limit": 1,
    "active": true
  }
]
```

3. **File `config/pay_ment.json` format:**
```json
{
  "BNK": "Mbbank",
  "STK": "0966549624",
  "UN": "HOANG NGOC HIEP",
  "COST": "2000",
  "LIMIT": 100
}
```

4. **Server tự động reload:** Server chạy ở chế độ debug, tự động reload khi code thay đổi.

5. **Ngrok URL:** Sau khi chạy ngrok, URL công khai sẽ được hiển thị. Sao chép URL này và cập nhật vào file `api.txt` nếu cần sử dụng trong ứng dụng.

---

## 🔗 Liên Hệ & Hỗ Trợ

Nếu gặp vấn đề hoặc cần hỗ trợ, vui lòng kiểm tra:
- Console logs khi chạy server
- Console logs khi chạy ngrok
- File `db/data.json` để kiểm tra dữ liệu
- File `config/pay_ment.json` để kiểm tra config
- File `api.txt` để kiểm tra URL API

---

**Chúc bạn sử dụng API thành công! 🎉**
