const burger = document.querySelector("#burger");
const menu = document.querySelector("#menu");

const home = document.querySelector("#home");
const index = document.querySelector("#index");
const complist = document.querySelector("#complist");




burger.addEventListener("click", () => {
  if (menu.classList.contains("hidden")) {
    menu.classList.remove("hidden");
  } else {
    menu.classList.add("hidden");
  }
});


       
  