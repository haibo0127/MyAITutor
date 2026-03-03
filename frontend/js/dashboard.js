// 页面加载时验证登录状态
document.addEventListener('DOMContentLoaded', async () => {
    const userInfo = getUserInfo();
    const userInfoEl = document.getElementById('userInfo');

    if (!userInfo) {
        window.location.href = "index.html";
        return;
    }

    // 显示用户信息
    userInfoEl.textContent = `欢迎，${userInfo.full_name}（${userInfo.grade}）`;

    // 退出登录按钮
    document.getElementById('logoutBtn').addEventListener('click', () => {
        clearToken();
        window.location.href = "index.html";
    });

    // 加载用户记忆（薄弱点）
    loadUserMemory();

    // 图片选择逻辑
    const fileInput = document.getElementById('fileInput');
    const selectFileBtn = document.getElementById('selectFileBtn');
    const fileNameEl = document.getElementById('fileName');
    const uploadBtn = document.getElementById('uploadBtn');
    let selectedFile = null;

    selectFileBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            selectedFile = e.target.files[0];
            fileNameEl.textContent = selectedFile.name;
            uploadBtn.disabled = false;
        } else {
            selectedFile = null;
            fileNameEl.textContent = "";
            uploadBtn.disabled = true;
        }
    });

    // 图片上传逻辑
    uploadBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        const uploadMessage = document.getElementById('uploadMessage');
        uploadMessage.textContent = "上传中...";
        uploadMessage.className = "message";

        try {
            // 1. 上传图片
            const formData = new FormData();
            formData.append('file', selectedFile);

            const uploadResponse = await authRequest(`${API_BASE_URL}/study/upload/image`, {
                method: 'POST',
                headers: {
                    // 移除Content-Type，让浏览器自动设置
                    'Authorization': `Bearer ${getToken()}`
                },
                body: formData
            });

            const uploadResult = await uploadResponse.json();

            if (!uploadResponse.ok) {
                throw new Error(uploadResult.detail || "上传失败");
            }

            uploadMessage.textContent = "上传成功，分析中...";

            // 2. 分析图片内容
            const analyzeResponse = await authRequest(`${API_BASE_URL}/study/analyze/${uploadResult.file_id}`, {
                method: 'POST'
            });

            const analyzeResult = await analyzeResponse.json();

            if (!analyzeResponse.ok) {
                throw new Error(analyzeResult.detail || "分析失败");
            }

            // 显示分析结果
            const analysisResultEl = document.getElementById('analysisResult');
            analysisResultEl.innerHTML = `
                <strong>识别文本：</strong>${analyzeResult.analysis.ocr_text || "无"}\n
                <strong>知识点：</strong>${analyzeResult.analysis.knowledge_points?.join(", ") || "无"}\n
                <strong>薄弱点：</strong>${analyzeResult.analysis.weak_points?.join(", ") || "无"}\n
                <strong>错题数：</strong>${analyzeResult.analysis.error_count || 0}\n
                <strong>学习建议：</strong>${analyzeResult.analysis.suggestion || "无"}
            `;

            uploadMessage.className = "message success";
            uploadMessage.textContent = "上传并分析成功！";

            // 重新加载薄弱点
            loadUserMemory();

        } catch (error) {
            uploadMessage.className = "message error";
            uploadMessage.textContent = `错误：${error.message}`;
        }
    });
});

// 加载用户记忆（薄弱点）
async function loadUserMemory() {
    const memoryResultEl = document.getElementById('memoryResult');

    try {
        const response = await authRequest(`${API_BASE_URL}/study/memory`, {
            method: 'GET'
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "获取记忆失败");
        }

        if (result.memories.length === 0) {
            memoryResultEl.textContent = "暂无薄弱点记录，请先上传图片分析";
            return;
        }

        // 格式化显示记忆
        let memoryHtml = "";
        result.memories.forEach(mem => {
            memoryHtml += `
                <div class="memory-item">
                    <strong>${mem.memory_key.replace("weak_points_", "")}薄弱点：</strong>
                    ${Array.isArray(mem.memory_value) ? mem.memory_value.join(", ") : mem.memory_value}
                    <br>
                    <small>更新时间：${mem.updated_at} | 置信度：${(mem.confidence * 100).toFixed(0)}%</small>
                </div>
                <hr>
            `;
        });

        memoryResultEl.innerHTML = memoryHtml;

    } catch (error) {
        memoryResultEl.textContent = `加载失败：${error.message}`;
    }
}