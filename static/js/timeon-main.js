// Auto-expanding text area input element
const txr = document.getElementsByTagName('textarea');
for (let i = 0; i < txr.length; i++) {
  txr[i].setAttribute('style', 'height:' + (txr[i].scrollHeight+3) + 'px;overflow-y:hidden;resize:none');
  txr[i].addEventListener("input", OnInput, false);
}

function OnInput() {
  this.style.height = 'auto';
  this.style.height = (this.scrollHeight+3) + 'px';
}
