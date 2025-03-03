Telegram 的 HTML 格式化消息支持以下标签：

### **✅ 文字格式**
- `<b>...</b>` - **加粗**
- `<strong>...</strong>` - **加粗**（等效于 `<b>`）
- `<i>...</i>` - *斜体*
- `<em>...</em>` - *斜体*（等效于 `<i>`）
- `<u>...</u>` - ***下划线***
- `<ins>...</ins>` - ***下划线***（等效于 `<u>`）
- `<s>...</s>` - ~~删除线~~
- `<strike>...</strike>` - ~~删除线~~（等效于 `<s>`）
- `<del>...</del>` - ~~删除线~~（等效于 `<s>`）
- `<code>...</code>` - `行内代码`
- `<pre>...</pre>` - 代码块（默认不指定语言）
- `<pre><code class="language">...</code></pre>` - **带语法高亮的代码块**（`language` 为可选的编程语言）

### **✅ 链接**
- `<a href="URL">文本</a>` - 超链接（支持 HTTP/HTTPS）

### **✅ 提及和引用**
- `<tg-emoji emoji-id="ID">😊</tg-emoji>` - Telegram **自定义表情**（仅限 bot 和某些支持的客户端）
- `<span class="tg-spoiler">...</span>` - **隐藏文本（点击后显示）**
- `<tg-mention user-id="123456789">用户名</tg-mention>` - **直接 @ 特定用户**（适用于 Bot API）

### **❌ 不支持的 HTML 标签**
❌ `<h1>` ~ `<h6>`（标题）  
❌ `<p>`（段落）  
❌ `<img>`（图片）  
❌ `<table>`（表格）  
❌ `<div>`、`<span>`（除 `tg-spoiler` 以外）

### **🎯 示例**
```html
<b>加粗文本</b>
<i>斜体文本</i>
<u>下划线</u>
<s>删除线</s>
<code>行内代码</code>
<pre>代码块</pre>
<pre><code class="python">print("Hello, Telegram!")</code></pre>
<a href="https://example.com">点击这里</a>
<tg-mention user-id="123456789">点击@用户</tg-mention>
<span class="tg-spoiler">这是隐藏文本</span>
```

这就是 Telegram **HTML 消息** 支持的所有标签！🚀