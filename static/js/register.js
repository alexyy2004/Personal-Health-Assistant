// your_project/static/js/register.js

document.getElementById('registerForm').addEventListener('submit', async function(e) {
    e.preventDefault(); // 防止表单默认提交

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    const errorMessage = document.getElementById('errorMessage');

    // 清除之前的错误消息
    errorMessage.textContent = '';

    if (username === '' || password === '') {
        errorMessage.textContent = 'Enter your username and password.';
        return;
    }

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            // 注册成功，重定向到主页或仪表盘
            window.location.href = '/';
        } else {
            // 显示错误消息
            errorMessage.textContent = data.error || 'Register failed, please try again';
        }
    } catch (error) {
        console.error('Error:', error);
        errorMessage.textContent = 'Server error, please try later.';
    }
});
