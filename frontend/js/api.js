// API基础配置
const API_BASE_URL = "http://127.0.0.1:8001";

// 获取本地存储的token
function getToken() {
    return localStorage.getItem("access_token");
}

// 设置本地存储的token
function setToken(token) {
    localStorage.setItem("access_token", token);
}

// 清除本地存储的token
function clearToken() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_info");
}

// 获取用户信息
function getUserInfo() {
    const userInfo = localStorage.getItem("user_info");
    return userInfo ? JSON.parse(userInfo) : null;
}

// 设置用户信息
function setUserInfo(userInfo) {
    localStorage.setItem("user_info", JSON.stringify(userInfo));
}

// 带认证的API请求
async function authRequest(url, options = {}) {
    const token = getToken();
    if (!token) {
        // 无token，跳转到登录页
        window.location.href = "index.html";
        throw new Error("未登录");
    }

    // 设置请求头
    options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };

    const response = await fetch(url, options);

    // 处理401未授权
    if (response.status === 401) {
        clearToken();
        window.location.href = "index.html";
        throw new Error("登录已过期，请重新登录");
    }

    return response;
}