jquery = window.jquery;
console.log(window);
const {$, jQuery} = jquery;
marked = window.marked;

window.$ = $;
window.jQuery = jQuery;

// Convert all .markdown-content to markdown
$(document).ready(() => {
	$(".markdown-content").each(() => {
		var content = $(this).text();
		var markedContent = marked.marked(content);
		console.log(markedContent);
	});
});