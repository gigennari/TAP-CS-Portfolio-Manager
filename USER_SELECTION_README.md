# 👤 User Selection Feature

## Overview
The user selection feature allows you to choose which user's portfolio to view and trade for. This is essential for multi-user portfolio management systems where different users have separate accounts and portfolios.

## 🚀 Features Implemented

### ✅ **Backend API**
- **`/users` endpoint**: Returns all users from the `users` table in bygDB
- **User validation**: Trade endpoints now require `user_id` parameter
- **Database integration**: Connects to MySQL bygDB database

### ✅ **Frontend Integration**
- **Portfolio Dashboard**: User dropdown in top-right corner
- **Homebroker**: User selection in header
- **Real-time updates**: Portfolio data updates when user is selected
- **Visual feedback**: User avatars with initials

### ✅ **User Experience**
- **Dropdown interface**: Clean, professional user selection
- **User information**: Shows name, email, and user ID
- **Persistent selection**: Selected user remains active during session
- **Validation**: Prevents trading without user selection

## 📁 Files Modified

### Backend Files:
1. **`server/routes.py`**
   - Added `/users` endpoint
   - Updated `/trade` endpoint to require `user_id`
   - Updated `/balance` endpoint to use `user_id`

2. **`server/app.py`**
   - Added route for test page

### Frontend Files:
1. **`client/portfoliotable.html`**
   - Added header with user selection dropdown
   - Added user management JavaScript functions
   - Integrated user selection with portfolio loading

2. **`client/homebroker.html`**
   - Added user selection to header
   - Updated trade execution to include `user_id`
   - Added user validation before trading

3. **`client/test_users.html`** (New)
   - Test page for user selection functionality

## 🔧 API Endpoints

### GET `/users`
Returns all users from the database.

**Response:**
```json
{
  "users": [
    {
      "user_id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe"
    }
  ]
}
```

### GET `/balance?user_id=1`
Returns the balance for a specific user.

**Response:**
```json
{
  "balance": 10000.00
}
```

### POST `/trade`
Executes a trade for a specific user.

**Request Body:**
```json
{
  "user_id": 1,
  "symbol": "AAPL",
  "action": "buy",
  "quantity": 10,
  "orderType": "market"
}
```

## 🎯 How to Use

### 1. **Portfolio Dashboard**
1. Open `http://localhost:5000/portfoliotable`
2. Click the user icon in the top-right corner
3. Select a user from the dropdown
4. Portfolio data will update for the selected user

### 2. **Homebroker Trading**
1. Open `http://localhost:5000/homebroker`
2. Select a user from the dropdown in the header
3. Search and select a stock
4. Place trades (user_id will be included automatically)

### 3. **Testing**
1. Open `http://localhost:5000/test-users`
2. Click "Test Users API" to verify database connection
3. Select users to test the selection functionality

## 🔍 User Interface Components

### User Dropdown Structure:
```html
<!-- User Selection Button -->
<button id="userDropdownBtn">
  <div class="user-avatar">👤</div>
  <span id="selectedUserName">Select User</span>
  <span id="selectedUserEmail">No user selected</span>
</button>

<!-- Dropdown Menu -->
<div id="userDropdownMenu">
  <div id="usersList">
    <!-- Users populated dynamically -->
  </div>
</div>
```

### JavaScript Functions:
- `loadUsers()` - Fetches users from API
- `populateUsersDropdown(users)` - Displays users in dropdown
- `selectUser(userId, ...)` - Handles user selection
- `loadUserPortfolio(userId)` - Loads user-specific data

## 🛠️ Database Requirements

### Users Table Structure:
```sql
CREATE TABLE users (
  user_id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  first_name VARCHAR(50),
  last_name VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Accounts Table Structure:
```sql
CREATE TABLE accounts (
  account_id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  balance DECIMAL(15,2) DEFAULT 0.00,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## 🔒 Security Considerations

### Current Implementation:
- **Client-side user selection**: User ID is stored in frontend JavaScript
- **No authentication**: Any user can be selected without login
- **Direct database access**: Backend directly queries user table

### Production Recommendations:
- **Add authentication**: Implement login system
- **Session management**: Store user context server-side
- **Authorization**: Verify user permissions for portfolio access
- **Input validation**: Sanitize all user inputs

## 🎨 Styling & Design

### User Avatar:
- **Gradient background**: Indigo to purple gradient
- **Initial display**: Shows first letter of name/username
- **Responsive sizing**: Adapts to different screen sizes

### Dropdown Menu:
- **Clean design**: White background with subtle shadows
- **Hover effects**: Smooth transitions on user items
- **Loading states**: Spinner during API calls
- **Error handling**: User-friendly error messages

## 📊 Data Flow

```
1. Page Load → loadUsers() → GET /users → Populate Dropdown
2. User Selection → selectUser() → Update UI → Store user_id
3. Portfolio Load → loadUserPortfolio() → GET /balance?user_id=X
4. Trade Execution → handleTradeSubmit() → POST /trade (with user_id)
```

## 🐛 Troubleshooting

### Common Issues:

#### "No users found"
- **Check database**: Ensure users table has data
- **Check connection**: Verify MySQL connection in `db.py`
- **Check API**: Test `/users` endpoint directly

#### "Failed to load users"
- **CORS issues**: Ensure Flask CORS is configured
- **Network errors**: Check if Flask server is running
- **Database errors**: Check MySQL server status

#### "Please select a user before trading"
- **User not selected**: Click user dropdown and select a user
- **JavaScript errors**: Check browser console for errors

### Debug Steps:
1. **Test API directly**: Visit `http://localhost:5000/users`
2. **Check browser console**: Look for JavaScript errors
3. **Verify database**: Check if users table exists and has data
4. **Test with test page**: Use `/test-users` to isolate issues

## 🚀 Future Enhancements

### Planned Features:
- **User authentication**: Login/logout functionality
- **User profiles**: Extended user information and preferences
- **Role-based access**: Admin vs regular user permissions
- **User creation**: Add new users through the interface
- **User search**: Search/filter users in large lists

### Advanced Features:
- **Multi-account support**: Users with multiple trading accounts
- **User groups**: Organize users by teams or departments
- **Audit logging**: Track which user performed which actions
- **User preferences**: Customizable dashboard settings per user

## 📞 Support

### Testing the Feature:
1. **Start the server**: `python server/app.py`
2. **Open test page**: `http://localhost:5000/test-users`
3. **Test API**: Click "Test Users API" button
4. **Select users**: Click on user items to test selection
5. **Check console**: Verify user data in browser console

### Verification Checklist:
- [ ] Users API returns data
- [ ] User dropdown populates correctly
- [ ] User selection updates UI
- [ ] Portfolio data loads for selected user
- [ ] Trading includes user_id in requests
- [ ] Balance API works with user_id parameter

The user selection feature is now fully integrated and ready for use!