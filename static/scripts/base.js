/* When the user scrolls down, hide the navbar. When the user scrolls up, show the navbar */
var prevScrollpos = window.pageYOffset;
window.onscroll = function() {
  var currentScrollPos = window.pageYOffset;
  if (prevScrollpos > currentScrollPos) {
    document.getElementById("navbar").style.top = "0";
    document.getElementById("navbar").style.backgroundColor = "#06a783";
  } else {
    document.getElementById("navbar").style.top = "-70px";
    document.getElementById("navbar").style.backgroundColor = "#06a783";
  }
  prevScrollpos = currentScrollPos;
}

window.onload = () => {
	console.log(
		"\n\n\n\n\nWow, a hacker. I'm so proud of you...\n\n\n\n\n"
	);
}
