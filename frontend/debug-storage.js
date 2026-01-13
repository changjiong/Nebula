/**
 * 对话持久化调试脚本
 * 
 * 使用方法：
 * 1. 打开浏览器访问 http://localhost:5173
 * 2. 按 F12 打开控制台
 * 3. 复制此文件内容到控制台执行
 */

console.log('🔍 对话持久化调试工具');

// 检查 localStorage
function checkStorage() {
    console.log('\n📦 检查 localStorage:');
    const chatStorage = localStorage.getItem('chat-storage');

    if (!chatStorage) {
        console.warn('❌ 没有找到 chat-storage 数据');
        return null;
    }

    try {
        const data = JSON.parse(chatStorage);
        console.log('✅ 找到存储数据:', data);

        const state = data.state;
        console.log('\n📊 存储内容分析:');
        console.log(`- 对话数量: ${state.conversations?.length || 0}`);
        console.log(`- 当前对话ID: ${state.currentConversationId || '无'}`);

        if (state.conversations && state.conversations.length > 0) {
            console.log('\n📋 对话详情:');
            state.conversations.forEach((conv, idx) => {
                console.log(`\n  对话 ${idx + 1}:`);
                console.log(`  - ID: ${conv.id}`);
                console.log(`  - 标题: ${conv.title}`);
                console.log(`  - 消息数: ${conv.messages?.length || 0}`);
                console.log(`  - 创建时间: ${conv.createdAt}`);
                console.log(`  - 更新时间: ${conv.updatedAt}`);

                if (conv.messages && conv.messages.length > 0) {
                    console.log(`  - 消息列表:`);
                    conv.messages.forEach((msg, midx) => {
                        console.log(`    ${midx + 1}. [${msg.role}]: ${msg.content.substring(0, 50)}...`);
                    });
                }
            });
        }

        return state;
    } catch (e) {
        console.error('❌ 解析存储数据失败:', e);
        return null;
    }
}

// 检查 Zustand store 状态
function checkStoreState() {
    console.log('\n🔄 检查当前 Zustand Store 状态:');

    // 尝试访问 store (需要在 React 上下文中)
    try {
        const store = window.__ZUSTAND_STORES__?.chatStore;
        if (store) {
            const state = store.getState();
            console.log('✅ Store 状态:', state);
            console.log(`- 当前消息数: ${state.messages?.length || 0}`);
            console.log(`- 对话数: ${state.conversations?.length || 0}`);
            console.log(`- 当前对话ID: ${state.currentConversationId || '无'}`);
        } else {
            console.warn('⚠️ 无法访问 Zustand store');
            console.log('💡 提示: 这是正常的,因为 Zustand 不暴露全局引用');
        }
    } catch (e) {
        console.log('ℹ️ Store 检查跳过 (需要在组件中)');
    }
}

// 手动触发保存测试
function testSave() {
    console.log('\n💾 测试手动保存:');

    const testData = {
        state: {
            conversations: [
                {
                    id: 'test-conv-' + Date.now(),
                    title: '测试对话',
                    messages: [
                        {
                            id: 'msg-1',
                            role: 'user',
                            content: '这是一条测试消息',
                            timestamp: Date.now()
                        }
                    ],
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString()
                }
            ],
            currentConversationId: 'test-conv-' + Date.now()
        },
        version: 0
    };

    localStorage.setItem('chat-storage', JSON.stringify(testData));
    console.log('✅ 测试数据已保存');
    console.log('🔄 请刷新页面查看是否能加载');
}

// 清除所有数据
function clearAll() {
    console.log('\n🗑️ 清除所有数据:');
    localStorage.removeItem('chat-storage');
    console.log('✅ 已清除 chat-storage');
    console.log('🔄 请刷新页面');
}

// 执行检查
console.log('\n='.repeat(50));
checkStorage();
checkStoreState();
console.log('\n='.repeat(50));

console.log('\n📌 可用命令:');
console.log('- checkStorage()   检查 localStorage');
console.log('- checkStoreState()  检查当前 store 状态');
console.log('- testSave()       保存测试数据');
console.log('- clearAll()       清除所有数据');
console.log('\n');
