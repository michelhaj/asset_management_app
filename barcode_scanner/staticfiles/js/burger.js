const burger = document.querySelector("#burger");
const menu = document.querySelector("#menu");

const home = document.querySelector("#home");
const index = document.querySelector("#index");
const complist = document.querySelector("#complist");

const homea = document.querySelector("#homea");
const indexa = document.querySelector("#indexa");
const complista = document.querySelector("#complista");


burger.addEventListener("click", () => {
  if (menu.classList.contains("hidden")) {
    menu.classList.remove("hidden");
  } else {
    menu.classList.add("hidden");
  }
});

home.addEventListener("click", () => {
    if (homea.classList.contains("border-orange-500")) {
      homea.classList.remove("border-orange-500");
      
    } else {
       
        
    }
  });

  // index.addEventListener("click", () => {
  //   if (indexa.classList.contains("border-white")) {
  //       indexa.classList.add("border-orange-500");
        
        
  //   } else {
  //       indexa.classList.remove("border-orange-500");
        
  //   }
  // });

  // complist.addEventListener("click", () => {
  //   if (complista.classList.contains("border-white")) {
  //     complista.classList.add("border-orange-500");
      
  //   } else {
  //       complista.classList.remove("border-orange-500");
        
  //   }
  // });
  

