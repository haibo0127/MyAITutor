// 登录表单提交逻辑
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const messageEl = document.getElementById('message');
    messageEl.textContent = "";
    messageEl.className = "message";

    try {
        // 调用登录API
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/auth/token`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "登录失败");
        }

        // 登录成功，保存token和用户信息
        setToken(result.access_token);
        setUserInfo(result.user_info);

        // 跳转到控制台
        window.location.href = "dashboard.html";

    } catch (error) {
        // 登录失败
        messageEl.className = "message error";
        messageEl.textContent = `错误：${error.message}`;
    }
});